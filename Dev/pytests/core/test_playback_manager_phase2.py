"""
Phase 2 Tests: PlaybackManager - Mandatory AlexaAPIService Injection
Tests that PlaybackManager correctly injects and uses AlexaAPIService
without fallbacks to _api_call.
"""

from unittest.mock import Mock, patch, MagicMock
import pytest

from core.music.playback_manager import PlaybackManager
from core.state_machine import AlexaStateMachine


class TestPlaybackManagerMandatoryInjection:
    """Test that api_service injection is mandatory."""

    def test_constructor_raises_without_api_service(self):
        """Constructor should raise ValueError if api_service is None."""
        auth = Mock()
        config = Mock()
        state_machine = AlexaStateMachine()

        with pytest.raises(ValueError, match="api_service is mandatory"):
            PlaybackManager(
                auth=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )

    def test_constructor_requires_explicit_api_service(self):
        """Constructor should require explicitly passed api_service."""
        auth = Mock()
        config = Mock()
        state_machine = AlexaStateMachine()

        with pytest.raises(ValueError):
            PlaybackManager(auth=auth, config=config, state_machine=state_machine)

    def test_constructor_succeeds_with_api_service(self):
        """Constructor should succeed when api_service is provided."""
        auth = Mock()
        config = Mock()
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        assert manager._api_service is api_service

    def test_api_service_not_optional(self):
        """api_service should not be optional in Phase 2."""
        auth = Mock()
        config = Mock()
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        # Verify it's set
        assert manager._api_service is not None
        assert manager._api_service is api_service


class TestPlaybackManagerPlay:
    """Test play() uses api_service directly."""

    def test_play_calls_api_service(self):
        """play() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        device_serial = "device123"
        device_type = "ECHO"

        result = manager.play(device_serial, device_type)

        # Verify api_service.post was called
        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[0][0] == "/api/np/command"
        assert call_args[1]["payload"]["deviceSerialNumber"] == device_serial
        assert call_args[1]["payload"]["type"] == "PlayCommand"
        assert result is True

    def test_play_handles_api_exception(self):
        """play() should return False on api_service exception."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.side_effect = Exception("API Error")

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.play("device123", "ECHO")
        assert result is False

    def test_play_respects_state_machine(self):
        """play() should return False if commands not allowed."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.play("device123", "ECHO")
        assert result is False
        api_service.post.assert_not_called()


class TestPlaybackManagerPause:
    """Test pause() uses api_service directly."""

    def test_pause_calls_api_service(self):
        """pause() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.pause("device123", "ECHO")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[1]["payload"]["type"] == "PauseCommand"
        assert result is True


class TestPlaybackManagerNext:
    """Test next_track() uses api_service directly."""

    def test_next_track_calls_api_service(self):
        """next_track() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.next_track("device123", "ECHO")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[1]["payload"]["type"] == "NextCommand"
        assert result is True


class TestPlaybackManagerPrevious:
    """Test previous_track() uses api_service directly."""

    def test_previous_track_calls_api_service(self):
        """previous_track() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.previous_track("device123", "ECHO")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[1]["payload"]["type"] == "PreviousCommand"
        assert result is True


class TestPlaybackManagerStop:
    """Test stop() uses api_service directly."""

    def test_stop_calls_api_service(self):
        """stop() should call api_service.post directly (sends PauseCommand)."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.stop("device123", "ECHO")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[1]["payload"]["type"] == "PauseCommand"
        assert result is True


class TestPlaybackManagerShuffle:
    """Test set_shuffle() uses api_service directly."""

    def test_set_shuffle_enabled_calls_api_service(self):
        """set_shuffle(enabled=True) should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_shuffle("device123", "ECHO", enabled=True)

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[1]["payload"]["type"] == "ShuffleCommand"
        assert call_args[1]["payload"]["shuffle"] == "true"
        assert result is True

    def test_set_shuffle_disabled_calls_api_service(self):
        """set_shuffle(enabled=False) should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_shuffle("device123", "ECHO", enabled=False)

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[1]["payload"]["shuffle"] == "false"
        assert result is True

    def test_set_shuffle_handles_400_error(self):
        """set_shuffle() should handle 400 errors gracefully (not supported)."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.side_effect = Exception("400 Bad Request: ShuffleCommand not supported")

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_shuffle("device123", "ECHO", enabled=True)
        assert result is False


