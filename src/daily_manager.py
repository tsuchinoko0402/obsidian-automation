#!/usr/bin/env uv run
"""
Obsidian Daily Manager
デイリーノートの自動生成・管理を行うためのメインスクリプトです。
Google Calendar や Google Tasks などの外部サービスと連携し、
雑多なメモや思いつき、タスクを整理し、デイリーノートを中心に概要を把握できるようにします。
"""

import argparse
import sys
import subprocess
import os

# プロジェクトルートをシステムのパスに追加し、'src' モジュールを解決できるようにする
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.google_api_services import get_calendar_events, get_tasks, get_completed_tasks, get_keep_notes
from src.gemini_helper import generate_daily_update
from src.inbox_organizer import organize_inbox
from src.notes_processor import process_unprocessed_notes
from src.obsidian_utils import get_vault_path, get_daily_note_path, OBSIDIAN_CMD

def find_vault_root(daily_path: str) -> str:
    """デイリーノートのパスからObsidian Vaultのルートディレクトリを探します。"""
    current_dir = os.path.dirname(daily_path)
    while current_dir != os.path.dirname(current_dir): # ルートディレクトリに到達するまで
        if os.path.exists(os.path.join(current_dir, ".obsidian")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return os.path.dirname(daily_path) # 見つからない場合は親ディレクトリを返す

def process_daily_note(period: str):
    """指定された期間(morning/evening/night)のデイリーノート処理を実行します"""
    print(f"{period} の処理を開始します...")
    try:
        daily_path = get_daily_note_path()
        print(f"対象デイリーノート: {daily_path}")

        if not os.path.exists(daily_path):
            print("デイリーノートが存在しません。Obsidian側で作成されているか確認してください。", file=sys.stderr)
            return

        with open(daily_path, "r", encoding="utf-8") as f:
            current_note = f.read()

        events = []
        tasks = []
        completed_tasks = []
        keep_notes = []

        print("データを取得中...")
        if period == "morning":
            events = get_calendar_events()
            tasks = get_tasks()
        elif period == "evening":
            keep_notes = get_keep_notes()
            tasks = get_tasks()
        elif period == "night":
            completed_tasks = get_completed_tasks()

        vault_root = find_vault_root(daily_path)
        prompt_template_path = os.path.join(vault_root, "_config", "templates", "prompts", "daily_edit_prompt.md")
        if not os.path.exists(prompt_template_path):
            prompt_template_path = None

        print("Gemini API でノートの更新内容を生成中...")
        updated_note = generate_daily_update(period, current_note, events, tasks, completed_tasks, keep_notes, prompt_template_path)

        with open(daily_path, "w", encoding="utf-8") as f:
            clean_note = updated_note.strip()
            # Markdownコードブロックでラップされている場合は除去
            if clean_note.startswith("```markdown"):
                clean_note = clean_note[11:]
            elif clean_note.startswith("```"):
                clean_note = clean_note[3:]
            if clean_note.endswith("```"):
                clean_note = clean_note[:-3]

            f.write(clean_note.strip() + "\n")

        print("-> 処理完了")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}", file=sys.stderr)
        raise

def process_morning():
    """朝の処理：一日のスケジュールやタスクをデイリーノートにセットアップする"""
    print("Obsidian でデイリーノートを生成・確認します...")
    try:
        # ノートが存在しない場合を考慮し、事前に obsidian daily を実行してノートを生成/開く
        subprocess.run([OBSIDIAN_CMD, "daily"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Obsidian CLI (daily) の実行に失敗しました: {e.stderr}", file=sys.stderr)

    process_daily_note("morning")

def process_evening():
    """夕方の処理：一日の振り返りや未完了タスクの整理を行う"""
    process_daily_note("evening")

def process_night():
    """夜の処理：翌日に向けた最終整理とノートの確定を行う"""
    process_daily_note("night")

    print("手動レビューのために Obsidian を開きます...")
    try:
        subprocess.run([OBSIDIAN_CMD, "daily"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Obsidian を開けませんでした: {e.stderr}", file=sys.stderr)

    # 同期スクリプトが存在する場合は実行
    # 実行場所がプロジェクトのルートを想定
    mirror_script = os.path.join(project_root, "mirror_obsidian.sh")
    if os.path.exists(mirror_script):
        print("Google Drive への同期スクリプト (mirror_obsidian.sh) を実行します...")
        try:
            subprocess.run(["bash", mirror_script], check=True)
            print("-> 同期完了")
        except subprocess.CalledProcessError as e:
            print(f"同期スクリプトの実行に失敗しました: {e.stderr}", file=sys.stderr)

def process_organize():
    """Inboxの整理：Geminiを使ってInboxのメモを適切なフォルダへ移動し、MOCへ追記する"""
    print("Inboxの自動整理 (organize) を開始します...")
    try:
        vault_root = get_vault_path()
        print(f"Vaultルート: {vault_root}")
        organize_inbox(vault_root)
        print("-> 整理完了")
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}", file=sys.stderr)
        raise

def process_notes():
    """Apple Notesの整理：Geminiを使って未処理のメモをObsidianに反映する"""
    process_unprocessed_notes()

def main():
    # .envファイルの読み込み
    try:
        from dotenv import load_dotenv
        # スクリプトの存在するディレクトリ（src）の親ディレクトリにある .env を探す
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        load_dotenv(dotenv_path=env_path)
    except ImportError:
        pass # dotenvがインストールされていない場合はスキップ

    parser = argparse.ArgumentParser(
        description="Obsidian のデイリーノートを管理・更新するツール"
    )
    parser.add_argument(
        "period",
        choices=["morning", "evening", "night", "organize", "notes"],
        help="実行する処理 (morning, evening, night, organize: Inbox整理, notes: Appleメモ整理)"
    )

    args = parser.parse_args()

    try:
        if args.period == "morning":
            process_morning()
        elif args.period == "evening":
            process_evening()
        elif args.period == "night":
            process_night()
        elif args.period == "organize":
            process_organize()
        elif args.period == "notes":
            process_notes()
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
