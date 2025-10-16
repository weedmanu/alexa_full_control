"""Root pytest configuration for all tests."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import all fixtures from fixtures module
from Dev.pytests.fixtures.conftest import *  # noqa: F401, F403
