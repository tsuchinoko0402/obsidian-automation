import pytest
from unittest.mock import patch, MagicMock, mock_open

# Local
from src.notes_processor import NoteAction, _get_action_for_note, _append_summary_to_daily, _create_new_note_and_link, process_unprocessed_notes

@patch("src.notes_processor.genai")
def test_get_action_for_note(mock_genai):
    """Test Gemini decision making for note actions."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"action": "create_new_note", "new_note_title": "Test", "target_folder": "30_tech", "target_moc": "MOC_tech"}'
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        result = _get_action_for_note("some content")

    assert isinstance(result, NoteAction)
    assert result.action == "create_new_note"
    assert result.new_note_title == "Test"

@patch("src.notes_processor.get_daily_note_path")
@patch("builtins.open", new_callable=mock_open, read_data="existing content")
def test_append_summary_to_daily(mock_file, mock_get_daily_path):
    """Test appending a summary to the daily note."""
    mock_get_daily_path.return_value = "/fake/daily.md"
    
    with patch("os.path.exists", return_value=True):
        success = _append_summary_to_daily("Test summary")

    assert success is True
    # Initial read to check heading, then append
    mock_file.assert_any_call("/fake/daily.md", "a", encoding="utf-8")

@patch("src.notes_processor.get_daily_note_path")
@patch("src.notes_processor.os.makedirs")
@patch("src.notes_processor.os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data="existing content")
@patch("os.walk")
def test_create_new_note_and_link(mock_walk, mock_file, mock_exists, mock_makedirs, mock_get_daily_path):
    """Test creating a new note and linking it."""
    # Mock exists to return False for new note, but True for daily note and MOC
    def exists_side_effect(path):
        if "New Tech Note.md" in path:
            return False
        return True
    mock_exists.side_effect = exists_side_effect
    
    mock_get_daily_path.return_value = "/fake/daily.md"
    mock_walk.return_value = [("/fake/vault", [], ["MOC_tech.md"])] # MOC exists

    success = _create_new_note_and_link("New Tech Note", "content", "30_tech", "MOC_tech", "/fake/vault")

    assert success is True
    # Check that new note was created
    mock_file.assert_any_call("/fake/vault/30_tech/New Tech Note.md", "w", encoding="utf-8")
    # Check that MOC was updated
    mock_file.assert_any_call("/fake/vault/MOC_tech.md", "a", encoding="utf-8")
    # Check that daily note was updated
    mock_file.assert_any_call("/fake/daily.md", "a", encoding="utf-8")

@patch("src.notes_processor.get_unprocessed_apple_notes")
@patch("src.notes_processor._get_action_for_note")
@patch("src.notes_processor._append_summary_to_daily")
@patch("src.notes_processor._create_new_note_and_link")
@patch("src.notes_processor.mark_apple_note_as_processed")
@patch("src.notes_processor.get_vault_path")
def test_process_unprocessed_notes_loop(mock_get_vault, mock_mark, mock_create, mock_append, mock_get_action, mock_get_notes):
    """Test the main loop of processing notes."""
    mock_note = MagicMock()
    mock_note.name = "Test Note"
    mock_note.plaintext = "This is a test note about tech."
    
    mock_get_notes.return_value = [mock_note]
    mock_get_vault.return_value = "/fake/vault"
    
    mock_action = NoteAction(
        action="create_new_note",
        new_note_title="New Test Note",
        target_folder="30_tech",
        target_moc="MOC_tech"
    )
    mock_get_action.return_value = mock_action
    mock_create.return_value = True # Simulate successful creation

    process_unprocessed_notes()

    mock_get_notes.assert_called_once()
    mock_get_action.assert_called_once_with("This is a test note about tech.")
    mock_create.assert_called_once()
    mock_mark.assert_called_once_with(mock_note)
