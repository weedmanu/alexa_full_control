"""
CLI Command Template - Base Class for All Commands.

Provides the foundation for all CLI commands with built-in support for:
- Dependency injection from DIContainer
- Parameter validation
- Error handling and logging
- Help text generation
- Result formatting

Usage:
    from cli.command_template import ManagerCommand
    from core.di_container import get_di_container

    class PlayCommand(ManagerCommand):
        def __init__(self, di_container):
            super().__init__("playback", di_container)

        def validate(self, params: dict[str, Any]) -> bool:
            return "device" in params

        async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
            manager = self.get_manager("playback_manager")
            return {"success": True, "data": await manager.play()}
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.di_container import DIContainer
from core.exceptions import APIError, ValidationError

logger = logging.getLogger(__name__)


class ManagerCommand(ABC):
    """
    Base class for all CLI commands.

    Provides common functionality for command execution, validation, and help.
    Subclasses must implement:
    - validate(params): Parameter validation logic
    - execute(params): Command execution logic
    """

    def __init__(self, command_name: str, di_container: DIContainer) -> None:
        """
        Initialize command with DI container.

        Args:
            command_name: Name of the command (e.g., "playback", "device")
            di_container: DIContainer instance for dependency injection
        """
        self.command_name = command_name
        self.di_container = di_container
        self.logger = logging.getLogger(f"{__name__}.{command_name}")

    @classmethod
    def setup_parser(cls, parser: Any) -> None:
        """
        Optional classmethod to configure argparse parser for this command

        Default implementation does nothing. Subclasses may implement as a
        @classmethod to allow the command to be registered without
        instantiating it (useful during CLI parser setup).
        """
        # By default, nothing to configure at class level
        return

    @abstractmethod
    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate command parameters.

        Args:
            params: Command parameters to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValidationError: If validation fails with detailed error info
        """
        pass

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the command.

        Args:
            params: Validated command parameters

        Returns:
            Result dictionary with structure:
            {
                "success": bool,
                "data": Any (optional),
                "error": str (optional),
                "formatted": str (optional)
            }

        Raises:
            APIError: On API communication errors
            Exception: On any execution errors
        """
        pass

    def get_manager(self, manager_name: str) -> Any:
        """
        Get a manager from DI container.

        Args:
            manager_name: Name of the manager to retrieve

        Returns:
            Manager instance from container

        Raises:
            KeyError: If manager not found in container
        """
        return self.di_container.get_manager(manager_name)

    def help(self) -> Dict[str, Any]:
        """
        Generate help text for the command.

        Returns:
            Dictionary with:
            {
                "name": str,
                "description": str,
                "usage": str,
                "parameters": dict,
                "examples": list,
                "errors": dict
            }
        """
        return {
            "name": self.command_name,
            "description": self.__doc__ or "No description available",
            "usage": f"{self.command_name} [options]",
            "parameters": {},
            "examples": [],
            "errors": {},
        }

    def validate_and_execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters then execute command synchronously.

        This is a convenience wrapper for sync-style usage.

        Args:
            params: Command parameters

        Returns:
            Execution result

        Raises:
            ValidationError: If validation fails
        """
        try:
            self.logger.debug(f"Validating parameters for {self.command_name}")
            if not self.validate(params):
                raise ValidationError(f"Invalid parameters for {self.command_name}")

            self.logger.info(f"Executing {self.command_name} with params: {params}")

            # Execute async command using event loop
            import asyncio

            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(self.execute(params))

            self.logger.info(f"Executed {self.command_name} successfully: {result}")
            return result

        except ValidationError as e:
            self.logger.warning(f"Validation error: {e}")
            return {"success": False, "error": str(e), "field": "parameters"}
        except APIError as e:
            self.logger.error(f"API error: {e}", exc_info=True)
            return {"success": False, "error": f"API Error: {str(e)}", "code": getattr(e, "code", None)}
        except Exception as e:
            self.logger.error(f"Unexpected error executing {self.command_name}: {e}", exc_info=True)
            return {"success": False, "error": f"Error: {str(e)}"}

    def format_output(self, data: Any) -> str:
        """
        Format command output for display.

        Args:
            data: Data to format

        Returns:
            Formatted string for display
        """
        if isinstance(data, dict):
            return str(data)
        elif isinstance(data, list):
            return "\n".join(str(item) for item in data)
        else:
            return str(data)

    def log_execution(self, params: Dict[str, Any], result: Dict[str, Any], duration_ms: float) -> None:
        """
        Log command execution with metrics.

        Args:
            params: Input parameters
            result: Execution result
            duration_ms: Execution duration in milliseconds
        """
        status = "SUCCESS" if result.get("success") else "FAILED"
        self.logger.info(
            f"{self.command_name} {status}: {duration_ms:.2f}ms - "
            f"params={params}, error={result.get('error', 'None')}"
        )


