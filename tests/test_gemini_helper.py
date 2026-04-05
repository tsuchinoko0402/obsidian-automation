import pytest
from unittest.mock import patch, MagicMock

from src.gemini_helper import generate_daily_update

@patch("src.gemini_helper.genai")
@patch("src.gemini_helper.os.environ.get")
def test_generate_daily_update(mock_get_env, mock_genai):
    mock_get_env.return_value = "fake_api_key"
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "updated text"
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    events = [{'start': {'dateTime': '2026-04-05T10:00:00Z'}, 'summary': 'Meeting'}]
    tasks = [{'title': 'Do laundry'}]
    
    result = generate_daily_update("morning", "current note", events, tasks)
    
    assert result == "updated text"
    mock_genai.configure.assert_called_once_with(api_key="fake_api_key")
    mock_model.generate_content.assert_called_once()
    
    # Check that prompt formatting correctly integrated the text
    prompt_arg = mock_model.generate_content.call_args[0][0]
    assert "morning" in prompt_arg
    assert "Meeting" in prompt_arg
    assert "Do laundry" in prompt_arg
    assert "current note" in prompt_arg

@patch("src.gemini_helper.os.environ.get")
def test_generate_daily_update_no_api_key(mock_get_env):
    mock_get_env.return_value = None
    with pytest.raises(ValueError, match="環境変数 GEMINI_API_KEY が設定されていません"):
        generate_daily_update("morning", "note", [], [])
