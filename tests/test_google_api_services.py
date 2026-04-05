import pytest
from unittest.mock import patch, MagicMock

from src.google_api_services import get_calendar_events, get_tasks

@patch("src.google_api_services.get_credentials")
@patch("src.google_api_services.build")
def test_get_calendar_events(mock_build, mock_get_credentials):
    # Mocking Calendar API
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_list = MagicMock()
    mock_execute = MagicMock()
    
    mock_build.return_value = mock_service
    mock_service.events.return_value = mock_events
    mock_events.list.return_value = mock_list
    mock_list.execute.return_value = {'items': [{'summary': 'Test Event'}]}
    
    events = get_calendar_events()
    
    assert len(events) == 1
    assert events[0]['summary'] == 'Test Event'
    mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_get_credentials.return_value)
    mock_service.events().list.assert_called_once()

@patch("src.google_api_services.get_credentials")
@patch("src.google_api_services.build")
def test_get_tasks(mock_build, mock_get_credentials):
    # Mocking Tasks API
    mock_service = MagicMock()
    mock_tasks = MagicMock()
    mock_list = MagicMock()
    mock_execute = MagicMock()
    
    mock_build.return_value = mock_service
    mock_service.tasks.return_value = mock_tasks
    mock_tasks.list.return_value = mock_list
    mock_list.execute.return_value = {'items': [{'title': 'Test Task'}]}
    
    tasks = get_tasks()
    
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Test Task'
    mock_build.assert_called_once_with('tasks', 'v1', credentials=mock_get_credentials.return_value)
    mock_service.tasks().list.assert_called_once()
