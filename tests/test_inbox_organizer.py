import pytest
from unittest.mock import patch, MagicMock

from src.inbox_organizer import organize_inbox, OrganizationResult

@patch("src.inbox_organizer.genai")
@patch("src.inbox_organizer.os.environ.get")
@patch("src.inbox_organizer.os.listdir")
@patch("src.inbox_organizer.os.path.exists")
@patch("src.inbox_organizer.shutil.move")
@patch("builtins.open")
def test_organize_inbox(mock_open, mock_move, mock_exists, mock_listdir, mock_get_env, mock_genai):
    mock_get_env.return_value = "fake_api_key"
    def mock_exists_side_effect(path):
        if "test_note.md" in path and "30_tech" in path:
            return False
        return True
    mock_exists.side_effect = mock_exists_side_effect
    mock_listdir.return_value = ["test_note.md"]
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Mocking Gemini response containing JSON string
    mock_response.text = '{"target_folder": "30_tech", "target_moc": "MOC_tech"}'
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client
    
    # Just checking it runs without errors and moves the file
    with patch("src.inbox_organizer.os.walk") as mock_walk:
        mock_walk.return_value = [("/vault/root", [], ["MOC_tech.md"])]
        organize_inbox("/vault/root")
        
    mock_move.assert_called_once()
    assert "30_tech" in mock_move.call_args[0][1]
