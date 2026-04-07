import os
import json
import shutil
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Gemini and Google API
from google import genai
from google.genai import types

# Local Helpers
from src.apple_notes_helper import get_unprocessed_apple_notes, mark_apple_note_as_processed
from src.obsidian_utils import get_vault_path, get_daily_note_path

# --- Pydantic Models for Structured Gemini Output ---
class NoteAction(BaseModel):
    """AIが決定したノートの処理方法を定義するモデル"""
    action: Literal["summarize_to_daily", "create_new_note"] = Field(description="デイリーノートに要約するか、新規ノートを作成するかを決定します。")
    summary: Optional[str] = Field(default=None, description="デイリーノートに追記するための簡潔な一行要約。")
    new_note_title: Optional[str] = Field(default=None, description="新規作成するノートの適切なタイトル。")
    target_folder: Optional[str] = Field(default=None, description="新規ノートの保存先フォルダ (例: '30_tech')。")
    target_moc: Optional[str] = Field(default=None, description="新規ノートのリンクを追記すべきMOCファイル名 (例: 'MOC_tech')。")

# --- Main Workflow ---
def process_unprocessed_notes():
    """
    Apple Notesから未処理のメモを取得し、Geminiで分類・処理してObsidianに反映する。
    """
    print("--- 🍎 Apple Notesの未処理メモの整理を開始します ---")
    
    try:
        unprocessed_notes = get_unprocessed_apple_notes()
        if not unprocessed_notes:
            print("🎉 未処理のメモはありません！")
            return
            
        print(f"📝 {len(unprocessed_notes)} 件の未処理メモを処理します...")
        
        vault_root = get_vault_path()

        for note in unprocessed_notes:
            print(f"\n▶︎ 処理中: 「{note.name}」")
            
            # 1. Geminiに処理方法を問い合わせる
            try:
                action_plan = _get_action_for_note(note.plaintext)
                print(f"  -> AIの判断: {action_plan.action}")
            except Exception as e:
                print(f"  -> AIによる判断中にエラーが発生しました: {e}")
                continue # 次のノートへ

            # 2. AIの指示に従ってObsidianを更新
            success = False
            if action_plan.action == "summarize_to_daily" and action_plan.summary:
                success = _append_summary_to_daily(action_plan.summary)
                
            elif action_plan.action == "create_new_note" and all([action_plan.new_note_title, action_plan.target_folder, action_plan.target_moc]):
                success = _create_new_note_and_link(
                    title=action_plan.new_note_title,
                    content=note.plaintext,
                    folder=action_plan.target_folder,
                    moc=action_plan.target_moc,
                    vault_root=vault_root
                )
            
            # 3. 成功した場合のみApple Noteを「処理済み」にする
            if success:
                mark_apple_note_as_processed(note)

    except Exception as e:
        print(f"❌ Apple Notesの処理中に予期せぬエラーが発生しました: {e}")

# --- Private Helper Functions ---
def _get_action_for_note(note_content: str) -> NoteAction:
    """Geminiにメモ内容を渡し、実行すべきアクションをJSON形式で取得する。"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEYが設定されていません。")
    client = genai.Client(api_key=api_key)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-pro-latest")

    # プロジェクトのプロンプトファイルをチェック
    project_prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "prompts", "apple_notes_processor.md")
    
    system_prompt = ""
    if os.path.exists(project_prompt_path):
        with open(project_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    else:
        system_prompt = """あなたはObsidianのノート整理アシスタントです。
提供されたメモの内容を読み、最適なアクションを決定してください。

アクションは以下の2種類です:
1. `summarize_to_daily`: 内容が短く、一時的な情報（例：今日の買い物リスト、簡単なリマインダー）である場合。
2. `create_new_note`: 内容が永続的に価値のある知識、アイデア、特定のプロジェクトに関する情報である場合。

`create_new_note` を選択した場合は、以下のカテゴリに基づいてタイトル、保存先フォルダ、追加すべきMOCも提案してください。

【カテゴリ】
- folder: 10_scout, moc: MOC_scout (ボーイスカウト関連)
- folder: 20_music, moc: MOC_music (音楽・NPO運営関連)
- folder: 30_tech, moc: MOC_tech (技術・自己研鑽関連)
- folder: 40_private, moc: MOC_private (個人・家庭関連)
"""
    prompt = f"以下のメモを処理してください:\n\n{note_content}"
    
    response = client.models.generate_content(
        model=model_name,
        contents=[system_prompt, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NoteAction,
        ),
    )
    # Pydanticモデルに直接パースする
    return NoteAction(**json.loads(response.text))

def _append_summary_to_daily(summary: str) -> bool:
    """今日のデイリーノートに要約を追記する。"""
    try:
        daily_note_path = get_daily_note_path()
        if not os.path.exists(daily_note_path):
            print(f"  -> デイリーノートが見つかりません ({daily_note_path})。要約の追記をスキップします。")
            return False

        heading = "\n## 📝 Apple Notesからのメモ\n"
        content_to_append = f"- {summary}\n"

        with open(daily_note_path, "a", encoding="utf-8") as f:
            # 見出しが含まれているかチェックするために一度読み込む必要があるが、簡易的に追記
            # 実際には既存の内容チェックをした方が良いが、ここでは単純追記とする
            f.write(heading if heading not in open(daily_note_path).read() else "")
            f.write(content_to_append)
        
        print(f"  -> 今日のデイリーノートに要約を追記しました。")
        return True
    except Exception as e:
        print(f"  -> デイリーノートへの追記中にエラー: {e}")
        return False

def _create_new_note_and_link(title: str, content: str, folder: str, moc: str, vault_root: str) -> bool:
    """Obsidianに新しいノートを作成し、MOCとデイリーノートにリンクを貼る。"""
    try:
        # 1. 新規ノートの作成
        dest_dir = os.path.join(vault_root, folder)
        os.makedirs(dest_dir, exist_ok=True)
        # ファイル名として不適切な文字を置換
        safe_title = title.replace("/", "-").replace(":", "-")
        new_note_path = os.path.join(dest_dir, f"{safe_title}.md")

        if os.path.exists(new_note_path):
            print(f"  -> 警告: ノート '{safe_title}.md' は既に存在するため、作成をスキップします。")
            return False # 処理済みにはしない

        with open(new_note_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{content}")
        print(f"  -> 新規ノート '{safe_title}.md' を作成しました。")

        # 2. MOCへのリンク追記
        if moc and moc != "None":
            moc_files = []
            for root, _, files in os.walk(vault_root):
                if f"{moc}.md" in files:
                    moc_files.append(os.path.join(root, f"{moc}.md"))
            
            if moc_files:
                with open(moc_files[0], "a", encoding="utf-8") as mf:
                    mf.write(f"\n- [[{safe_title}]]\n")
                print(f"  -> {moc}.md にリンクを追記しました。")
            else:
                print(f"  -> 警告: MOCファイル {moc}.md が見つかりません。")

        # 3. デイリーノートへのリンク追記
        daily_note_path = get_daily_note_path()
        if os.path.exists(daily_note_path):
            heading = "\n## 📝 Apple Notesからのメモ\n"
            link_text = f"- 新規ノート『[[{safe_title}]]』を作成しました。\n"
            
            # 既存ファイルを開いて追記
            with open(daily_note_path, "a", encoding="utf-8") as f:
                if heading not in open(daily_note_path).read():
                    f.write(heading)
                f.write(link_text)
            print(f"  -> 今日のデイリーノートに新規ノートへのリンクを追記しました。")
        
        return True
    except Exception as e:
        print(f"  -> 新規ノート作成またはリンク処理中にエラー: {e}")
        return False
