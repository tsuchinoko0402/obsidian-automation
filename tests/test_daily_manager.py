import subprocess
import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open

from src.daily_manager import (
    get_daily_note_path,
    find_vault_root,
    process_daily_note,
    process_morning,
    process_evening,
    process_night,
    main
)

def test_get_daily_note_path_success():
    mock_result = MagicMock()
    mock_result.stdout = "/path/to/daily_note.md\n"
    
    with patch("src.daily_manager.subprocess.run", return_value=mock_result) as mock_run:
        result = get_daily_note_path()
        assert result == "/path/to/daily_note.md"

def test_find_vault_root():
    with patch("os.path.exists") as mock_exists:
        # Simulate .obsidian exists at /path/to/vault/.obsidian
        def side_effect(path):
            return path == "/path/to/vault/.obsidian"
        mock_exists.side_effect = side_effect
        
        root = find_vault_root("/path/to/vault/Daily/2026-04-05.md")
        assert root == "/path/to/vault"

@patch("src.daily_manager.get_daily_note_path")
@patch("src.daily_manager.os.path.exists")
@patch("src.daily_manager.get_calendar_events")
@patch("src.daily_manager.get_tasks")
@patch("src.daily_manager.generate_daily_update")
@patch("builtins.open", new_callable=mock_open, read_data="current text")
def test_process_daily_note(mock_file, mock_generate, mock_tasks, mock_events, mock_exists, mock_get_path):
    mock_get_path.return_value = "/path/to/vault/daily.md"
    mock_exists.return_value = True # File exists
    mock_events.return_value = []
    mock_tasks.return_value = []
    mock_generate.return_value = "```markdown\nnew text\n```"
    
    with patch("src.daily_manager.find_vault_root") as mock_find_root:
        mock_find_root.return_value = "/path/to/vault"
        process_daily_note("morning")
        
    mock_generate.assert_called_once()
    
    # Check if backticks were removed
    handle = mock_file()
    handle.write.assert_called_with("new text\n")

@patch("src.daily_manager.process_daily_note")
def test_process_functions(mock_process):
    process_morning()
    mock_process.assert_called_with("morning")
    process_evening()
    mock_process.assert_called_with("evening")
    process_night()
    mock_process.assert_called_with("night")

@patch("src.daily_manager.process_morning")
@patch("sys.argv", ["daily_manager.py", "morning"])
def test_main_morning(mock_process_morning):
    main()
    mock_process_morning.assert_called_once()
