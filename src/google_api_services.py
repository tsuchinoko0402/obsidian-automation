import datetime
from googleapiclient.discovery import build
from src.google_auth_helper import get_credentials

def get_calendar_events(date=None):
    """
    指定された日付の予定をGoogle Calendarから取得します。
    デフォルトは今日です。
    """
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    if date is None:
        date = datetime.date.today()
        
    # timezone is required for timeMin/timeMax. Using basic UTC Z for simplicity
    # but strictly it should use the local timezone. Let's use local timezone if possible
    # For now, just using naive midnight to midnight in UTC might cause offset issues.
    # A better approach is to use timezone-aware datetimes.
    # Python 3.12 has datetime.UTC
    start_of_day = datetime.datetime.combine(date, datetime.time.min).astimezone().isoformat()
    end_of_day = datetime.datetime.combine(date, datetime.time.max).astimezone().isoformat()
    
    events_result = service.events().list(
        calendarId='primary', timeMin=start_of_day, timeMax=end_of_day,
        singleEvents=True, orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])

def get_tasks():
    """
    Google Tasksから未完了のタスクを取得します。
    """
    creds = get_credentials()
    service = build('tasks', 'v1', credentials=creds)
    
    # '@default' tasklist
    tasks_result = service.tasks().list(tasklist='@default', showHidden=False).execute()
    return tasks_result.get('items', [])

def get_keep_notes(days_back=1):
    """
    gkeepapiを使用してGoogle Keepから最近のメモを取得します。
    """
    import os
    import gkeepapi
    
    username = os.environ.get("KEEP_USERNAME")
    password = os.environ.get("KEEP_PASSWORD")
    token_file = 'keep_token.txt'
    
    if not username or not password:
        print("Google Keepの認証情報が設定されていません (.envのKEEP_USERNAME/KEEP_PASSWORDを確認してください)。")
        return []

    keep = gkeepapi.Keep()
    
    # トークンによる認証を試みる
    try:
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                master_token = f.read().strip()
            if master_token:
                keep.resume(username, master_token)
                print("Google Keep: 既存のトークンで認証しました。")
            else:
                raise ValueError("空のトークンファイルです。")
        else:
            # 新規認証（アプリパスワードを使用）
            print(f"Google Keep: {username} として新規認証を試行中...")
            keep.authenticate(username, password)
            master_token = keep.getMasterToken()
            if master_token:
                with open(token_file, 'w') as f:
                    f.write(master_token)
                print("Google Keep: 新しいトークンを発行して認証しました。")
            else:
                print("Google Keep: 認証に成功しましたが、トークンの取得に失敗しました。")
    except Exception as e:
        print(f"Google Keepの認証に失敗しました: {e}")
        print("【確認事項】")
        print("1. .env の KEEP_PASSWORD が「16桁のアプリパスワード」であることを確認してください。")
        print("2. 以下のURLにアクセスしてアクセスを許可してください: https://accounts.google.com/DisplayUnlockCaptcha")
        # 認証に失敗した場合はトークンファイルを削除
        if os.path.exists(token_file):
            os.remove(token_file)
        return []

    # 全メモを同期
    keep.sync()

    # 抽出する基準時間を設定 (24時間前)
    threshold = datetime.datetime.now() - datetime.timedelta(days=days_back)
    
    # 全メモを取得（アーカイブ・ゴミ箱以外）
    notes = keep.find(archived=False, trashed=False)

    recent_notes_text = []

    for note in notes:
        # note.timestamps.updated は naive な datetime (UTC)
        if note.timestamps.updated > threshold:
            # タイトルと本文を整形
            title = note.title if note.title else "(無題)"
            recent_notes_text.append(f"【{title}】\n{note.text}")

    return recent_notes_text

def get_completed_tasks(date=None):
    """
    Google Tasksから指定された日付（デフォルトは今日）に完了したタスクを取得します。
    """
    creds = get_credentials()
    service = build('tasks', 'v1', credentials=creds)
    
    if date is None:
        date = datetime.date.today()
        
    start_of_day = datetime.datetime.combine(date, datetime.time.min).astimezone()
    end_of_day = datetime.datetime.combine(date, datetime.time.max).astimezone()
    
    # '@default' tasklist
    # showHidden=True to include completed tasks
    tasks_result = service.tasks().list(tasklist='@default', showHidden=True).execute()
    
    all_tasks = tasks_result.get('items', [])
    completed_tasks = []
    
    for task in all_tasks:
        if task.get('status') == 'completed':
            completed_date_str = task.get('completed')
            if completed_date_str:
                # API returns string like "2026-04-05T12:00:00.000Z"
                # python 3.12 fromisoformat handles 'Z' correctly
                try:
                    completed_dt = datetime.datetime.fromisoformat(completed_date_str).astimezone()
                    if start_of_day <= completed_dt <= end_of_day:
                        completed_tasks.append(task)
                except ValueError:
                    pass
                    
    return completed_tasks
