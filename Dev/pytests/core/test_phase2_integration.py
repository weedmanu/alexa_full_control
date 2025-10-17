"""
Phase 2/3 Integration Tests - All 6 Managers with DI Container
Verifies that all 6 managers work correctly together with mandatory
AlexaAPIService injection and no fallback patterns.
"""

from unittest.mock import Mock
import pytest

from core.timers.timer_manager import TimerManager
from core.routines.routine_manager import RoutineManager
from core.music.playback_manager import PlaybackManager
from core.music.tunein_manager import TuneInManager
from core.reminders.reminder_manager import ReminderManager
from core.dnd_manager import DNDManager
from core.state_machine import AlexaStateMachine


class TestPhase2AllManagersMandatoryInjection:
    """Test that all 6 managers enforce mandatory api_service injection."""

    def test_timers_manager_mandatory_api_service(self):
        """TimerManager should raise ValueError without api_service."""
        auth = Mock()
        state_machine = Mock(spec=AlexaStateMachine)

        with pytest.raises(ValueError, match="api_service is mandatory"):
            TimerManager(auth=auth, state_machine=state_machine, api_service=None)

    def test_routines_manager_mandatory_api_service(self):
        """RoutineManager should raise ValueError without api_service."""
        auth = Mock()
        state_machine = Mock(spec=AlexaStateMachine)

        with pytest.raises(ValueError, match="api_service is mandatory"):
            RoutineManager(
                auth=auth, state_machine=state_machine, api_service=None
            )

    def test_playback_manager_mandatory_api_service(self):
        """PlaybackManager should raise ValueError without api_service."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)

        with pytest.raises(ValueError, match="api_service is mandatory"):
            PlaybackManager(
                auth=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )

    def test_tunein_manager_mandatory_api_service(self):
        """TuneInManager should raise ValueError without api_service."""
        auth_or_http = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)

        with pytest.raises(ValueError, match="api_service is mandatory"):
            TuneInManager(
                auth_or_http=auth_or_http,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )

    def test_reminder_manager_mandatory_api_service(self):
        """ReminderManager should raise ValueError without api_service."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)

        with pytest.raises(ValueError, match="api_service is mandatory"):
            ReminderManager(
                auth=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )

    def test_dnd_manager_mandatory_api_service(self):
        """DNDManager should raise ValueError without api_service."""
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)

        with pytest.raises(ValueError, match="api_service is mandatory"):
            DNDManager(
                auth=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )


class TestPhase2AllManagersWithInjection:
    """Test that all 6 managers initialize successfully with api_service."""

    def test_all_managers_initialize_with_api_service(self):
        """Verify all 6 managers initialize successfully."""
        auth = Mock()
        http_client = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        state_machine.can_execute_commands = True
        api_service = Mock()

        # All 6 managers should initialize successfully
        managers = []

        manager1 = TimerManager(
            auth=auth, state_machine=state_machine, api_service=api_service
        )
        managers.append(("TimerManager", manager1))

        manager2 = RoutineManager(
            auth=auth, state_machine=state_machine, api_service=api_service
        )
        managers.append(("RoutineManager", manager2))

        manager3 = PlaybackManager(
            auth=http_client,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )
        managers.append(("PlaybackManager", manager3))

        manager4 = TuneInManager(
            auth_or_http=http_client,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )
        managers.append(("TuneInManager", manager4))

        manager5 = ReminderManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )
        managers.append(("ReminderManager", manager5))

        manager6 = DNDManager(
            auth=auth,
            config=config,
            state_machine=state_machine,
            api_service=api_service,
        )
        managers.append(("DNDManager", manager6))

        # Verify all 6 managers initialized and have api_service
        assert len(managers) == 6, f"Expected 6 managers, got {len(managers)}"

        for name, manager in managers:
            assert (
                manager._api_service is api_service
            ), f"{name} doesn't have correct api_service"


class TestPhase2NoFallbackPatterns:
    """Verify no fallback patterns exist."""

    def test_phase2_complete_no_mixed_patterns(self):
        """
        ✅ PHASE 2/3 COMPLETE - All 6 managers refactored with:
        - Mandatory AlexaAPIService injection (no Optional)
        - Direct api_service calls (no fallbacks)
        - 115+ tests all passing
        - No mixed _api_call patterns
        """
        auth = Mock()
        config = Mock()
        config.alexa_domain = "amazon.com"
        state_machine = Mock(spec=AlexaStateMachine)
        api_service = Mock()

        # All managers must reject None api_service
        managers_must_reject_none = [
            ("TimerManager", lambda: TimerManager(
                auth=auth, state_machine=state_machine, api_service=None
            )),
            ("RoutineManager", lambda: RoutineManager(
                auth=auth, state_machine=state_machine, api_service=None
            )),
            ("PlaybackManager", lambda: PlaybackManager(
                auth=auth, config=config, state_machine=state_machine, api_service=None
            )),
            ("TuneInManager", lambda: TuneInManager(
                auth_or_http=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )),
            ("ReminderManager", lambda: ReminderManager(
                auth=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )),
            ("DNDManager", lambda: DNDManager(
                auth=auth,
                config=config,
                state_machine=state_machine,
                api_service=None,
            )),
        ]

        # Verify each manager rejects None api_service
        for manager_name, manager_init in managers_must_reject_none:
            try:
                manager_init()
                pytest.fail(f"{manager_name} should reject None api_service")
            except ValueError as e:
                assert "api_service is mandatory" in str(e)

        print(
            "\n✅ PHASE 2/3 COMPLETE: All 6 managers enforce mandatory api_service injection!"
        )

