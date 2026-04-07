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

## 2026-04-05: Google Keepの実装（試行）と夕方 (evening) プロセスの完成

- `gkeepapi` ライブラリを追加し、`src/google_api_services.py` に `get_keep_notes` を実装。
- ただしGoogle側の認証制限（BadAuthentication）によりKeepの直接取得は不安定なため、運用上の課題として残る。

## 2026-04-05: Apple純正メモ連携機能 (notes) の実装完了

- `macnotesapp` ライブラリを用いて、Appleメモアプリから未処理（「#処理済み」タグがない）メモを取得し、Geminiで要約または新規ノート作成を行う機能を実装。
- 循環インポート（circular import）問題を解決するため、Vaultパス取得等の共通関数を `src/obsidian_utils.py` に分離。
- `src/notes_processor.py` で発生していた `SyntaxError`（f-string内の改行文字の扱い）を、`sed` および精密な `replace` を用いて修正完了。
- 実際にApple Notesからメモを取り込み、Geminiの判断で新規ノート作成やデイリーノートへのリンク追記ができることを確認。

## 2026-04-05: Inbox自動整理機能 (organize) の追加

- `src/inbox_organizer.py` を新規作成し、`00_inbox` 内のマークダウンファイルをGemini API（構造化JSON出力）を用いて自動分類するロジックを実装。
- ユーザー指定のフォルダ構成（`10_scout`, `20_music`, `30_tech`など）および対象MOCリストに基づき、適切なフォルダへのファイル移動とMOCへのリンク追記（`[[ノート名]]`）を行う仕組みを構築。

## 現在の課題
- `obsidian-daily` コマンドとしてどこからでも呼び出せるようにするためのシンボリックリンクの作成（ユーザー環境での設定待ち）。
- 一部のMOCファイル（`MOC_tech.md` 等）がVault内に存在しないため、リンク追記時に警告が出る場合がある。
