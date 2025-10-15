"""Terminal color utilities shared across the project.

This module centralises ANSI color codes and small helpers to check
whether the terminal supports colours (with a best-effort support for
Windows via colorama).
"""

# Optional Windows color support (imported at module level to avoid local imports)
# Prefer to check availability with importlib to avoid import-time side-effects
import importlib.util
import os
import platform
import sys

if importlib.util.find_spec("colorama") is not None:
    # dynamic import to keep static analyzers happy only when present
    import importlib

    colorama = importlib.import_module("colorama")  # type: ignore
    _has_colorama_available = True
else:
    # colorama is optional; absence simply means no ANSI emulation on Windows
    _has_colorama_available = False
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
        if not bool(getattr(sys.stdout, "isatty", lambda: False)()):
            return False

        if platform.system() == "Windows":
            # If colorama wasn't imported, assume no colour support
            if not _has_colorama_available:
                return False

            # colorama may not be present in globals() if ImportError occurred
            colorama_mod = globals().get("colorama")
            if colorama_mod is None:
                return False

            # If colorama provides init, call it. Use attribute checks to avoid
            # catching broadly; if init is missing assume no color support.
            init_fn = getattr(colorama_mod, "init", None)
            if not callable(init_fn):
                return False

            # Call init and assume success; if it raises an unexpected
            # exception it's fine to let it surface as it's an unusual state.
            init_fn()  # type: ignore
            return True

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


def should_colorize(*, no_color: bool = False) -> bool:
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

    # If output is a TTY, allow colors. Use getattr to avoid AttributeError on
    # unusual stream objects and avoid broad try/except.
    stdout_isatty = bool(getattr(sys.stdout, "isatty", lambda: False)())
    stderr_isatty = bool(getattr(sys.stderr, "isatty", lambda: False)())
    return stdout_isatty and stderr_isatty
