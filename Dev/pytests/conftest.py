import os
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--real", action="store_true", default=False, help="Enable tests that use real Alexa API and cookies")


@pytest.fixture(scope="session", autouse=True)
def ensure_test_cookies_available(request):
    """Session fixture: if ALEXA_TEST_COOKIES is not set and the local
    real-user data folder exists and contains files, export it so tests
    that depend on cookies can run without manual env setup.

    Behavior change: the fallback only sets `ALEXA_TEST_COOKIES` when
    pytest is invoked with `--real` (or when the env var is explicitly set).
    This prevents accidental use of real credentials during normal mock-first runs.
    """
    # Explicit env var always honored
    if os.environ.get("ALEXA_TEST_COOKIES"):
        return

    # If user didn't request real-mode, don't set the fallback
    if not request.config.getoption("--real"):
        return

    # expected local data folder relative to repo
    repo_root = Path(__file__).resolve().parents[2]
    fallback = repo_root / "Dev" / "pytests" / "pytests_real_user_api" / "data"

    if fallback.exists() and any(fallback.iterdir()):
        os.environ["ALEXA_TEST_COOKIES"] = str(fallback)
        # Small informative print so test runner logs indicate the fallback
        print(f"[conftest] (--real) ALEXA_TEST_COOKIES set to fallback: {fallback}")
    else:
        # nothing to do; tests that require cookies will still skip
        pass


@pytest.fixture(scope="session")
def maybe_real_auth(request):
    """Return a real AlexaAuth-like object when cookies are available and
    `--real` is requested, otherwise return a lightweight fake with the
    same interface used by the real-user tests.

    The fake implements: load_cookies() -> False, amazon_domain, and
    simple HTTP methods (.get/.post/.put/.delete) returning a small
    object with .status_code and .json()/ .text.
    """
    # If user didn't explicitly opt-in to real mode, return fake quickly
    if not (request.config.getoption("--real") or os.environ.get("ALEXA_TEST_COOKIES")):
        return _make_fake_auth()

    # prefer explicit env var, otherwise fallback (ensure_test_cookies_available may have set it)
    cookie_dir = os.environ.get("ALEXA_TEST_COOKIES")
    if not cookie_dir:
        repo_root = Path(__file__).resolve().parents[2]
        fallback = repo_root / "Dev" / "pytests" / "pytests_real_user_api" / "data"
        if fallback.exists() and any(fallback.iterdir()):
            cookie_dir = str(fallback)

    if cookie_dir:
        try:
            from alexa_auth.alexa_auth import AlexaAuth

            auth = AlexaAuth(data_dir=Path(cookie_dir))
            loaded = auth.load_cookies()
            if loaded:
                return auth
        except Exception:
            # fallthrough to fake below
            pass

    return _make_fake_auth()


def _make_fake_auth():
    class _FakeResp:
        def __init__(self, status_code=200, data=None, text=""):
            self.status_code = status_code
            self._data = data or {}
            self.text = text

        def json(self):
            return self._data

    class _FakeAuth:
        amazon_domain = "com"

        def load_cookies(self):
            return False

        def _ok(self, *args, **kwargs):
            return _FakeResp(status_code=200, data={})

        def get(self, url, timeout=10):
            return self._ok()

        def post(self, url, json=None, timeout=10):
            return self._ok()

        def put(self, url, json=None, timeout=10):
            return self._ok()

        def delete(self, url, timeout=10):
            return self._ok()

    return _FakeAuth()
"""Root pytest configuration for all tests."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import all fixtures from fixtures module
from Dev.pytests.fixtures.conftest import *  # noqa: F401, F403
