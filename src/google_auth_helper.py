import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# スコープを変更する場合は、token.pickle ファイルを削除してください。
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]

def get_credentials(scopes=None, token_path='token.pickle', creds_path='credentials.json'):
    """
    保存されたユーザー認証情報を取得します。

    token.pickle ファイルが存在する場合はそれを利用して認証情報を読み込みます。
    有効な認証情報がない場合、または期限切れの場合は、
    リフレッシュトークンを使用して更新するか、ローカルサーバーを起動して
    ユーザーにログインを促し、新しい認証情報を取得・保存します。

    Args:
        scopes (list, optional): 要求するOAuth 2.0スコープのリスト。デフォルトは SCOPES 定数。
        token_path (str, optional): 認証情報を保存するpickleファイルのパス。デフォルトは 'token.pickle'。
        creds_path (str, optional): クライアントシークレットJSONファイルのパス。デフォルトは 'credentials.json'。

    Returns:
        google.oauth2.credentials.Credentials: 有効なGoogle API認証情報オブジェクト。

    Raises:
        FileNotFoundError: credentials.json が見つからない場合。
    """
    if scopes is None:
        scopes = SCOPES
    
    creds = None
    # token.pickle ファイルにはユーザーのアクセスとリフレッシュトークンが保存されており、
    # 初回認証フロー完了時に自動的に作成されます。
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    # 有効な認証情報がない場合はユーザーにログインさせます。
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"{creds_path} が見つかりません。Google Cloud Consoleからダウンロードしてください。")
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, scopes)
            creds = flow.run_local_server(port=0)
            
        # 次回実行時のために認証情報を保存します
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
    return creds
