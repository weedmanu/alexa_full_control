"""
ManagerFactory - Factory pattern for centralized manager instantiation.

Provides a registry-based approach to creating and configuring manager instances
with standardized dependencies and configuration.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from loguru import logger


@dataclass
class ManagerConfig:
    """Configuration for a manager to be created by the factory."""

    name: str
    """Unique name for the manager (e.g., 'playback_manager')."""

    manager_class: Callable[..., Any]
    """The manager class or factory function to instantiate."""

    dependencies: Dict[str, str] = field(default_factory=dict)
    """Mapping of parameter names to dependency names (e.g., {'auth': 'auth', 'config': 'config'})."""

    cache_ttl: int = 60
    """Cache time-to-live in seconds for the manager."""

    optional_params: Dict[str, str] = field(default_factory=dict)
    """Optional parameters that may be injected if available."""

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not isinstance(self.name, str):
            raise TypeError(f"ManagerConfig.name must be str, got {type(self.name)}")
        if not callable(self.manager_class):
            raise TypeError(f"ManagerConfig.manager_class must be callable, got {type(self.manager_class)}")
        if not isinstance(self.dependencies, dict):
            raise TypeError(f"ManagerConfig.dependencies must be dict, got {type(self.dependencies)}")
        if not isinstance(self.cache_ttl, int) or self.cache_ttl <= 0:
            raise ValueError(f"ManagerConfig.cache_ttl must be positive int, got {self.cache_ttl}")


class ManagerFactory:
    """Factory for creating and managing manager instances."""

    def __init__(self) -> None:
        """Initialize the factory with default manager configurations."""
        self._configs: Dict[str, ManagerConfig] = {}
        self._instances: Dict[str, Any] = {}
        self._load_default_configs()

    def _load_default_configs(self) -> None:
        """Load default configurations for standard managers."""
        # Import here to avoid circular imports
        try:
            from core.alarms.alarm_manager import AlarmManager
            from core.audio.bluetooth_manager import BluetoothManager
            from core.audio.equalizer_manager import EqualizerManager
            from core.device_manager import DeviceManager
            from core.lists.lists_manager import ListsManager
            from core.music.library_manager import LibraryManager
            from core.music.playback_manager import PlaybackManager
            from core.reminders.reminder_manager import ReminderManager
            from core.music.tunein_manager import TuneInManager
            from core.routines.routine_manager import RoutineManager
            from core.settings.device_settings_manager import DeviceSettingsManager

            # Register standard managers
            self.register(
                ManagerConfig(
                    name="playback_manager",
                    manager_class=PlaybackManager,
                    dependencies={"auth": "auth", "config": "config", "state_machine": "state_machine"},
                    optional_params={"api_service": "alexa_api_service"},
                    cache_ttl=60,
                )
            )

            self.register(
                ManagerConfig(
                    name="routine_manager",
                    manager_class=RoutineManager,
                    dependencies={"auth": "auth", "config": "config", "state_machine": "state_machine"},
                    cache_ttl=300,
                )
            )

            self.register(
                ManagerConfig(
                    name="device_manager",
                    manager_class=DeviceManager,
                    dependencies={"auth": "auth", "config": "config"},
                    optional_params={"api_service": "alexa_api_service"},
                    cache_ttl=600,
                )
            )

            # Reminder manager (batch1)
            self.register(
                ManagerConfig(
                    name="reminder_manager",
                    manager_class=ReminderManager,
                    dependencies={"auth": "auth", "config": "config", "state_machine": "state_machine"},
                    optional_params={"api_service": "alexa_api_service"},
                    cache_ttl=60,
                )
            )

            self.register(
                ManagerConfig(
                    name="alarm_manager",
                    manager_class=AlarmManager,
                    dependencies={"auth": "auth", "config": "config"},
                    cache_ttl=300,
                )
            )

            self.register(
                ManagerConfig(
                    name="library_manager",
                    manager_class=LibraryManager,
                    dependencies={"auth": "auth", "config": "config"},
                    optional_params={"voice_service": "voice_service"},
                )
            )

            self.register(
                ManagerConfig(
                    name="tunein_manager",
                    manager_class=TuneInManager,
                    dependencies={"auth": "auth", "config": "config"},
                    cache_ttl=300,
                )
            )

            self.register(
                ManagerConfig(
                    name="lists_manager",
                    manager_class=ListsManager,
                    dependencies={"auth": "auth", "config": "config"},
                    optional_params={"voice_service": "voice_service"},
                )
            )

            self.register(
                ManagerConfig(
                    name="bluetooth_manager",
                    manager_class=BluetoothManager,
                    dependencies={"auth": "auth", "config": "config"},
                    cache_ttl=300,
                )
            )

            self.register(
                ManagerConfig(
                    name="equalizer_manager",
                    manager_class=EqualizerManager,
                    dependencies={"auth": "auth", "config": "config"},
                    cache_ttl=300,
                )
            )

            self.register(
                ManagerConfig(
                    name="device_settings_manager",
                    manager_class=DeviceSettingsManager,
                    dependencies={"auth": "auth", "config": "config"},
                    cache_ttl=300,
                )
            )

            logger.info(f"✅ Loaded {len(self._configs)} default manager configurations")

        except ImportError as e:
            logger.warning(f"⚠️ Could not load all default manager configs: {e}")

    def register(self, config: ManagerConfig) -> None:
        """
        Register a manager configuration.

        Args:
            config: ManagerConfig instance to register
        """
        if not isinstance(config, ManagerConfig):
            raise TypeError(f"Expected ManagerConfig, got {type(config)}")

        self._configs[config.name] = config
        logger.debug(f"Registered manager config: {config.name}")

    def get_registered_names(self) -> List[str]:
        """
        Get list of all registered manager names.

        Returns:
            List of manager names
        """
        return list(self._configs.keys())

    def get_config(self, name: str) -> ManagerConfig:
        """
        Get a manager configuration by name.

        Args:
            name: Manager name

        Returns:
            ManagerConfig instance

        Raises:
            ValueError: If manager not registered
        """
        if name not in self._configs:
            raise ValueError(f"Manager '{name}' not registered. Available: {self.get_registered_names()}")

        return self._configs[name]

    def get_all_configs(self) -> Dict[str, ManagerConfig]:
        """
        Get all registered manager configurations.

        Returns:
            Dictionary mapping names to ManagerConfigs
        """
        return dict(self._configs)

    def create(self, name: str, dependencies: Dict[str, Any]) -> Any:
        """
        Create a manager instance.

        Args:
            name: Manager name
            dependencies: Dictionary of resolved dependencies

        Returns:
            Manager instance

        Raises:
            ValueError: If manager not registered or dependencies missing
            TypeError: If dependency injection fails
        """
        config = self.get_config(name)

        # Validate required dependencies
        missing_deps = set(config.dependencies.values()) - set(dependencies.keys())
        if missing_deps:
            raise ValueError(
                f"Missing dependencies for '{name}': {missing_deps}. "
                f"Provided: {list(dependencies.keys())}"
            )

        # Build kwargs for manager initialization
        kwargs: Dict[str, Any] = {}

        # Add required dependencies
        for param_name, dep_name in config.dependencies.items():
            if dep_name in dependencies:
                kwargs[param_name] = dependencies[dep_name]

        # Add optional parameters if available
        for param_name, dep_name in config.optional_params.items():
            if dep_name in dependencies:
                kwargs[param_name] = dependencies[dep_name]

        # Add cache_ttl if supported
        if "cache_ttl" in config.__dict__:
            # Some managers may support cache_ttl parameter
            try:
                instance = config.manager_class(**kwargs, cache_ttl=config.cache_ttl)
            except TypeError:
                # Manager doesn't support cache_ttl, create without it
                instance = config.manager_class(**kwargs)
        else:
            instance = config.manager_class(**kwargs)

        logger.debug(f"Created manager instance: {name}")
        return instance

    def create_all(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create all registered manager instances.

        Args:
            dependencies: Dictionary of resolved dependencies

        Returns:
            Dictionary mapping manager names to instances
        """
        instances: Dict[str, Any] = {}

        for name in self.get_registered_names():
            try:
                instances[name] = self.create(name, dependencies)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to create manager '{name}': {e}")

        return instances
