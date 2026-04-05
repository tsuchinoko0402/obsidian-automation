import pytest
from unittest.mock import patch, MagicMock

from src.gemini_helper import generate_daily_update

@patch("src.gemini_helper.genai")
@patch("src.gemini_helper.os.environ.get")
def test_generate_daily_update(mock_get_env, mock_genai):
    def mock_env_get(key, default=None):
        if key == "GEMINI_API_KEY":
            return "fake_api_key"
        return default
    mock_get_env.side_effect = mock_env_get
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "updated text"
    
    # Mocking client.models.generate_content
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client
    
    events = [{'start': {'dateTime': '2026-04-05T10:00:00Z'}, 'summary': 'Meeting'}]
    tasks = [{'title': 'Do laundry'}]
    
    result = generate_daily_update("morning", "current note", events, tasks)
    
    assert result == "updated text"
    mock_genai.Client.assert_called_once_with(api_key="fake_api_key")
    mock_client.models.generate_content.assert_called_once()
    
    # Check that prompt formatting correctly integrated the text
    kwargs = mock_client.models.generate_content.call_args[1]
    prompt_arg = kwargs.get('contents') or mock_client.models.generate_content.call_args[0][0]
    
    assert kwargs.get('model') == 'gemini-pro-latest'
    assert "朝のセットアップを行います" in prompt_arg
    assert "Meeting" in prompt_arg
    assert "Do laundry" in prompt_arg
    assert "current note" in prompt_arg

@patch("src.gemini_helper.os.environ.get")
def test_generate_daily_update_no_api_key(mock_get_env):
    mock_get_env.return_value = None
    with pytest.raises(ValueError, match="環境変数 GEMINI_API_KEY が設定されていません"):
        generate_daily_update("morning", "note", [], [])
