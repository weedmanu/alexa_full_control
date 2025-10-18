"""Core modules for Alexa CLI - robust and thread-safe components."""

# Core infrastructure
from .activity_manager import ActivityManager

# Audio package
from .audio import BluetoothManager, EqualizerManager
from .circuit_breaker import CircuitBreaker, CircuitBreakerError, CircuitState

# DND Manager
from .dnd_manager import DNDManager

# Lists package
from .lists import ListsManager

# Music package
from .music import PlaybackManager, TuneInManager

# Notifications & Activity managers
from .notification_manager import NotificationManager

# Settings package
from .settings import DeviceSettingsManager

# Smart Home package
from .smart_home import LightController, SmartDeviceController, ThermostatController
from .state_machine import AlexaStateMachine, ConnectionState, StateTransitionError

# Timers package
from .alarms import AlarmManager
from .reminders import ReminderManager
from .timers import TimerManager

__all__ = [
    # Core infrastructure
    "AlexaStateMachine",
    "ConnectionState",
    "StateTransitionError",
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitState",
    # Notifications & Activity
    "NotificationManager",
    "DNDManager",
    "ActivityManager",
    # Timers
    "TimerManager",
    "AlarmManager",
    "ReminderManager",
    # Smart Home
    "LightController",
    "ThermostatController",
    "SmartDeviceController",
    # Music
    "PlaybackManager",
    "TuneInManager",
    # Lists
    "ListsManager",
    # Audio
    "EqualizerManager",
    "BluetoothManager",
    # Settings
    "DeviceSettingsManager",
]
