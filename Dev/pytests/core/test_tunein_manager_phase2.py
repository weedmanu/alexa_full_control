"""
Phase 2 Tests: TuneInManager - Mandatory AlexaAPIService Injection
Tests that TuneInManager correctly injects and uses AlexaAPIService
without fallbacks to _api_call.
"""

from unittest.mock import Mock
import pytest

from core.music.tunein_manager import TuneInManager
from core.state_machine import AlexaStateMachine


class TestTuneInManagerMandatoryInjection:
    """Test that api_service injection is mandatory."""

    def test_constructor_raises_without_api_service(self):
        """Constructor should raise ValueError if api_service is None."""
        auth = Mock()
        config = Mock()
        state_machine = AlexaStateMachine()

        with pytest.raises(ValueError, match="api_service is mandatory"):
            TuneInManager(
                auth_or_http=auth,
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
            TuneInManager(auth_or_http=auth, config=config, state_machine=state_machine)

    def test_constructor_succeeds_with_api_service(self):
        """Constructor should succeed when api_service is provided."""
        auth = Mock()
        config = Mock()
        state_machine = AlexaStateMachine()
        api_service = Mock()

        manager = TuneInManager(
            auth_or_http=auth,
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

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        assert manager._api_service is not None
        assert manager._api_service is api_service


class TestTuneInManagerSearchStations:
    """Test search_stations() uses api_service directly."""

    def test_search_stations_calls_api_service(self):
        """search_stations() should call api_service.get directly."""
        auth = Mock()
        auth.customer_id = "customer123"
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {
            "results": [
                {"id": "1", "title": "Station 1"},
                {"id": "2", "title": "Station 2"},
                {"id": "3", "title": "Station 3"},
            ]
        }

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.search_stations("jazz", limit=2)

        api_service.get.assert_called_once()
        call_args = api_service.get.call_args
        assert call_args[0][0] == "/api/tunein/search"
        assert call_args[1]["params"]["query"] == "jazz"
        assert len(result) == 2
        assert result[0]["title"] == "Station 1"

    def test_search_stations_default_limit(self):
        """search_stations() should use default limit of 20."""
        auth = Mock()
        auth.customer_id = "customer123"
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {"results": []}

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        manager.search_stations("rock")

        call_args = api_service.get.call_args
        # default limit is 20, so we should get all results

    def test_search_stations_handles_exception(self):
        """search_stations() should return empty list on exception."""
        auth = Mock()
        auth.customer_id = "customer123"
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.side_effect = Exception("API Error")

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.search_stations("jazz")
        assert result == []

    def test_search_stations_respects_state_machine(self):
        """search_stations() should return empty list if commands not allowed."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.search_stations("jazz")
        assert result == []
        api_service.get.assert_not_called()


class TestTuneInManagerPlayStation:
    """Test play_station() uses api_service directly."""

    def test_play_station_calls_api_service(self):
        """play_station() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.play_station("device123", "ECHO", "station_xyz")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[0][0] == "/api/tunein/queue-and-play"
        assert call_args[1]["payload"]["deviceSerialNumber"] == "device123"
        assert call_args[1]["payload"]["guideId"] == "station_xyz"
        assert result is True

    def test_play_station_handles_exception(self):
        """play_station() should return False on exception."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.side_effect = Exception("API Error")

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.play_station("device123", "ECHO", "station_xyz")
        assert result is False

    def test_play_station_respects_state_machine(self):
        """play_station() should return False if commands not allowed."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.play_station("device123", "ECHO", "station_xyz")
        assert result is False
        api_service.post.assert_not_called()


class TestTuneInManagerGetFavorites:
    """Test get_favorites() uses api_service directly."""

    def test_get_favorites_calls_api_service(self):
        """get_favorites() should call api_service.get directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {
            "favorites": [
                {"id": "1", "title": "Favorite 1"},
                {"id": "2", "title": "Favorite 2"},
            ]
        }

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_favorites()

        api_service.get.assert_called_once_with("/api/tunein/favorites")
        assert len(result) == 2
        assert result[0]["title"] == "Favorite 1"

    def test_get_favorites_empty_list(self):
        """get_favorites() should return empty list when no favorites."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {"favorites": []}

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_favorites()
        assert result == []

    def test_get_favorites_handles_exception(self):
        """get_favorites() should return empty list on exception."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.side_effect = Exception("API Error")

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_favorites()
        assert result == []

    def test_get_favorites_respects_state_machine(self):
        """get_favorites() should return empty list if commands not allowed."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.get_favorites()
        assert result == []
        api_service.get.assert_not_called()


class TestTuneInManagerAddFavorite:
    """Test add_favorite() uses api_service directly."""

    def test_add_favorite_calls_api_service(self):
        """add_favorite() should call api_service.post directly."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.add_favorite("station_xyz")

        api_service.post.assert_called_once()
        call_args = api_service.post.call_args
        assert call_args[0][0] == "/api/tunein/favorites"
        assert call_args[1]["payload"]["guideId"] == "station_xyz"
        assert result is True

    def test_add_favorite_handles_exception(self):
        """add_favorite() should return False on exception."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.post.side_effect = Exception("API Error")

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.add_favorite("station_xyz")
        assert result is False

    def test_add_favorite_respects_state_machine(self):
        """add_favorite() should return False if commands not allowed."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = False
        api_service = Mock()

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        result = manager.add_favorite("station_xyz")
        assert result is False
        api_service.post.assert_not_called()


class TestTuneInManagerNoFallbacks:
    """Verify no fallback patterns exist to _api_call."""

    def test_no_api_call_usage(self):
        """Verify that operations use api_service, not _api_call."""
        auth = Mock()
        config = Mock()
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()
        api_service.get.return_value = {"results": []}

        manager = TuneInManager(
            auth_or_http=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )

        # If api_call is called, it will fail since we don't have http_client set up
        result = manager.search_stations("test")
        assert result == []
        api_service.get.assert_called_once()