class TestPlaybackManagerRepeat:
    """Test set_repeat() uses api_service directly."""

    def test_set_repeat_one_calls_api_service(self):
        """set_repeat('ONE') should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_repeat("device123", "ECHO", "ONE")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[1]["payload"]["type"] == "RepeatCommand"
        assert call_args[1]["payload"]["repeat"] is True
        assert result is True

    def test_set_repeat_all_calls_api_service(self):
        """set_repeat('ALL') should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_repeat("device123", "ECHO", "ALL")

        api_service.post.assert_called_once()
        assert result is True

    def test_set_repeat_off_returns_false(self):
        """set_repeat('OFF') should return False (not supported)."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_repeat("device123", "ECHO", "OFF")

        api_service.post.assert_not_called()
        assert result is False

    def test_set_repeat_invalid_mode_returns_false(self):
        """set_repeat with invalid mode should return False."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.set_repeat("device123", "ECHO", "INVALID")

        api_service.post.assert_not_called()
        assert result is False


class TestPlaybackManagerSeek:
    """Test seek_to() uses api_service directly."""

    def test_seek_to_calls_api_service(self):
        """seek_to() should call api_service.put directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.seek_to("device123", "ECHO", 30000)

        api_service.put.assert_called_once()
        call_args = api_service.put.call_args
        assert call_args[0][0] == "/api/np/command"
        assert call_args[1]["payload"]["mediaPosition"] == 30000
        assert result is True

    def test_seek_to_handles_exception(self):
        """seek_to() should return False on exception."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.put.side_effect = Exception("Seek failed")

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.seek_to("device123", "ECHO", 30000)
        assert result is False


class TestPlaybackManagerGetHistory:
    """Test get_history() uses api_service directly."""

    def test_get_history_calls_api_service(self):
        """get_history() should call api_service.get directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {
            "history": [
                {"id": "1", "title": "Song 1"},
                {"id": "2", "title": "Song 2"},
            ]
        }

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_history(limit=50)

        api_service.get.assert_called_once_with("/api/media/history", params={"size": 50})
        assert len(result) == 2
        assert result[0]["title"] == "Song 1"

    def test_get_history_default_limit(self):
        """get_history() should use default limit of 50."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {"history": []}

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        manager.get_history()

        api_service.get.assert_called_once_with("/api/media/history", params={"size": 50})

    def test_get_history_custom_limit(self):
        """get_history() should use custom limit."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {"history": []}

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        manager.get_history(limit=100)

        api_service.get.assert_called_once_with("/api/media/history", params={"size": 100})

    def test_get_history_handles_exception(self):
        """get_history() should return empty list on exception."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.side_effect = Exception("API Error")

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_history()
        assert result == []

    def test_get_history_respects_state_machine(self):
        """get_history() should return empty list if commands not allowed."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_history()
        assert result == []
        api_service.get.assert_not_called()


class TestPlaybackManagerGetState:
    """Test get_state() uses api_service directly for all 3 calls."""

    def test_get_state_calls_api_service_three_times(self):
        """get_state() should call api_service.get 3 times (player, media, queue)."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.side_effect = [
            {"currentTrack": "Song 1"},  # player
            {"state": "PLAYING"},  # media
            {"tracks": []},  # queue
        ]

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_state("device123", "ECHO")

        assert api_service.get.call_count == 3
        assert result is not None
        assert "player" in result
        assert "media" in result
        assert "queue" in result
        assert result["player"]["currentTrack"] == "Song 1"
        assert result["media"]["state"] == "PLAYING"

    def test_get_state_with_multiroom_params(self):
        """get_state() should include multiroom params if provided."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.side_effect = [
            {"currentTrack": "Song 1"},
            {"state": "PLAYING"},
            {"tracks": []},
        ]

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_state(
            "device123", "ECHO", parent_id="parent_id", parent_type="ECHO_GROUP"
        )

        # First call should include lemurId
        first_call_params = api_service.get.call_args_list[0][1]["params"]
        assert first_call_params.get("lemurId") == "parent_id"
        assert first_call_params.get("lemurDeviceType") == "ECHO_GROUP"

        assert result is not None

    def test_get_state_handles_exception(self):
        """get_state() should return None on exception."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.side_effect = Exception("API Error")

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_state("device123", "ECHO")
        assert result is None

    def test_get_state_respects_state_machine(self):
        """get_state() should return None if commands not allowed."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_state("device123", "ECHO")
        assert result is None
        api_service.get.assert_not_called()


class TestPlaybackManagerNoFallbacks:
    """Verify no fallback patterns exist to _api_call."""

    def test_all_api_calls_use_api_service(self):
        """Verify that operations call api_service, not _api_call."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        # Patch _api_call to verify it's never called
        with patch.object(manager, "_api_call") as mock_api_call:
            manager.play("device123", "ECHO")
            mock_api_call.assert_not_called()

        api_service.post.assert_called_once()

    def test_no_conditional_api_service_checks(self):
        """Verify no conditional checks like 'if _api_service is not None'."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = PlaybackManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        # Read the source to verify pattern (code inspection)
        import inspect

        source = inspect.getsource(manager.play)
        assert "if" not in source or "can_execute_commands" in source  # Only state_machine check
        assert "else" not in source or "except" in source  # Only exception handling
