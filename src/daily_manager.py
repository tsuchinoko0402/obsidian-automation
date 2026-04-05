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

def get_daily_note_path() -> str:
    """Obsidian CLI を使用して現在のデイリーノートのパスを取得します。"""
    try:
        # obsidian daily:path コマンドを実行し、標準出力を取得
        result = subprocess.run(
            ["obsidian", "daily:path"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        # 改行文字などを取り除いて返す
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Obsidian CLI (daily:path) の実行に失敗しました: {e.stderr}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print("obsidian コマンドが見つかりません。CLIツールがインストールされ、パスが通っているか確認してください。", file=sys.stderr)
        raise

def process_morning():
    """朝の処理：一日のスケジュールやタスクをデイリーノートにセットアップする"""
    print("朝の処理 (morning) を開始します...")
    try:
        daily_path = get_daily_note_path()
        print(f"対象デイリーノート: {daily_path}")
    except Exception:
        return
    # TODO: Google Calendar/Tasks からの取得、デイリーノートへの追記ロジック
    print("-> 処理完了")

def process_evening():
    """夕方の処理：一日の振り返りや未完了タスクの整理を行う"""
    print("夕方の処理 (evening) を開始します...")
    try:
        daily_path = get_daily_note_path()
        print(f"対象デイリーノート: {daily_path}")
    except Exception:
        return
    # TODO: デイリーノートの整理ロジック
    print("-> 処理完了")

def process_night():
    """夜の処理：翌日に向けた最終整理とノートの確定を行う"""
    print("夜の処理 (night) を開始します...")
    try:
        daily_path = get_daily_note_path()
        print(f"対象デイリーノート: {daily_path}")
    except Exception:
        return
    # TODO: デイリーノートの確定ロジック
    print("-> 処理完了")

def main():
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
