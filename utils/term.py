"""Terminal color utilities shared across the project.

This module centralises ANSI color codes and small helpers to check
whether the terminal supports colours (with a best-effort support for
Windows via colorama).
"""
import os
import platform
import sys


class Colors:
    """Centralised ANSI color palette and helpers.

    Keeps attribute names used across the codebase (RESET, BOLD, *_BOLD,
    and a few convenience methods like supports_color / is_supported and
    colorize) so refactors are minimal.
    """

    # Reset / attributes
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Standardised section colours (used by help formatter)
    GRAY_BOLD = "\033[1;90m"
    CYAN_BOLD = "\033[1;36m"
    CYAN = "\033[0;36m"
    MAGENTA_BOLD = "\033[1;35m"
    MAGENTA = "\033[0;35m"
    GREEN_BOLD = "\033[1;32m"
    GREEN = "\033[0;32m"
    ORANGE_BOLD = "\033[1;38;5;208m"
    ORANGE = "\033[0;38;5;208m"
    YELLOW_BOLD = "\033[1;33m"
    WHITE_BOLD = "\033[1;37m"
    RED_BOLD = "\033[1;31m"

    # Additional simple colours referenced elsewhere
    BLUE = "\033[1;34m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"

    @staticmethod
    def supports_color() -> bool:
        """Return True if the running output supports ANSI colours.

        On Windows, attempt to initialise colorama if present; otherwise
        conservatively return False.
        """
        # If stdout is not a TTY we don't assume colours
        if not sys.stdout or not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        if platform.system() == "Windows":
            try:
                import colorama

                colorama.init()
                return True
            except Exception:
                return False

        # On other OSes, assume a TTY supports colours
        return True

    # alias kept for backwards-compatibility
    is_supported = supports_color

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Wrap text with the colour sequence if supported."""
        if not Colors.supports_color():
            return text
        return f"{color}{text}{Colors.RESET}"


def should_colorize(no_color: bool = False) -> bool:
    """Return True if ANSI/color should be used.

    Priority:
    - If `no_color` True -> False
    - If environment variable NO_COLOR is set -> False
    - If stdout/stderr are TTY -> True
    - Otherwise False
    """
    if no_color:
        return False

    # Respect standard NO_COLOR env var
    if os.environ.get("NO_COLOR") is not None:
        return False

    # If output is a TTY, allow colors
    try:
        if sys.stdout.isatty() and sys.stderr.isatty():
            return True
    except Exception:
        pass

    return False
