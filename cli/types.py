from typing import Protocol, Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from alexa_auth.alexa_auth import AlexaAuth
    from core.device_manager import DeviceManager
    from services.sync_service import SyncService
    from services.voice_command_service import VoiceCommandService
    from core.state_machine import AlexaStateMachine
    from core.config import Config
    from services.cache_service import CacheService


class ContextProtocol(Protocol):
    """Minimal Protocol describing the Context interface used by commands.

    Keep this intentionally small; add attributes here as needed to reduce
    a large number of mypy `union-attr` errors caused by lazy-loaded
    Optional attributes on the concrete Context class.
    """

    config: "Config"
    auth: Optional["AlexaAuth"]
    state_machine: "AlexaStateMachine"
    cache_service: "CacheService"

    # Common lazy-loaded resources used widely by commands
    breaker: object

    # Many resources in the concrete Context are exposed as @property
    # (read-only). Declare them as properties in the Protocol so structural
    # subtyping matches and mypy does not complain about settable vs read-only.
    @property
    def device_mgr(self) -> Optional["DeviceManager"]: ...

    @property
    def sync_service(self) -> Optional["SyncService"]: ...

    @property
    def voice_service(self) -> Optional["VoiceCommandService"]: ...

    @property
    def timer_mgr(self) -> Optional[Any]: ...

    @property
    def alarm_mgr(self) -> Optional[Any]: ...

    @property
    def reminder_mgr(self) -> Optional[Any]: ...

    @property
    def light_ctrl(self) -> Optional[Any]: ...

    @property
    def thermostat_ctrl(self) -> Optional[Any]: ...

    @property
    def smarthome_ctrl(self) -> Optional[Any]: ...

    @property
    def playback_mgr(self) -> Optional[Any]: ...

    @property
    def tunein_mgr(self) -> Optional[Any]: ...

    @property
    def library_mgr(self) -> Optional[Any]: ...

    @property
    def music_library(self) -> Optional[Any]: ...

    @property
    def notification_mgr(self) -> Optional[Any]: ...

    @property
    def dnd_mgr(self) -> Optional[Any]: ...

    @property
    def activity_mgr(self) -> Optional[Any]: ...

    @property
    def announcement_mgr(self) -> Optional[Any]: ...

    @property
    def calendar_manager(self) -> Optional[Any]: ...

    @property
    def routine_mgr(self) -> Optional[Any]: ...

    @property
    def list_mgr(self) -> Optional[Any]: ...

    # Device controller (smarthome) - concrete Context exposes this as device_ctrl
    @property
    def device_ctrl(self) -> Optional[Any]: ...

    @property
    def equalizer_mgr(self) -> Optional[Any]: ...

    @property
    def bluetooth_mgr(self) -> Optional[Any]: ...

    @property
    def device_settings_mgr(self) -> Optional[Any]: ...

    @property
    def settings_mgr(self) -> Optional[Any]: ...

    @property
    def multiroom_mgr(self) -> Optional[Any]: ...

    # Keep extensible: commands can rely on these attributes being present
    # at type-check time (they may still be None at runtime before auth).

    # Fallback generic attribute access
    def __getattr__(self, name: str) -> Any: ...

