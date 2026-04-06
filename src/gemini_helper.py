import os
from google import genai

def generate_daily_update(period: str, current_note: str, calendar_events: list = None, tasks: list = None, completed_tasks: list = None, keep_notes: list = None, prompt_template_path: str = None) -> str:
    """
    Gemini APIを使用してデイリーノートの更新内容を生成します。
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 GEMINI_API_KEY が設定されていません。")
        
    client = genai.Client(api_key=api_key)
    
    calendar_events = calendar_events or []
    tasks = tasks or []
    completed_tasks = completed_tasks or []
    keep_notes = keep_notes or []
    
    prompt_template = ""
    if prompt_template_path and os.path.exists(prompt_template_path):
        with open(prompt_template_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    else:
        prompt_template = """あなたはObsidianを「第二の脳」として管理するアシスタントです。
以下の情報を元に、Obsidianのデイリーノートを更新してください。
元のノートのレイアウト（見出しや構成）を維持したまま、内容を追加・整理してください。
出力はMarkdownのテキストのみとしてください。

{period_instruction}

【提供データ】
本日の予定:
{calendar}

未完了タスク (Google Todos):
{tasks}

本日完了したタスク:
{completed_tasks}

Google Keepメモ:
{keep_notes}

現在のノートの内容:
{current_note}
"""

    period_instruction = ""
    if period == "morning":
        period_instruction = "【指示】\n朝のセットアップを行います。提供された「本日の予定」と「未完了タスク」をノート内の適切な場所（例えば今日のスケジュールやタスク一覧セクション）に追記してください。"
    elif period == "evening":
        period_instruction = "【指示】\n夕方の整理を行います。提供された「Google Keepメモ」と「未完了タスク」を読み解き、日中のメモをカテゴリ（Scout, Music, Tech, Privateなど）に分類して活動・思考ログのセクションに追記・整理してください。"
    elif period == "night":
        period_instruction = "【指示】\n夜の最終確定を行います。提供された「本日完了したタスク」を「✅ Completed Today」などの実績セクションに追記し、明日に向けた整理を行ってください。"
    else:
        period_instruction = f"【指示】\n実行タイミング: {period}"

    calendar_text = ""
    for event in calendar_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No title')
        calendar_text += f"- {start}: {summary}\n"
    if not calendar_text:
        calendar_text = "なし\n"
        
    tasks_text = ""
    for task in tasks:
        title = task.get('title', 'No title')
        tasks_text += f"- [ ] {title}\n"
    if not tasks_text:
        tasks_text = "なし\n"

    completed_text = ""
    for task in completed_tasks:
        title = task.get('title', 'No title')
        completed_text += f"- [x] {title}\n"
    if not completed_text:
        completed_text = "なし\n"
        
    keep_text = ""
    for note in keep_notes:
        keep_text += f"- {note}\n"
    if not keep_text:
        keep_text = "なし\n"
        
    prompt = prompt_template.format(
        period=period,
        period_instruction=period_instruction,
        calendar=calendar_text,
        tasks=tasks_text,
        completed_tasks=completed_text,
        keep_notes=keep_text,
        current_note=current_note
    )
    
    model_name = os.environ.get("GEMINI_MODEL", "gemini-pro-latest")
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text
