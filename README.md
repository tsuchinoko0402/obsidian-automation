# Obsidian Automation

Obsidian のデイリーノート自動生成・管理を行うためのスクリプト群です。
Google Calendar や Google Tasks 等の外部サービスと連携し、雑多に取ったメモや思いついたこと、タスクなどを整理し管理しやすくするための処理を行います。デイリーノートを中心に眺めることで日々の概要が把握できるようにし、Obsidianを「第二の脳」として活用できるような情報整理を行うことを目的とします。

## 前提条件

- Python 3.12 以上
- `uv` (Python のパッケージ・プロジェクト管理ツール)
- Google Cloud Console で作成した `credentials.json` (OAuth 2.0 クライアント ID)

## 環境のセットアップ

1. 本リポジトリを準備し、カレントディレクトリとします。
2. プロジェクトルートディレクトリに、Google Cloud Console から取得した `credentials.json` を配置します。
3. 以下のコマンドで、必要な依存パッケージのインストールや仮想環境のセットアップを行います。

```bash
uv sync
```

## 現在の実装状況と使い方

### Google API 認証モジュール (`src/google_auth_helper.py`)

Google API を利用するための OAuth 2.0 認証を管理するモジュールです。

**利用方法 (コードからの呼び出し):**
```python
from src.google_auth_helper import get_credentials

# 認証情報を取得します。
# 初回は自動的にブラウザが起動し、Google ログインと権限の許可を求められます。
# 完了後、同じディレクトリに token.pickle が保存され、以後の実行で再利用されます。
creds = get_credentials()
```

## テストの実行方法

このプロジェクトでは `pytest` をテストフレームワークとして利用しています。
以下のコマンドを実行することで、モジュールの単体テストを走らせることができます。

```bash
# プロジェクトのルートディレクトリで実行してください
PYTHONPATH=. uv run pytest tests/
```

テストコードは `tests/` ディレクトリ内に配置されています。
