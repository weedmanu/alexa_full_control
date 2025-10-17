"""
CLI Command Adapter Layer for DI Integration.

This adapter layer allows gradual refactoring of existing commands
to use the new ManagerCommand template and DIContainer without breaking
existing functionality.

Pattern:
    - Old commands inherit from BaseCommand (current)
    - New commands inherit from ManagerCommand (new)
    - Adapter provides bridge between both patterns
    - DIContainer is available to both via adapter
"""

from typing import Any, Dict, Optional, Type

from loguru import logger

from cli.command_template import ManagerCommand
from core.di_container import get_di_container


class CommandAdapter:
    """
    Adapter that bridges old BaseCommand and new ManagerCommand patterns.

    Provides:
    - DIContainer access for all commands
    - Manager lookup and injection
    - Error handling and logging
    - Backward compatibility
    """

    def __init__(self) -> None:
        """Initialize adapter with DI container."""
        self.di_container = get_di_container()
        self.logger = logger

    def get_manager(self, manager_name: str) -> Any:
        """
        Get manager instance from DI container by name.

        Args:
            manager_name: Name of manager to retrieve (e.g., 'playback_manager')

        Returns:
            Manager instance or None if not found

        Raises:
            ValueError: If manager not registered in container
        """
        try:
            return self.di_container.get_manager(manager_name)
        except Exception as e:
            self.logger.error(f"Failed to get manager {manager_name}: {e}")
            raise ValueError(f"Manager not available: {manager_name}") from e

    def inject_di_container(self, command: Any) -> None:
        """
        Inject DIContainer into command instance.

        Allows old BaseCommand subclasses to access DI container.

        Args:
            command: Command instance to inject into
        """
        if hasattr(command, "context"):
            # Attach DI container to context if available
            if command.context is None:
                command.context = type("Context", (), {})()
            # Use setattr to avoid static typing issues on Context
            command.context.di_container = self.di_container
        else:
            # Direct injection as attribute
            command.di_container = self.di_container

    def create_manager_command(
        self,
        command_class: Type[ManagerCommand],
        command_name: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ) -> ManagerCommand:
        """
        Create and initialize a ManagerCommand instance.

        Args:
            command_class: ManagerCommand subclass
            command_name: Name of the command (defaults to class name)
            args: Optional arguments dict (not directly assigned to command)

        Returns:
            Initialized ManagerCommand instance
        """
        try:
            name = command_name or command_class.__name__.lower()
            command = command_class(name, self.di_container)
            return command
        except Exception as e:
            self.logger.error(f"Failed to create command {command_class.__name__}: {e}")
            raise

    def execute_command(self, command: Any, args: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute command with error handling and logging.

        Args:
            command: Command instance (BaseCommand or ManagerCommand)
            args: Optional arguments

        Returns:
            Command result
        """
        try:
            # Inject DI container
            self.inject_di_container(command)

            # Execute
            if isinstance(command, ManagerCommand):
                # ManagerCommand defines an async execute() and provides a
                # synchronous helper validate_and_execute() which runs the
                # coroutine in an event loop. Use that wrapper to remain
                # compatible with sync callers.
                try:
                    return command.validate_and_execute(args or {})
                except AttributeError:
                    # Fallback: if the ManagerCommand implementation does not
                    # provide validate_and_execute for some reason, try to
                    # run the coroutine safely.
                    import asyncio

                    coro = command.execute(args or {})
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = None

                    if loop and loop.is_running():
                        # Running event loop (rare in CLI). Schedule and wait.
                        return asyncio.run(coro)
                    else:
                        return asyncio.get_event_loop().run_until_complete(coro)
            else:
                # Old BaseCommand pattern (synchronous execute)
                return command.execute(args or {})

        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise


class CommandContext:
    """
    Context object for passing managers and services to commands.

    Provides a unified interface for command dependencies.
    """

    def __init__(self, di_container: Optional[Any] = None) -> None:
        """
        Initialize context with optional DI container.

        Args:
            di_container: DIContainer instance (defaults to get_di_container())
        """
        self.di_container = di_container or get_di_container()
        self._managers: Dict[str, Any] = {}

    def get_manager(self, manager_name: str) -> Any:
        """
        Get manager from DI container with caching.

        Args:
            manager_name: Name of manager

        Returns:
            Manager instance
        """
        if manager_name not in self._managers:
            self._managers[manager_name] = self.di_container.get_manager(manager_name)
        return self._managers[manager_name]

    def set_manager(self, manager_name: str, instance: Any) -> None:
        """
        Set manager instance directly (for testing).

        Args:
            manager_name: Name of manager
            instance: Manager instance
        """
        self._managers[manager_name] = instance

    def clear_cache(self) -> None:
        """Clear manager cache."""
        self._managers.clear()


class CommandFactory:
    """
    Factory for creating commands with proper initialization.

    Handles both old and new command patterns.
    """

    def __init__(self) -> None:
        """Initialize factory with adapter."""
        self.adapter = CommandAdapter()
        self.logger = logger

    def create_base_command(self, command_class: Type[Any], context: Optional[CommandContext] = None) -> Any:
        """
        Create BaseCommand instance with context.

        Args:
            command_class: BaseCommand subclass
            context: Optional CommandContext

        Returns:
            Initialized command instance
        """
        try:
            command = command_class()
            if context is None:
                context = CommandContext(self.adapter.di_container)
            command.context = context
            self.adapter.inject_di_container(command)
            return command
        except Exception as e:
            self.logger.error(f"Failed to create command {command_class.__name__}: {e}")
            raise

    def create_manager_command(self, command_class: Type[ManagerCommand]) -> ManagerCommand:
        """
        Create ManagerCommand instance with DI container.

        Args:
            command_class: ManagerCommand subclass

        Returns:
            Initialized ManagerCommand instance
        """
        return self.adapter.create_manager_command(command_class)

    def create_command(self, command_class: Type[Any], context: Optional[CommandContext] = None) -> Any:
        """
        Create command (auto-detects type).

        Args:
            command_class: Command class
            context: Optional CommandContext

        Returns:
            Initialized command instance
        """
        try:
            if issubclass(command_class, ManagerCommand):
                return self.create_manager_command(command_class)
            else:
                return self.create_base_command(command_class, context)
        except Exception as e:
            self.logger.error(f"Failed to create command: {e}")
            raise


# Singleton instance
_adapter: Optional[CommandAdapter] = None
_factory: Optional[CommandFactory] = None


def get_command_adapter() -> CommandAdapter:
    """Get or create command adapter singleton."""
    global _adapter
    if _adapter is None:
        _adapter = CommandAdapter()
    return _adapter


def get_command_factory() -> CommandFactory:
    """Get or create command factory singleton."""
    global _factory
    if _factory is None:
        _factory = CommandFactory()
    return _factory
