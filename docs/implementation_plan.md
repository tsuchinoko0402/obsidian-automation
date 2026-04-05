# Obsidian Automation 実装・運用計画

## 1. 開発・実行環境

- リポジトリ: ~/develop/obsidian-automation/
- パッケージ管理: uv (Python 3.12+)
- 目標: コマンド obsidian-daily [morning|evening|night] でどこからでも実行可能にする。

## 2. 実装ミッション

### A. uv による環境構築

1. uv init でプロジェクトを初期化（既存の場合はスキップ）。
2. uv add google-generativeai google-api-python-client google-auth-httplib2 google-auth-oauthlib requests で依存関係を追加。

### B. スクリプトの「ツール化」

- src/daily_manager.py の先頭にシバンを追加: #!/usr/bin/env uv run
- pyproject.toml にスクリプトのエントリポイントを定義するか、実行バイナリへのシンボリックリンクを作成する。

### C. 統合管理ロジックの完成

- Google Auth: token.pickle を使用したセッション維持。
- Obsidian CLI: obsidian daily:path を起点としたアトミックなファイル更新。
- Gemini マージ: _config/templates/prompts/daily_edit_prompt.md を使用したレイアウト維持マージ。

### 3. 自動実行 (cron) 設定

- Mac の crontab に以下を登録する（設定例を docs/crontab_setting.txt に残す）。

```crontab
# 朝の生成 (平日 07:00)
0 7 * * 1-5 /usr/local/bin/obsidian-daily morning
# 夕方の整理 (毎日 18:00)
0 18 * * * /usr/local/bin/obsidian-daily evening
# 夜の確定 (毎日 23:00)
0 23 * * * /usr/local/bin/obsidian-daily night
```

### 4. 進捗ログ (Gemini/CodeAssist へのコンテキスト提供用)

- 作業が完了するたびに docs/progress_log.md に以下を追記・編集してください。
    - 実施した内容
    - 発生したエラーと解決策
    - 未完了の課題
- 以下のような形式で記載してください。

```md
# Project Progress Log

## 2024-XX-XX: 初期設計完了

- Obsidian フォルダ構成の確定。
- デイリーノートテンプレートの確定。
- uv を使用した開発環境の方針決定。
- credentials.json の手動配置完了。

## 現在の課題
- Google API の初回認証フローのテスト。
- obsidian CLI のパス通し確認。
```
