"""
DI Setup Module - Initialization and configuration helpers for the DI container.

Provides utilities for setting up and managing the dependency injection container
in different contexts (CLI, tests, API, etc.).
"""

from typing import Any, Optional
from loguru import logger

from core.di_container import DIContainer, setup_di_container, reset_di_container, get_di_container
from core.config import Config
from core.state_machine import AlexaStateMachine
from alexa_auth.alexa_auth import AlexaAuth


class DISetup:
    """Helper class for DI container setup and management."""

    @staticmethod
    def setup_for_cli(
        auth_file: Optional[str] = None,
        config_file: Optional[str] = None,
    ) -> DIContainer:
        """
        Setup DI container for CLI usage.

        Args:
            auth_file: Path to auth credentials file (Note: AlexaAuth loads from default dir)
            config_file: Path to configuration file (Note: Config loads from default dir)

        Returns:
            Configured DIContainer
        """
        logger.info("Setting up DI Container for CLI")

        # Load configuration (Config reads from its default data directory)
        config = Config()

        # Load or create auth (AlexaAuth reads from its default data directory)
        auth = AlexaAuth()

        # Setup container
        container = setup_di_container(auth, config)

        logger.info("✅ CLI DI Container ready")
        return container

    @staticmethod
    def setup_for_testing() -> DIContainer:
        """
        Setup DI container for testing.

        Returns:
            Clean DIContainer for tests
        """
        logger.debug("Setting up DI Container for testing")

        # Reset any global state
        reset_di_container()

        # Create fresh instances
        config = Config()
        auth = AlexaAuth()
        state_machine = AlexaStateMachine()

        # Setup container
        container = setup_di_container(auth, config, state_machine)

        logger.debug("✅ Test DI Container ready")
        return container

    @staticmethod
    def setup_for_api(
        auth: AlexaAuth,
        config: Config,
        state_machine: Optional[AlexaStateMachine] = None,
    ) -> DIContainer:
        """
        Setup DI container for API/service usage.

        Args:
            auth: AlexaAuth instance
            config: Config instance
            state_machine: Optional AlexaStateMachine instance

        Returns:
            Configured DIContainer
        """
        logger.info("Setting up DI Container for API")

        container = setup_di_container(auth, config, state_machine)

        logger.info("✅ API DI Container ready")
        return container

    @staticmethod
    def register_custom_service(name: str, instance: Any) -> None:
        """
        Register a custom service in the DI container.

        Args:
            name: Service name
            instance: Service instance
        """
        container = get_di_container()
        container.register_singleton(name, instance)
        logger.debug(f"Registered custom service: {name}")

    @staticmethod
    def get_container() -> DIContainer:
        """Get the current DI container."""
        return get_di_container()

    @staticmethod
    def clear() -> None:
        """Clear the DI container (for testing)."""
        reset_di_container()
        logger.debug("DI Container cleared")


# Lazy initialization pattern
_setup_instance: Optional[DISetup] = None


def get_setup() -> DISetup:
    """Get the DISetup helper instance."""
    global _setup_instance
    if _setup_instance is None:
        _setup_instance = DISetup()
    return _setup_instance
