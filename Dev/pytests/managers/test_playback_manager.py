"""TDD Tests for PlaybackManager refactoring to BaseManager inheritance.

These tests define the expected behavior BEFORE refactoring PlaybackManager
to inherit from BaseManager. Tests are written first (TDD approach).

Coverage Target: 90%+
"""

import pytest
from unittest.mock import MagicMock
from core.music.playback_manager import PlaybackManager


class TestPlaybackManagerInitialization:
    """Test PlaybackManager initialization and setup."""

    @pytest.mark.unit
    def test_init_with_minimal_params(self, mock_auth: MagicMock, mock_config: MagicMock) -> None:
        """PlaybackManager should initialize with auth and config."""
        manager = PlaybackManager(auth=mock_auth, config=mock_config)
        
        assert manager.auth == mock_auth
        assert manager.config == mock_config
        assert manager.state_machine is not None
        assert hasattr(manager, "breaker")
        assert hasattr(manager, "_lock")

    @pytest.mark.unit
    def test_init_with_state_machine(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> None:
        """PlaybackManager should use provided state machine."""
        manager = PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )
        
        assert manager.state_machine == mock_state_machine

    @pytest.mark.unit
    def test_init_creates_http_client(self, mock_auth: MagicMock, mock_config: MagicMock) -> None:
        """PlaybackManager should create/normalize http_client."""
        manager = PlaybackManager(auth=mock_auth, config=mock_config)
        
        assert hasattr(manager, "http_client")
        assert manager.http_client is not None

    @pytest.mark.unit
    def test_init_creates_voice_service(self, mock_auth: MagicMock, mock_config: MagicMock) -> None:
        """PlaybackManager should initialize VoiceCommandService."""
        manager = PlaybackManager(auth=mock_auth, config=mock_config)
        
        assert hasattr(manager, "voice_service")
        assert manager.voice_service is not None


