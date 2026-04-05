import subprocess
import sys
import pytest
from unittest.mock import patch, MagicMock

from src.daily_manager import (
    get_daily_note_path,
    process_morning,
    process_evening,
    process_night,
    main
)

def test_get_daily_note_path_success():
    """obsidian daily:path が成功した場合のテスト"""
    mock_result = MagicMock()
    mock_result.stdout = "/path/to/daily_note.md\n"
    
    with patch("src.daily_manager.subprocess.run", return_value=mock_result) as mock_run:
        result = get_daily_note_path()
        assert result == "/path/to/daily_note.md"
        mock_run.assert_called_once_with(
            ["obsidian", "daily:path"], 
            capture_output=True, 
            text=True, 
            check=True
        )

def test_get_daily_note_path_called_process_error(capsys):
    """obsidian daily:path コマンドがエラー終了した場合のテスト"""
    mock_error = subprocess.CalledProcessError(1, ["obsidian", "daily:path"], stderr="Command failed")
    
    with patch("src.daily_manager.subprocess.run", side_effect=mock_error):
        with pytest.raises(subprocess.CalledProcessError):
            get_daily_note_path()
    
    captured = capsys.readouterr()
    assert "Obsidian CLI (daily:path) の実行に失敗しました" in captured.err

def test_get_daily_note_path_file_not_found_error(capsys):
    """obsidian コマンドが見つからない場合のテスト"""
    with patch("src.daily_manager.subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            get_daily_note_path()
            
    captured = capsys.readouterr()
    assert "obsidian コマンドが見つかりません" in captured.err

@patch("src.daily_manager.get_daily_note_path")
def test_process_morning(mock_get_path, capsys):
    """morning 処理のテスト"""
    mock_get_path.return_value = "/path/to/daily_note.md"
    process_morning()
    captured = capsys.readouterr()
    assert "朝の処理 (morning) を開始します..." in captured.out
    assert "対象デイリーノート: /path/to/daily_note.md" in captured.out
    assert "-> 処理完了" in captured.out

@patch("src.daily_manager.get_daily_note_path")
def test_process_evening(mock_get_path, capsys):
    """evening 処理のテスト"""
    mock_get_path.return_value = "/path/to/daily_note.md"
    process_evening()
    captured = capsys.readouterr()
    assert "夕方の処理 (evening) を開始します..." in captured.out
    assert "対象デイリーノート: /path/to/daily_note.md" in captured.out
    assert "-> 処理完了" in captured.out

@patch("src.daily_manager.get_daily_note_path")
def test_process_night(mock_get_path, capsys):
    """night 処理のテスト"""
    mock_get_path.return_value = "/path/to/daily_note.md"
    process_night()
    captured = capsys.readouterr()
    assert "夜の処理 (night) を開始します..." in captured.out
    assert "対象デイリーノート: /path/to/daily_note.md" in captured.out
    assert "-> 処理完了" in captured.out

@patch("src.daily_manager.process_morning")
@patch("sys.argv", ["daily_manager.py", "morning"])
def test_main_morning(mock_process_morning):
    """main() で morning が指定された場合のテスト"""
    main()
    mock_process_morning.assert_called_once()

@patch("src.daily_manager.process_evening")
@patch("sys.argv", ["daily_manager.py", "evening"])
def test_main_evening(mock_process_evening):
    """main() で evening が指定された場合のテスト"""
    main()
    mock_process_evening.assert_called_once()

@patch("src.daily_manager.process_night")
@patch("sys.argv", ["daily_manager.py", "night"])
def test_main_night(mock_process_night):
    """main() で night が指定された場合のテスト"""
    main()
    mock_process_night.assert_called_once()

@patch("sys.argv", ["daily_manager.py", "morning"])
@patch("src.daily_manager.process_morning", side_effect=Exception("Test Error"))
def test_main_exception(mock_process, capsys):
    """main() 実行中に予期せぬエラーが発生した場合のテスト"""
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "予期せぬエラーが発生しました: Test Error" in captured.err
