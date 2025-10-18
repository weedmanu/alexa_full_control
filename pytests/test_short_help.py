import subprocess
import sys
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENTRY = str(PROJECT_ROOT / "alexa")


def run_alexa(args):
    env = os.environ.copy()
    # Force UTF-8 for child process to avoid decoding issues on Windows
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, ENTRY] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=PROJECT_ROOT,
        env=env,
    )
    return proc


def test_short_help_exists_and_exits_0():
    proc = run_alexa(["-h"])
    assert proc.returncode == 0, f"Exit code != 0: stdout={proc.stdout!r} stderr={proc.stderr!r}"
    out = proc.stdout
    assert "Usage:" in out, "Short help should contain 'Usage:'"
    assert any(k in out for k in ("Categories:", "Categories", "Actions possibles", "Actions")), \
        "Short help should list categories or actions"


def test_short_help_no_color_strips_ansi():
    # Run with color then with --no-color and make sure ANSI sequences are absent
    proc_color = run_alexa(["-h"])    
    proc_nocolor = run_alexa(["-h", "--no-color"])
    # Basic sanity
    assert proc_color.returncode == 0 and proc_nocolor.returncode == 0
    # If color enabled, stdout may contain ESC (\x1b). When --no-color, it must not.
    has_esc_color = "\x1b" in proc_color.stdout
    has_esc_nocolor = "\x1b" in proc_nocolor.stdout
    assert not has_esc_nocolor, "--no-color output should not contain ANSI escape codes"
