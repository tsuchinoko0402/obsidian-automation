import pytest
from unittest.mock import MagicMock, patch
from macnotesapp import Note # Import the actual Note class if possible for type hinting

from src.apple_notes_helper import get_unprocessed_apple_notes, mark_apple_note_as_processed

# Helper function to create a mock Note object
def create_mock_note(name="Test Note", plaintext="Some content", body="<p>Some content</p>"):
    mock_note = MagicMock(spec=Note)
    mock_note.name = name
    mock_note.plaintext = plaintext
    mock_note.body = body
    # Ensure body can be modified as in mark_apple_note_as_processed
    return mock_note

@patch("src.apple_notes_helper.NotesApp")
def test_get_unprocessed_apple_notes(mock_notes_app_cls):
    # Mock NotesApp instance and its notes() method
    mock_notes_app = MagicMock()
    mock_notes_app_cls.return_value = mock_notes_app

    # Create mock notes
    note1 = create_mock_note("Note 1", "Content 1")
    note2 = create_mock_note("Note 2", "Content 2 #処理済み")
    note3 = create_mock_note("Note 3", "Content 3 without tag")

    mock_notes_app.notes.return_value = [note1, note2, note3]

    unprocessed = get_unprocessed_apple_notes()

    # Assert that only note1 and note3 are returned (note2 has the tag)
    assert len(unprocessed) == 2
    assert unprocessed[0].name == "Note 1"
    assert unprocessed[1].name == "Note 3"
    mock_notes_app_cls.assert_called_once()
    mock_notes_app.notes.assert_called_once()

@patch("builtins.print") # To capture print statements
def test_mark_apple_note_as_processed(mock_print):
    note = create_mock_note("Test Note for Tagging", "Original content", "<p>Original content</p>")
    
    mark_apple_note_as_processed(note)
    
    # Assert that the tag was appended to the body
    assert "#処理済み" in note.body
    assert note.body.endswith("<br><br>#処理済み")
    mock_print.assert_called_with("✅ Appleメモ「Test Note for Tagging」を処理済みにしました。")

@patch("builtins.print")
def test_mark_apple_note_as_processed_failure(mock_print):
    note = create_mock_note("Failing Note", "Content")
    
    # Mock the += operation on note.body to raise an exception
    mock_body_value = MagicMock()
    mock_body_value.__iadd__.side_effect = Exception("Mock write error")
    note.body = mock_body_value # Replace the body property with this mock
    
    mark_apple_note_as_processed(note)

    mock_print.assert_called_with("❌ Appleメモ「Failing Note」の処理済みタグ付けに失敗しました: Mock write error")
