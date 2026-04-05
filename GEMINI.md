# Project Context & Agent Instructions

このプロジェクトは、Obsidianのデイリーノート自動生成・管理を行うための自動化スクリプトの開発・運用を目的としています。
Google Calendar や Google Tasks などの外部サービスと連携し、雑多に取ったメモや思いついたこと、タスクなどを整理し管理しやすくするための処理を行います。デイリーノートを中心に眺めることで日々の概要が把握できるようにし、Obsidianを「第二の脳」として活用できるような情報整理を行うことを目指しています。

最終的には `obsidian-daily [morning|evening|night]` コマンドによってどこからでも実行可能なツールとして提供します。

## フォルダ構造

```text
.
├── credentials.json
├── docs/
│   ├── implementation_plan.md
│   └── progress_log.md
├── main.py
├── pyproject.toml
├── README.md
├── src/
│   └── google_auth_helper.py
├── tests/
│   └── test_google_auth_helper.py
└── uv.lock
```

- `docs/`: 計画書 (`implementation_plan.md`) や進捗記録 (`progress_log.md`) などのドキュメントを配置
- `src/`: プロジェクトのメインロジック (Google API認証、Obsidian連携等) を配置
- `tests/`: pytest による単体テストを配置
- パッケージ管理と環境は `uv` で構築・管理しています。

## 作業時のルール (Agent Instructions)

AI (Gemini CLI) がこのプロジェクトで作業を行う際は、以下のルールを必ず遵守してください。

1. **進捗ログの確認**:
   作業を開始する前に必ず `docs/progress_log.md` を読み、現在の進行状況や課題を確認してください。

2. **作業完了時のログ更新**:
   作業（実装、テストの追加、バグ修正など）を終える際は、必ず `docs/progress_log.md` の末尾に以下の情報を追記・編集して更新してください。
   - 本日の日付と実施した内容の概要
   - 発生したエラーとその解決策（もしあれば）
   - 未完了の課題・次のステップ

3. **テストの実施**:
   `src/` 配下のロジックを変更・追加した場合は、`tests/` に対応する単体テストを追加し、以下のコマンドでテストが全てパスすることを確認してから作業を完了してください。
   ```bash
   PYTHONPATH=. uv run pytest tests/
   ```

4. **環境とコード規約**:
   - 依存関係の追加は `uv add <package>` を使用してください。
   - 外部ライブラリを追加する前に、既存のものや標準ライブラリで代替できないか検討してください。
   - コードには適切なdocstring（日本語）を記述し、可読性を重視した実装を行ってください。