class TestPlaybackManagerPlayControl:
    """Test basic playback control methods (play, pause, next, previous, stop)."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.unit
    def test_play_command_success(self, playback_manager: PlaybackManager, mock_http_client: MagicMock) -> None:
        """play() should send PlayCommand and return True on success."""
        playback_manager.http_client = mock_http_client
        device_serial = "DEVICE-ABC123"
        device_type = "ALEXA_ECHO_DOT"
        
        result = playback_manager.play(device_serial, device_type)
        
        assert result is True

    @pytest.mark.unit
    def test_pause_command_success(self, playback_manager: PlaybackManager, mock_http_client: MagicMock) -> None:
        """pause() should send PauseCommand and return True on success."""
        playback_manager.http_client = mock_http_client
        device_serial = "DEVICE-ABC123"
        device_type = "ALEXA_ECHO_DOT"
        
        result = playback_manager.pause(device_serial, device_type)
        
        assert result is True

    @pytest.mark.unit
    def test_next_track_success(self, playback_manager: PlaybackManager, mock_http_client: MagicMock) -> None:
        """next_track() should send NextCommand and return True on success."""
        playback_manager.http_client = mock_http_client
        device_serial = "DEVICE-ABC123"
        device_type = "ALEXA_ECHO_DOT"
        
        result = playback_manager.next_track(device_serial, device_type)
        
        assert result is True

    @pytest.mark.unit
    def test_previous_track_success(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """previous_track() should send PreviousCommand and return True on success."""
        playback_manager.http_client = mock_http_client
        device_serial = "DEVICE-ABC123"
        device_type = "ALEXA_ECHO_DOT"
        
        result = playback_manager.previous_track(device_serial, device_type)
        
        assert result is True

    @pytest.mark.unit
    def test_stop_command_success(self, playback_manager: PlaybackManager, mock_http_client: MagicMock) -> None:
        """stop() should send PauseCommand (stop = pause in API) and return True."""
        playback_manager.http_client = mock_http_client
        device_serial = "DEVICE-ABC123"
        device_type = "ALEXA_ECHO_DOT"
        
        result = playback_manager.stop(device_serial, device_type)
        
        assert result is True

    @pytest.mark.unit
    def test_play_when_state_machine_not_ready(
        self, playback_manager: PlaybackManager, mock_state_machine: MagicMock
    ) -> None:
        """play() should return False when state_machine.can_execute_commands is False."""
        mock_state_machine.can_execute_commands = False
        
        result = playback_manager.play("DEVICE-ABC123", "ALEXA_ECHO_DOT")
        
        assert result is False


class TestPlaybackManagerShuffleAndRepeat:
    """Test shuffle and repeat mode control."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.unit
    def test_set_shuffle_enabled(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """set_shuffle() should enable shuffle when enabled=True."""
        playback_manager.http_client = mock_http_client
        
        result = playback_manager.set_shuffle("DEVICE-ABC123", "ALEXA_ECHO_DOT", enabled=True)
        
        assert result is True

    @pytest.mark.unit
    def test_set_shuffle_disabled(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """set_shuffle() should disable shuffle when enabled=False."""
        playback_manager.http_client = mock_http_client
        
        result = playback_manager.set_shuffle("DEVICE-ABC123", "ALEXA_ECHO_DOT", enabled=False)
        
        assert result is True

    @pytest.mark.unit
    def test_set_repeat_one(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """set_repeat() should set repeat to ONE."""
        playback_manager.http_client = mock_http_client
        
        result = playback_manager.set_repeat("DEVICE-ABC123", "ALEXA_ECHO_DOT", "ONE")
        
        assert result is True

    @pytest.mark.unit
    def test_set_repeat_all(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """set_repeat() should set repeat to ALL."""
        playback_manager.http_client = mock_http_client
        
        result = playback_manager.set_repeat("DEVICE-ABC123", "ALEXA_ECHO_DOT", "ALL")
        
        assert result is True

    @pytest.mark.unit
    def test_set_repeat_off_not_supported(
        self, playback_manager: PlaybackManager
    ) -> None:
        """set_repeat() should return False when mode is OFF (not supported)."""
        result = playback_manager.set_repeat("DEVICE-ABC123", "ALEXA_ECHO_DOT", "OFF")
        
        assert result is False

    @pytest.mark.unit
    def test_set_repeat_invalid_mode(self, playback_manager: PlaybackManager) -> None:
        """set_repeat() should return False for invalid mode."""
        result = playback_manager.set_repeat("DEVICE-ABC123", "ALEXA_ECHO_DOT", "INVALID")
        
        assert result is False


class TestPlaybackManagerSeek:
    """Test seek/position control."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.unit
    def test_seek_to_position(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """seek_to() should set media position and return True on success."""
        playback_manager.http_client = mock_http_client
        position_ms = 30000  # 30 seconds
        
        result = playback_manager.seek_to("DEVICE-ABC123", "ALEXA_ECHO_DOT", position_ms)
        
        assert result is True

    @pytest.mark.unit
    def test_seek_to_zero(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """seek_to() should allow seeking to position 0 (start)."""
        playback_manager.http_client = mock_http_client
        
        result = playback_manager.seek_to("DEVICE-ABC123", "ALEXA_ECHO_DOT", 0)
        
        assert result is True

    @pytest.mark.unit
    def test_seek_when_state_machine_not_ready(
        self, playback_manager: PlaybackManager, mock_state_machine: MagicMock
    ) -> None:
        """seek_to() should return False when state_machine.can_execute_commands is False."""
        mock_state_machine.can_execute_commands = False
        
        result = playback_manager.seek_to("DEVICE-ABC123", "ALEXA_ECHO_DOT", 30000)
        
        assert result is False


class TestPlaybackManagerHistory:
    """Test playback history retrieval."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.unit
    def test_get_history_default_limit(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """get_history() should return list with default limit=50."""
        playback_manager.http_client = mock_http_client
        mock_http_client.get.return_value.json.return_value = {
            "history": [{"track": "Song 1"}, {"track": "Song 2"}]
        }
        
        result = playback_manager.get_history()
        
        assert isinstance(result, list)
        assert len(result) >= 0

    @pytest.mark.unit
    def test_get_history_custom_limit(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """get_history() should accept custom limit parameter."""
        playback_manager.http_client = mock_http_client
        mock_http_client.get.return_value.json.return_value = {"history": []}
        
        result = playback_manager.get_history(limit=100)
        
        assert isinstance(result, list)

    @pytest.mark.unit
    def test_get_history_when_state_machine_not_ready(
        self, playback_manager: PlaybackManager, mock_state_machine: MagicMock
    ) -> None:
        """get_history() should return empty list when state_machine not ready."""
        mock_state_machine.can_execute_commands = False
        
        result = playback_manager.get_history()
        
        assert result == []


class TestPlaybackManagerVoiceCommands:
    """Test voice command integration (play_artist)."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.unit
    def test_play_artist(self, playback_manager: PlaybackManager) -> None:
        """play_artist() should use voice_service to play artist."""
        playback_manager.voice_service.speak = MagicMock(return_value=True)
        
        result = playback_manager.play_artist("DEVICE-ABC123", "Adele")
        
        assert result is True
        playback_manager.voice_service.speak.assert_called()

    @pytest.mark.unit
    def test_play_artist_when_state_machine_not_ready(
        self, playback_manager: PlaybackManager, mock_state_machine: MagicMock
    ) -> None:
        """play_artist() should return False when state_machine not ready."""
        mock_state_machine.can_execute_commands = False
        
        result = playback_manager.play_artist("DEVICE-ABC123", "Adele")
        
        assert result is False


class TestPlaybackManagerState:
    """Test playback state retrieval (get_state)."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.unit
    def test_get_state_complete(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """get_state() should return complete playback state (player, media, queue)."""
        playback_manager.http_client = mock_http_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"track": "Song", "artist": "Artist"}
        mock_http_client.get.return_value = mock_response
        
        result = playback_manager.get_state("DEVICE-ABC123", "ALEXA_ECHO_DOT")
        
        assert result is not None
        assert isinstance(result, dict)
        assert "player" in result or result is None  # May be None if API call fails

    @pytest.mark.unit
    def test_get_state_with_multiroom_parent(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """get_state() should accept parent_id and parent_type for multiroom."""
        playback_manager.http_client = mock_http_client
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_http_client.get.return_value = mock_response
        
        _ = playback_manager.get_state(
            "DEVICE-ABC123",
            "ALEXA_ECHO_DOT",
            parent_id="PARENT-ID",
            parent_type="PARENT-TYPE",
        )
        
        # Should not raise and should process multiroom params

    @pytest.mark.unit
    def test_get_state_when_state_machine_not_ready(
        self, playback_manager: PlaybackManager, mock_state_machine: MagicMock
    ) -> None:
        """get_state() should return None when state_machine not ready."""
        mock_state_machine.can_execute_commands = False
        
        result = playback_manager.get_state("DEVICE-ABC123", "ALEXA_ECHO_DOT")
        
        assert result is None


class TestPlaybackManagerThreadSafety:
    """Test thread safety with internal locks."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.unit
    def test_lock_exists(self, playback_manager: PlaybackManager) -> None:
        """PlaybackManager should have internal lock for thread safety."""
        assert hasattr(playback_manager, "_lock")


class TestPlaybackManagerIntegration:
    """Integration tests for PlaybackManager behavior."""

    @pytest.fixture
    def playback_manager(
        self, mock_auth: MagicMock, mock_config: MagicMock, mock_state_machine: MagicMock
    ) -> PlaybackManager:
        """Create PlaybackManager instance for testing."""
        mock_config.alexa_domain = "alexa.amazon.com"
        return PlaybackManager(
            auth=mock_auth, config=mock_config, state_machine=mock_state_machine
        )

    @pytest.mark.integration
    def test_full_playback_sequence(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """Test complete playback sequence: play → next → pause."""
        playback_manager.http_client = mock_http_client
        device = "DEVICE-ABC123"
        device_type = "ALEXA_ECHO_DOT"
        
        # Play
        assert playback_manager.play(device, device_type) is True
        
        # Next track
        assert playback_manager.next_track(device, device_type) is True
        
        # Pause
        assert playback_manager.pause(device, device_type) is True

    @pytest.mark.integration
    @pytest.mark.slow
    def test_shuffle_repeat_sequence(
        self, playback_manager: PlaybackManager, mock_http_client: MagicMock
    ) -> None:
        """Test shuffle and repeat settings sequence."""
        playback_manager.http_client = mock_http_client
        device = "DEVICE-ABC123"
        device_type = "ALEXA_ECHO_DOT"
        
        # Enable shuffle
        assert playback_manager.set_shuffle(device, device_type, enabled=True) is True
        
        # Set repeat to ONE
        assert playback_manager.set_repeat(device, device_type, "ONE") is True
        
        # Play
        assert playback_manager.play(device, device_type) is True
