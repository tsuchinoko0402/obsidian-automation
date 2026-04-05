# Obsidian Automation

Obsidian のデイリーノート自動生成・管理を行うための自動化スクリプトです。
Google Calendar や Google Tasks 等の外部サービスと連携し、雑多に取ったメモや思いついたこと、タスクなどを整理し管理しやすくするための処理を行います。デイリーノートを中心に眺めることで日々の概要が把握できるようにし、Obsidianを「第二の脳」として活用できるような情報整理を行うことを目的とします。

最終的には `obsidian-daily [morning|evening|night]` コマンドによって、ターミナルから手軽に実行可能なツールとして提供されます。

## 機能概要

スクリプトを実行すると、背後で以下の処理が全自動で行われます。

1. **対象ノートの特定**: `obsidian` CLIコマンドを使用して、本日のデイリーノートのパスを自動で取得します。
2. **データの収集**: Google Calendar から本日の予定、Google Tasks から未完了のタスクを取得します。
3. **AIによる情報整理**: 取得した予定、タスク、およびデイリーノートの現在の内容を Gemini API (最新のProモデル) に送信します。元のノートの見出しや構成（レイアウト）を維持したまま、新しく取得した情報が適切な場所に追記・整理されます。
4. **ノートの更新**: 整理された新しい内容で、元のデイリーノートを自動で上書き保存します。

## 前提条件

- Python 3.12 以上
- [uv](https://github.com/astral-sh/uv) (Python パッケージ管理ツール)
- [Obsidian CLI](https://help.obsidian.md/Advanced+topics/Using+obsidian+URI) (`obsidian` コマンドへのパスが通っていること)
- Google Cloud Console で作成した `credentials.json` (OAuth 2.0 クライアント ID)
- [Google AI Studio](https://aistudio.google.com/) で取得した Gemini API キー

## 環境のセットアップ

1. **リポジトリの準備**:
   本リポジトリをクローンし、カレントディレクトリとします。

2. **Google API 認証情報の配置**:
   プロジェクトのルートディレクトリに、Google Cloud Console からダウンロードした `credentials.json` を配置します。

3. **環境変数 (.env) の設定**:
   プロジェクトのルートディレクトリにある `.env.example` をコピーして `.env` を作成し、取得した Gemini API キーを設定します。
   ```bash
   cp .env.example .env
   # .env を編集し、GEMINI_API_KEY="あなたのAPIキー" を追記します
   ```

4. **依存関係のインストール**:
   以下のコマンドで、必要なパッケージをインストールします。
   ```bash
   uv sync
   ```

## 使い方

以下のいずれかのコマンドをプロジェクトのルートディレクトリで実行することで、デイリーノートを更新できます。

```bash
# 朝のセットアップ（一日のスケジュールやタスクをデイリーノートにセットアップ）
uv run src/daily_manager.py morning

# 夕方の整理（一日の振り返りや未完了タスクの整理）
uv run src/daily_manager.py evening

# 夜の確定（翌日に向けた最終整理とノートの確定）
uv run src/daily_manager.py night
```

*※ 初回実行時は、ブラウザが起動し Google アカウントへのログインと権限（カレンダー、タスク）の許可が求められます。許可すると `token.pickle` が生成され、次回以降は自動で認証されます。*

## テストの実行方法

このプロジェクトでは `pytest` をテストフレームワークとして利用しています。
以下のコマンドを実行することで、モジュールの単体テストを走らせることができます。

```bash
PYTHONPATH=. uv run pytest tests/
```
