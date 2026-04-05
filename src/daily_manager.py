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

from src.google_api_services import get_calendar_events, get_tasks
from src.gemini_helper import generate_daily_update

def get_daily_note_path() -> str:
    """Obsidian CLI を使用して現在のデイリーノートの絶対パスを取得します。"""
    try:
        # obsidian vault info=path コマンドを実行し、Vaultのパスを取得
        vault_result = subprocess.run(
            ["obsidian", "vault", "info=path"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        vault_path = vault_result.stdout.strip()

        # obsidian daily:path コマンドを実行し、デイリーノートのパスを取得
        daily_result = subprocess.run(
            ["obsidian", "daily:path"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        daily_path = daily_result.stdout.strip()
        
        if not os.path.isabs(daily_path):
            daily_path = os.path.join(vault_path, daily_path)
            
        return daily_path
    except subprocess.CalledProcessError as e:
        print(f"Obsidian CLI の実行に失敗しました: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print("obsidian コマンドが見つかりません。CLIツールがインストールされ、パスが通っているか確認してください。", file=sys.stderr)
        raise

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
            
        print("Google Calendar と Tasks からデータを取得中...")
        events = get_calendar_events()
        tasks = get_tasks()
        
        vault_root = find_vault_root(daily_path)
        prompt_template_path = os.path.join(vault_root, "_config", "templates", "prompts", "daily_edit_prompt.md")
        if not os.path.exists(prompt_template_path):
            prompt_template_path = None
            
        print("Gemini API でノートの更新内容を生成中...")
        updated_note = generate_daily_update(period, current_note, events, tasks, prompt_template_path)
        
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
    process_daily_note("morning")

def process_evening():
    """夕方の処理：一日の振り返りや未完了タスクの整理を行う"""
    process_daily_note("evening")

def process_night():
    """夜の処理：翌日に向けた最終整理とノートの確定を行う"""
    process_daily_note("night")

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
        choices=["morning", "evening", "night"],
        help="実行する時間帯 (morning: 朝のセットアップ, evening: 夕方の整理, night: 夜の確定)"
    )

    args = parser.parse_args()

    try:
        if args.period == "morning":
            process_morning()
        elif args.period == "evening":
            process_evening()
        elif args.period == "night":
            process_night()
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
