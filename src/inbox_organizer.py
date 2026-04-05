import os
import json
import shutil
from pydantic import BaseModel
from google import genai
from google.genai import types

class OrganizationResult(BaseModel):
    target_folder: str
    target_moc: str

def organize_inbox(vault_root: str):
    """
    Inbox (00_inbox) 内のマークダウンファイルを読み込み、Geminiに分類させて
    適切なフォルダへの移動とMOCへのリンク追記を行います。
    """
    inbox_dir = os.path.join(vault_root, "00_inbox")
    if not os.path.exists(inbox_dir):
        print(f"Inboxディレクトリが見つかりません: {inbox_dir}")
        return
        
    md_files = [os.path.join(inbox_dir, f) for f in os.listdir(inbox_dir) if f.endswith('.md')]
    if not md_files:
        print("Inboxは空です。整理するファイルがありません。")
        return
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 GEMINI_API_KEY が設定されていません。")
    client = genai.Client(api_key=api_key)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-pro-latest")
    
    system_prompt = """あなたはObsidianのノート整理アシスタントです。
提供されたメモの内容を読み、以下のフォルダ構成とMOC（目次）リストから、最も適切な移動先フォルダと追加すべきMOCを選んでください。

【フォルダ構成】
- 00_inbox : 該当しない場合、または判断できない場合
- 10_scout : ボーイスカウト関連（日連、県連、地区、団）
- 20_music : 演奏活動・NPO運営関連（ニューフィル大阪、KGWO）
- 30_tech : 技術研鑽・自己研鑽（テックブログ下書き、学習ログ）
- 40_private : 個人・家庭・私的プロジェクト
- 90_archieve : 過去の記録

【MOCリスト】
- MOC_scout
- MOC_music
- MOC_tech
- MOC_private
- None (MOCに追加しない場合)
"""

    print(f"Inbox内の {len(md_files)} 件のファイルを整理します...")

    for file_path in md_files:
        file_name = os.path.basename(file_path)
        print(f"\n処理中: {file_name}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        prompt = f"ファイル名: {file_name}\n\n内容:\n{content}"
        
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[system_prompt, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=OrganizationResult,
                ),
            )
            
            result = json.loads(response.text)
            target_folder = result.get("target_folder")
            target_moc = result.get("target_moc")
            
            print(f"  -> 判定結果: フォルダ=[{target_folder}], MOC=[{target_moc}]")
            
            if target_folder and target_folder != "00_inbox":
                # ファイルの移動
                dest_dir = os.path.join(vault_root, target_folder)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, file_name)
                
                if not os.path.exists(dest_path):
                    shutil.move(file_path, dest_path)
                    print(f"  -> フォルダ {target_folder} へ移動しました。")
                    
                    # MOCへの追記
                    if target_moc and target_moc != "None":
                        # Vault内からMOCファイルを探す
                        moc_files = []
                        for root, _, files in os.walk(vault_root):
                            # 不要なディレクトリの探索をスキップ
                            if ".obsidian" in root or ".git" in root:
                                continue
                            if f"{target_moc}.md" in files:
                                moc_files.append(os.path.join(root, f"{target_moc}.md"))
                        
                        if moc_files:
                            moc_file_path = moc_files[0]
                            note_title = os.path.splitext(file_name)[0]
                            with open(moc_file_path, "a", encoding="utf-8") as mf:
                                mf.write(f"\n- [[{note_title}]]\n")
                            print(f"  -> {target_moc}.md にリンクを追記しました。")
                        else:
                            print(f"  -> 警告: MOCファイル {target_moc}.md がVault内に見つかりません。")
                else:
                    print(f"  -> 警告: 移動先に同名ファイルが存在するためスキップしました。")
            else:
                print(f"  -> 00_inbox に残します。")
                
        except Exception as e:
            print(f"  -> 処理中にエラーが発生しました: {e}")
