# Project Progress Log

## 2026-04-05: 依存関係と認証ロジックのセットアップ

- `uv` を使用して依存関係 (`google-generativeai`, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `requests`) を追加完了。
- `src/google_auth_helper.py` に `token.pickle` を使用したGoogle API認証ロジックの実装完了。
- `src/google_auth_helper.py` のdocstringを追加し、可読性を向上。
- `pytest` と `pytest-mock` を追加し、`tests/test_google_auth_helper.py` に単体テストを実装（全てパス）。
- `README.md` を更新し、セットアップやテスト実行方法を記載。
- `GEMINI.md` を作成し、プロジェクトのコンテキストとエージェント（AI）への指示を定義。
- プロジェクトの目的を「日々のタスク管理の完結」から、「Obsidianを第二の脳として活用するための情報整理」へ変更（`README.md`および`GEMINI.md`）。
- **Google API認証の課題を解決**: Google Cloud ConsoleのOAuth同意画面にて自身のメールアドレスをテストユーザーとして追加することで、403エラーを解消。
- **Obsidian CLIの課題を解決**: `obsidian daily:path` の動作確認に成功。
- `src/daily_manager.py` を作成し、`morning`, `evening`, `night` の引数を受け取るCLIの基本骨格を実装完了。先頭のシバン (`#!/usr/bin/env uv run`) を用いて単体で実行可能に設定。
- `tests/test_daily_manager.py` を作成し、`src/daily_manager.py` の単体テストを実装（全てパス）。

## 2026-04-05: 主要ロジックとテストの実装完了、ライブラリ移行

- Google Calendar と Tasks からデータを取得する処理を `src/google_api_services.py` に実装完了。
- Gemini API を利用してノートの更新内容を生成する処理を `src/gemini_helper.py` に実装完了。
- `src/daily_manager.py` 内に各機能を統合し、デイリーノートの読み込みからGeminiでの整理、書き込みまでの主要なワークフローを完成。
- 非推奨となっていた `google-generativeai` を削除し、推奨パッケージである `google-genai` に移行。コードおよびテストを更新し、警告を解消。
- `python-dotenv` を追加し、プロジェクトルートの `.env` ファイルから `GEMINI_API_KEY` などの環境変数を読み込めるように `src/daily_manager.py` を修正。
- 上記の実装に対応する単体テストを `tests/` に追加・修正し、全テストパスを確認（`PYTHONPATH=. uv run pytest tests/` で13件中13件成功）。

## 2026-04-05: 朝と夜の個別ワークフロー基盤の構築

- `src/google_api_services.py` に `get_completed_tasks` 関数を追加し、Google Tasksから指定日（今日）の完了済みタスクのみを取得する処理を実装。
- `src/gemini_helper.py` のプロンプトを改修。単なる時間帯文字列の置換から、朝・夕・夜それぞれの役割に合わせた専用の指示（プロンプト）を生成してGeminiに渡すように変更。
- `src/daily_manager.py` において、`morning`, `evening`, `night` でそれぞれ異なるデータを取得・処理するように分岐処理を追加。
- 朝（`morning`）の処理開始時に `obsidian daily` コマンドを実行し、ノートが未作成の場合は自動で生成（開く）する処理を追加。
- 夜（`night`）の処理完了後に `obsidian daily` コマンドでノートを開き手動レビューを促す機能と、プロジェクト直下に `mirror_obsidian.sh` が存在する場合はGoogle Drive等への同期を実行する機能を追加。
- 上記の実装に対応する単体テストの修正を行い、全テストパスを確認（`PYTHONPATH=. uv run pytest tests/` で13件中13件成功）。

## 2026-04-05: Google Keepの実装と夕方 (evening) プロセスの完成

- `gkeepapi` ライブラリを追加し、`src/google_api_services.py` に `get_keep_notes` を実装。`.env` から `KEEP_USERNAME` と `KEEP_PASSWORD`（アプリパスワード）を読み込み、直近24時間以内に更新されたメモを自動取得する仕組みを構築。
- `.env.example` に Google Keep の認証情報に関する項目を追加。
- `src/daily_manager.py` の `evening` 処理にて、実際に Google Keep のメモを取得して Gemini に渡すように変更。
- `src/gemini_helper.py` のプロンプトを更新し、「Google Keepメモ」と「未完了タスク」を読み解いて日中のメモをカテゴリ（Scout, Music, Tech, Privateなど）に分類して活動・思考ログに追記するよう指示を追加。
- これにより、朝(`morning`)、夕方(`evening`)、夜(`night`) の3つの時間帯に応じた独自のワークフロー（データの取得元とGeminiへのプロンプトの出し分け）が実データを用いて稼働可能な状態で完成。

## 2026-04-05: Apple純正メモ連携機能の基盤構築 (macnotesapp)

- `macnotesapp` ライブラリを追加。
- `src/apple_notes_helper.py` を新規作成し、以下の機能を実装：
    - `get_unprocessed_apple_notes()`: Appleメモアプリから「#処理済み」タグが付いていないメモを取得。
    - `mark_apple_note_as_processed(note)`: 指定されたAppleメモに「#処理済み」タグを付与。
- `tests/test_apple_notes_helper.py` を作成し、上記機能の単体テストを実装。全テストがパスすることを確認（`PYTHONPATH=. uv run pytest tests/` で17件中17件成功）。
- 今後、このヘルパー関数を利用して Gemini と連携し、メモの分類・整理を行う予定。

## 2026-04-05: Apple純正メモ連携機能の基盤構築 (macnotesapp)

- `macnotesapp` ライブラリを追加。
- `src/apple_notes_helper.py` を新規作成し、以下の機能を実装：
    - `get_unprocessed_apple_notes()`: Appleメモアプリから「#処理済み」タグが付いていないメモを取得。
    - `mark_apple_note_as_processed(note)`: 指定されたAppleメモに「#処理済み」タグを付与。
- `tests/test_apple_notes_helper.py` を作成し、上記機能の単体テストを実装。全テストがパスすることを確認（`PYTHONPATH=. uv run pytest tests/` で17件中17件成功）。
- 今後、このヘルパー関数を利用して Gemini と連携し、メモの分類・整理を行う予定。

## 2026-04-05: Inbox自動整理機能 (organize) の追加

- `src/inbox_organizer.py` を新規作成し、`00_inbox` 内のマークダウンファイルをGemini API（構造化JSON出力）を用いて自動分類するロジックを実装。
- ユーザー指定のフォルダ構成（`10_scout`, `20_music`, `30_tech`など）および対象MOCリストに基づき、適切なフォルダへのファイル移動とMOCへのリンク追記（`[[ノート名]]`）を行う仕組みを構築。
- `src/daily_manager.py` のコマンドライン引数に `organize` を追加し、`uv run src/daily_manager.py organize` として単独実行できる機能を提供。
