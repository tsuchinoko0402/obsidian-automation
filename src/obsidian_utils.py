import os
import subprocess
import sys

# Obsidian コマンドのパス設定（.env で上書き可能、デフォルトは Mac の標準パス）
OBSIDIAN_CMD = os.environ.get("OBSIDIAN_PATH", "/Applications/Obsidian.app/Contents/MacOS/obsidian")

def get_vault_path() -> str:
    """Obsidian CLI を使用してVaultのルートパスを取得します。"""
    try:
        vault_result = subprocess.run(
            [OBSIDIAN_CMD, "vault", "info=path"],
            capture_output=True,
            text=True,
            check=True
        )
        return vault_result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Obsidian CLI の実行に失敗しました: {e.stderr}", file=sys.stderr)
        raise

def get_daily_note_path() -> str:
    """Obsidian CLI を使用して現在のデイリーノートの絶対パスを取得します。"""
    try:
        # Vaultのパスを取得
        vault_path = get_vault_path()

        # obsidian daily:path コマンドを実行し、デイリーノートのパスを取得
        daily_result = subprocess.run(
            [OBSIDIAN_CMD, "daily:path"],
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
        print(f"{OBSIDIAN_CMD} が見つかりません。パスが通っているか確認してください。", file=sys.stderr)
        raise
