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
