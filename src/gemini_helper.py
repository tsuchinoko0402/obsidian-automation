import os
import google.generativeai as genai

def generate_daily_update(period: str, current_note: str, calendar_events: list, tasks: list, prompt_template_path: str = None) -> str:
    """
    Gemini APIを使用してデイリーノートの更新内容を生成します。
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 GEMINI_API_KEY が設定されていません。")
        
    genai.configure(api_key=api_key)
    # Use standard pro model as text generation is standard
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt_template = ""
    if prompt_template_path and os.path.exists(prompt_template_path):
        with open(prompt_template_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    else:
        prompt_template = """あなたはObsidianを「第二の脳」として管理するアシスタントです。
以下の情報を元に、Obsidianのデイリーノートを更新してください。
元のノートのレイアウト（見出しや構成）を維持したまま、内容を追加・整理してください。
出力はMarkdownのテキストのみとしてください。

実行タイミング: {period}

本日の予定:
{calendar}

未完了タスク:
{tasks}

現在のノートの内容:
{current_note}
"""

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
        
    prompt = prompt_template.format(
        period=period,
        calendar=calendar_text,
        tasks=tasks_text,
        current_note=current_note
    )
    
    response = model.generate_content(prompt)
    return response.text