class ManagerCommandBuilder:
    """
    Builder class for creating ManagerCommand instances with configuration.

    Useful for creating commands with custom managers and settings.
    """

    def __init__(self, command_name: str) -> None:
        """Initialize builder."""
        self.command_name = command_name
        self._manager_name: Optional[str] = None
        self._di_container: Optional[DIContainer] = None

    def with_manager(self, manager_name: str) -> "ManagerCommandBuilder":
        """Set the manager for this command."""
        self._manager_name = manager_name
        return self

    def with_di_container(self, di_container: DIContainer) -> "ManagerCommandBuilder":
        """Set the DI container."""
        self._di_container = di_container
        return self

    def build(self) -> Dict[str, Any]:
        """Build command configuration."""
        if not self._di_container:
            raise ValueError("DI container must be configured")

        return {"name": self.command_name, "manager": self._manager_name, "di_container": self._di_container}


class CommandRegistry:
    """
    Registry for managing command instances.

    Provides centralized command registration and retrieval.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._commands: Dict[str, ManagerCommand] = {}
        self._logger = logging.getLogger(__name__)

    def register(self, command_name: str, command: ManagerCommand) -> None:
        """
        Register a command.

        Args:
            command_name: Name for the command
            command: ManagerCommand instance
        """
        if command_name in self._commands:
            self._logger.warning(f"Overwriting existing command: {command_name}")
        self._commands[command_name] = command
        self._logger.debug(f"Registered command: {command_name}")

    def get(self, command_name: str) -> Optional[ManagerCommand]:
        """
        Get a registered command.

        Args:
            command_name: Name of command to retrieve

        Returns:
            ManagerCommand or None if not found
        """
        return self._commands.get(command_name)

    def list_commands(self) -> Dict[str, ManagerCommand]:
        """
        Get all registered commands.

        Returns:
            Dictionary of all commands
        """
        return self._commands.copy()

    def has_command(self, command_name: str) -> bool:
        """
        Check if command is registered.

        Args:
            command_name: Command to check

        Returns:
            True if registered, False otherwise
        """
        return command_name in self._commands

    def unregister(self, command_name: str) -> bool:
        """
        Unregister a command.

        Args:
            command_name: Command to remove

        Returns:
            True if removed, False if not found
        """
        if command_name in self._commands:
            del self._commands[command_name]
            self._logger.debug(f"Unregistered command: {command_name}")
            return True
        return False

    def clear(self) -> None:
        """Clear all registered commands."""
        self._commands.clear()
        self._logger.debug("Cleared all commands")


# Global command registry instance
_command_registry: Optional[CommandRegistry] = None


def get_command_registry() -> CommandRegistry:
    """
    Get or create the global command registry.

    Returns:
        Global CommandRegistry instance
    """
    global _command_registry
    if _command_registry is None:
        _command_registry = CommandRegistry()
    return _command_registry


def reset_command_registry() -> None:
    """Reset the global command registry (useful for testing)."""
    global _command_registry
    if _command_registry:
        _command_registry.clear()
    _command_registry = None
