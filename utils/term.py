from __future__ import annotations

import os
import sys


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
