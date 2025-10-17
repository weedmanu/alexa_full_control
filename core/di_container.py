"""
DI Container - Dependency Injection container for the Alexa application.

Manages all dependencies and provides centralized instance resolution
for managers, services, and components.
"""

from typing import Any, Dict, Optional, TypeVar

from loguru import logger

from alexa_auth.alexa_auth import AlexaAuth
from core.config import Config
from core.manager_factory import ManagerFactory
from core.multiroom.multiroom_manager import MultiRoomManager
from core.state_machine import AlexaStateMachine
from services.favorite_service import FavoriteService

T = TypeVar("T")


class DIContainer:
    """Centralized dependency injection container."""

    def __init__(self) -> None:
        """Initialize the DI container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Any] = {}
        self._manager_factory: Optional[ManagerFactory] = None

    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton instance.

        Args:
            name: Name for the dependency
            instance: The singleton instance
        """
        self._singletons[name] = instance
        logger.debug(f"Registered singleton: {name}")

    def register_factory(self, name: str, factory_func: Any) -> None:
        """
        Register a factory function for lazy creation.

        Args:
            name: Name for the dependency
            factory_func: Callable that creates instances
        """
        self._factories[name] = factory_func
        logger.debug(f"Registered factory: {name}")

    def get(self, name: str) -> Any:
        """
        Get a dependency instance.

        Args:
            name: Dependency name

        Returns:
            The dependency instance

        Raises:
            KeyError: If dependency not registered
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]

        # Check factories
        if name in self._factories:
            factory = self._factories[name]
            instance = factory()
            self._singletons[name] = instance  # Cache as singleton after first creation
            return instance

        raise KeyError(f"Dependency '{name}' not registered")

    def has(self, name: str) -> bool:
        """Check if dependency is registered."""
        return name in self._singletons or name in self._factories

    def resolve_dependencies(self, dependencies: Dict[str, str]) -> Dict[str, Any]:
        """
        Resolve a dictionary of dependency names to instances.

        Args:
            dependencies: Dict mapping param names to dependency names

        Returns:
            Dict mapping param names to resolved instances
        """
        resolved: Dict[str, Any] = {}
        for param_name, dep_name in dependencies.items():
            try:
                resolved[param_name] = self.get(dep_name)
            except KeyError:
                logger.warning(f"Could not resolve dependency: {dep_name}")
        return resolved

    def get_manager(self, name: str) -> Any:
        """
        Get a manager instance by name.

        Args:
            name: Manager name (e.g., 'playback_manager')

        Returns:
            Manager instance
        """
        if self._manager_factory is None:
            self._manager_factory = ManagerFactory()

        # Get required dependencies
        all_deps = {}
        for singleton_name, instance in self._singletons.items():
            all_deps[singleton_name] = instance

        return self._manager_factory.create(name, all_deps)

    def get_all_managers(self) -> Dict[str, Any]:
        """Get all manager instances."""
        if self._manager_factory is None:
            self._manager_factory = ManagerFactory()

        all_deps = dict(self._singletons)
        return self._manager_factory.create_all(all_deps)

    def clear(self) -> None:
        """Clear all registered dependencies (for testing)."""
        self._singletons.clear()
        self._factories.clear()
        self._manager_factory = None
        logger.debug("DI Container cleared")


# Global instance
_container: Optional[DIContainer] = None


def get_di_container() -> DIContainer:
    """Get or create the global DI container."""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def setup_di_container(
    auth: AlexaAuth,
    config: Config,
    state_machine: Optional[AlexaStateMachine] = None,
) -> DIContainer:
    """
    Setup the DI container with standard dependencies.

    Args:
        auth: AlexaAuth instance
        config: Config instance
        state_machine: Optional AlexaStateMachine instance

    Returns:
        Configured DIContainer instance
    """
    container = get_di_container()

    # Register core singletons
    container.register_singleton("auth", auth)
    container.register_singleton("config", config)

    # Register or create state machine
    if state_machine is None:
        state_machine = AlexaStateMachine()
    container.register_singleton("state_machine", state_machine)

    # Register services
    favorite_service = FavoriteService()
    container.register_singleton("FavoriteService", favorite_service)

    # Register cache service used by AlexaAPIService and managers
    from services.cache_service import CacheService

    cache_service = CacheService()
    container.register_singleton("cache_service", cache_service)

    # Register AlexaAPIService skeleton for managers that may consume it
    try:
        from services.alexa_api_service import AlexaAPIService

        alexa_api_service = AlexaAPIService(auth, cache_service)
        container.register_singleton("alexa_api_service", alexa_api_service)
    except Exception as e:
        logger.warning(f"Could not initialize AlexaAPIService: {e}")

    # Register managers
    multiroom_manager = MultiRoomManager()
    container.register_singleton("MultiRoomManager", multiroom_manager)

    logger.info("✅ DI Container initialized with core dependencies")

    return container


def reset_di_container() -> None:
    """Reset the global DI container (for testing)."""
    global _container
    if _container:
        _container.clear()
    _container = None
    logger.debug("Global DI Container reset")
