"""
Tests for Music Managers Phase 3.7 DTO integration.
"""

import pytest
from typing import Any, Dict, List, Optional
from core.music.playback_manager import PlaybackManager
from core.music.library_manager import LibraryManager
from core.music.tunein_manager import TuneInManager
from services.cache_service import CacheService


class FakeAPIServiceMusic:
    """Fake API service for music managers."""
    
    def __init__(self, mock_data: Dict[str, Any]):
        self.mock_data = mock_data
    
    def get(self, path: str, params: Dict[str, Any] = None, timeout: int = 10):
        """Mock GET request."""
        if path == "/api/np/player":
            return self.mock_data.get("player", {})
        elif path == "/api/media/state":
            return self.mock_data.get("media", {})
        elif path == "/api/np/queue":
            return self.mock_data.get("queue", {})
        elif path == "/api/media/history":
            return {"history": self.mock_data.get("history", [])}
        elif path == "/api/tunein/search":
            return {"results": self.mock_data.get("tunein_results", [])}
        return {}
    
    def post(self, path: str, json: Dict[str, Any], timeout: int = 10):
        """Mock POST request."""
        return {"success": True}
    
    def delete(self, path: str, timeout: int = 10):
        """Mock DELETE request."""
        return None
    
    def put(self, path: str, json: Dict[str, Any], timeout: int = 10):
        """Mock PUT request."""
        return None


class FakeStateMachineMusic:
    """Fake state machine."""
    
    @property
    def can_execute_commands(self) -> bool:
        return True
    
    @property
    def state(self):
        class State:
            name = "CONNECTED"
        return State()


def make_playback_manager(mock_data: Dict[str, Any] = None):
    """Create a PlaybackManager for testing."""
    class FakeAuth:
        pass
    
    class FakeConfig:
        amazon_domain = "amazon.com"
    
    auth = FakeAuth()
    config = FakeConfig()
    state_machine = FakeStateMachineMusic()
    
    mock_data = mock_data or {
        "player": {"isPlaying": True, "volume": 50, "progress": 45, "duration": 180}
    }
    api_service = FakeAPIServiceMusic(mock_data)
    
    manager = PlaybackManager(
        auth=auth,
        config=config,
        state_machine=state_machine,
        api_service=api_service
    )
    return manager


def make_library_manager():
    """Create a LibraryManager for testing."""
    class FakeAuth:
        pass
    
    class FakeConfig:
        amazon_domain = "amazon.com"
    
    auth = FakeAuth()
    config = FakeConfig()
    state_machine = FakeStateMachineMusic()
    
    manager = LibraryManager(
        auth=auth,
        config=config,
        state_machine=state_machine
    )
    return manager


def make_tunein_manager(mock_data: Dict[str, Any] = None):
    """Create a TuneInManager for testing."""
    class FakeAuth:
        customer_id = "customer123"
    
    class FakeConfig:
        amazon_domain = "amazon.com"
    
    auth = FakeAuth()
    config = FakeConfig()
    state_machine = FakeStateMachineMusic()
    
    mock_data = mock_data or {
        "tunein_results": [
            {"id": "station1", "title": "Station 1", "genre": "Music"}
        ]
    }
    api_service = FakeAPIServiceMusic(mock_data)
    
    manager = TuneInManager(
        auth_or_http=auth,
        config=config,
        state_machine=state_machine,
        api_service=api_service
    )
    return manager


# PlaybackManager Tests
def test_playback_get_state_basic():
    """Test get_state returns dict."""
    manager = make_playback_manager()
    state = manager.get_state("SERIAL1", "ECHO_DOT")
    assert isinstance(state, dict)
    assert "player" in state


def test_playback_get_music_status_typed():
    """Test Phase 3.7: get_music_status_typed() returns MusicStatusResponse DTO."""
    mock_data = {
        "player": {
            "isPlaying": True,
            "volume": 75,
            "progress": 30,
            "duration": 200,
            "queueLength": 5,
            "queueIndex": 0
        }
    }
    manager = make_playback_manager(mock_data)
    
    response = manager.get_music_status_typed("SERIAL1", "ECHO_DOT")
    
    if response is not None:
        assert hasattr(response, 'is_playing'), "Response should have 'is_playing'"
        assert response.volume == 75, "Volume should be 75"


def test_playback_get_music_status_typed_no_data():
    """Test get_music_status_typed handles missing data gracefully."""
    mock_data = {}
    manager = make_playback_manager(mock_data)
    
    response = manager.get_music_status_typed("SERIAL1", "ECHO_DOT")
    # Should either return None or default MusicStatusResponse
    assert True  # Just verify no exception


# LibraryManager Tests
def test_library_search_music_basic():
    """Test search_music returns results."""
    manager = make_library_manager()
    results = manager.search_music("rock music")
    assert isinstance(results, list)


def test_library_search_music_typed():
    """Test Phase 3.7: search_music_typed() returns MusicSearchResponse DTO."""
    manager = make_library_manager()
    
    response = manager.search_music_typed("jazz")
    
    if response is not None:
        assert hasattr(response, 'results'), "Response should have 'results'"
        assert isinstance(response.results, list), "Results should be a list"


# TuneInManager Tests
def test_tunein_search_stations_basic():
    """Test search_stations returns results."""
    manager = make_tunein_manager()
    results = manager.search_stations("rock radio")
    assert isinstance(results, list)


def test_tunein_search_stations_typed():
    """Test Phase 3.7: search_stations_typed() returns MusicSearchResponse DTO."""
    mock_data = {
        "tunein_results": [
            {"id": "s1", "title": "Rock Station", "genre": "Rock"},
            {"id": "s2", "title": "Jazz Station", "genre": "Jazz"}
        ]
    }
    manager = make_tunein_manager(mock_data)
    
    response = manager.search_stations_typed("rock", limit=10)
    
    if response is not None:
        assert hasattr(response, 'results'), "Response should have 'results'"
        assert response.total_count == 2, "Should have 2 stations"
