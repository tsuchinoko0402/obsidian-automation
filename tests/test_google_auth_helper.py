import os
import pickle
import pytest
from unittest.mock import patch, MagicMock
from google.oauth2.credentials import Credentials
from src.google_auth_helper import get_credentials, SCOPES

@pytest.fixture
def mock_creds():
    creds = MagicMock(spec=Credentials)
    creds.valid = True
    return creds

@patch('src.google_auth_helper.os.path.exists')
@patch('builtins.open', new_callable=MagicMock)
@patch('src.google_auth_helper.pickle.load')
def test_get_credentials_valid_token_exists(mock_pickle_load, mock_open, mock_exists, mock_creds):
    """token.pickle が存在し、有効な認証情報が取得できる場合のテスト"""
    mock_exists.return_value = True
    mock_pickle_load.return_value = mock_creds

    creds = get_credentials(token_path='dummy_token.pickle')

    assert creds == mock_creds
    mock_exists.assert_called_once_with('dummy_token.pickle')
    mock_pickle_load.assert_called_once()

@patch('src.google_auth_helper.os.path.exists')
@patch('builtins.open', new_callable=MagicMock)
@patch('src.google_auth_helper.pickle.load')
@patch('src.google_auth_helper.Request')
@patch('src.google_auth_helper.pickle.dump')
def test_get_credentials_expired_token_refresh(mock_pickle_dump, mock_request, mock_pickle_load, mock_open, mock_exists):
    """token.pickle が存在し、期限切れだがリフレッシュ可能な場合のテスト"""
    expired_creds = MagicMock(spec=Credentials)
    expired_creds.valid = False
    expired_creds.expired = True
    expired_creds.refresh_token = "dummy_refresh_token"
    
    mock_exists.return_value = True
    mock_pickle_load.return_value = expired_creds

    creds = get_credentials(token_path='dummy_token.pickle')

    assert creds == expired_creds
    expired_creds.refresh.assert_called_once()
    mock_pickle_dump.assert_called_once()

@patch('src.google_auth_helper.os.path.exists')
@patch('src.google_auth_helper.InstalledAppFlow')
@patch('builtins.open', new_callable=MagicMock)
@patch('src.google_auth_helper.pickle.dump')
def test_get_credentials_no_token_flow(mock_pickle_dump, mock_open, mock_flow_class, mock_exists, mock_creds):
    """token.pickle が存在せず、新規に認証フローを実行する場合のテスト"""
    # os.path.exists のモック設定
    # token_path のチェックは False、creds_path のチェックは True を返すようにする
    def exists_side_effect(path):
        if path == 'dummy_token.pickle':
            return False
        if path == 'dummy_creds.json':
            return True
        return False
    mock_exists.side_effect = exists_side_effect

    mock_flow_instance = MagicMock()
    mock_flow_instance.run_local_server.return_value = mock_creds
    mock_flow_class.from_client_secrets_file.return_value = mock_flow_instance

    creds = get_credentials(token_path='dummy_token.pickle', creds_path='dummy_creds.json')

    assert creds == mock_creds
    mock_flow_class.from_client_secrets_file.assert_called_once_with('dummy_creds.json', SCOPES)
    mock_flow_instance.run_local_server.assert_called_once_with(port=0)
    mock_pickle_dump.assert_called_once()

@patch('src.google_auth_helper.os.path.exists')
def test_get_credentials_no_creds_file(mock_exists):
    """credentials.json が存在しない場合、例外が発生することのテスト"""
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError, match="が見つかりません"):
        get_credentials(token_path='missing_token.pickle', creds_path='missing_creds.json')
