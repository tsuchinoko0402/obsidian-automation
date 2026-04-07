# Obsidian Automation

Obsidian のデイリーノート自動生成・管理、およびナレッジの自動整理を行うための自動化スクリプト群です。
Google Calendar, Google Tasks, Apple 純正メモ等の外部サービスと連携し、AI（Gemini）を活用して日々の情報を整理し、Obsidian を真の「第二の脳」として機能させることを目的とします。

最終的には `obsidian-daily` コマンドとして、ターミナルやオートメーションから手軽に実行可能なツールを提供します。

## 主な機能

### 1. デイリーノート自動更新 (`morning`, `evening`, `night`)
実行時間帯に合わせて、以下の処理を自動で行います。
- **朝 (`morning`)**: 本日の予定（Google Calendar）と未完了タスク（Google Tasks）をデイリーノートに注入。
- **夕方 (`evening`)**: 日中のメモや未完了タスクを読み解き、カテゴリ別に活動ログを整理。
- **夜 (`night`)**: 本日完了したタスクの実績を記録し、手動レビューのためにノートを開く。最後に Google Drive 等への同期を実行（任意）。

### 2. Apple 純正メモの自動取り込み (`notes`)
iPhone や iPad の純正メモアプリで取った雑多なメモを Obsidian に同期します。
- 「#処理済み」タグがないメモを自動抽出。
- Gemini が内容を判断し、「デイリーノートへの要約追記」または「新規ノートとして作成＋MOCへのリンク」を自動実行。
- 処理完了後、元のメモに「#処理済み」タグを自動付与。

### 3. Inbox の自動整理 (`organize`)
Obsidian 内の `00_inbox` フォルダにある未分類ノートを AI が自動で仕分けます。
- 内容に基づき、適切なカテゴリフォルダ（`10_scout`, `20_music`, `30_tech`, `40_private` 等）へ移動。
- 対応する MOC（Map of Content）ファイルへ自動的にリンクを追記。

## 前提条件

- Python 3.12 以上
- [uv](https://github.com/astral-sh/uv) (Python パッケージ管理ツール)
- [Obsidian CLI](https://help.obsidian.md/Advanced+topics/Using+obsidian+URI) (`obsidian` コマンドが `/Applications/Obsidian.app/Contents/MacOS/obsidian` にあること)
- Google Cloud Console で作成した `credentials.json` (Google API 用)
- [Google AI Studio](https://aistudio.google.com/) で取得した Gemini API キー

## 環境のセットアップ

1. **リポジトリの準備**:
   本リポジトリをクローンします。

2. **認証情報の配置**:
   プロジェクトルートに Google API の `credentials.json` を配置します。

3. **環境変数 (.env) の設定**:
   `.env.example` をコピーして `.env` を作成し、以下を設定します。
   - `GEMINI_API_KEY`: Gemini API キー
   - `KEEP_USERNAME` / `KEEP_PASSWORD`: Google Keep 連携用（オプション）
   - `OBSIDIAN_PATH`: Obsidian の実行パス（デフォルトは Mac 標準パス）

4. **依存関係のインストール**:
   ```bash
   uv sync
   ```

## 使い方

プロジェクトのルートディレクトリで以下のコマンドを実行します。

```bash
# デイリーノートの更新
uv run src/daily_manager.py morning
uv run src/daily_manager.py evening
uv run src/daily_manager.py night

# Apple メモの取り込み
uv run src/daily_manager.py notes

# Inbox 内のファイル整理
uv run src/daily_manager.py organize
```

### 定期実行（macOS オートメーション / cron）
自動実行を行う際は、ログを日付別に管理し、30日分保存する以下のテンプレートを「ショートカット」アプリの「シェルスクリプトを実行」に設定することをおすすめします。

```bash
PROJECT_DIR="/Users/shogo/develop/obsidian-automation"
CMD="morning" # 実行したいコマンド名
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d)_$CMD.log"
mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"
./.venv/bin/python src/daily_manager.py "$CMD" >> "$LOG_FILE" 2>&1
find "$LOG_DIR" -name "*.log" -mtime +30 -delete
```

## テストの実行方法

```bash
PYTHONPATH=. uv run pytest tests/
```
