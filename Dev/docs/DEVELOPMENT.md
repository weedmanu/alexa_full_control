# Development Guide

This file explains how to set up the development environment, run the quality tools, and use the helper scripts added to the repo.

## Prerequisites

- Python 3.11+ installed
- Git

## Architecture Overview

### Refactored Architecture (Phase 1-9)

The codebase has been completely refactored with the following improvements:

#### Phase 1-6: BaseManager Migration

- **Eliminated ~650 lines** of duplicated code
- Unified API calling through `BaseManager._api_call()`
- Standardized error handling and logging
- All managers now inherit from `BaseManager`

#### Phase 7: Performance Optimizations

- **HTTP Headers Pre-computation**: ~50% faster header generation
- **Smart Caching**: Memory cache (TTL) + persistent disk cache
- **Conditional Logging**: Reduced logs in production via `DEBUG` env var
- **Optimized Locks**: Reduced thread contention

#### Phase 8: Integration Tests

- Comprehensive integration test suite (`Dev/pytests/test_integration.py`)
- Performance benchmarks (`Dev/tests/test_performance.py`)
- Cross-manager data consistency validation

#### Phase 9: Documentation

- Complete README with architecture details
- Performance metrics and optimization guides

### Core Components

- **`BaseManager`**: Base class with caching, connection management, unified API calls
- **`DeviceManager`**: Device discovery with 3-level caching (memory TTL + disk persistent + API)
- **`DNDManager`**: Do Not Disturb mode control
- **`NotificationManager`**: Notification and reminder management
- **Services**: `CacheService`, `AuthService`, `StateMachine`

## Create and activate virtual environment (Windows PowerShell)

```powershell
python -m venv venv
. .\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Create and activate virtual environment (Unix/macOS)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

## Run all quality checks (recommended)

```bash
# from project root
python dev_quality.py --all
# or using platform wrappers
./run_tests.sh --all
# on Windows
.\run_tests.ps1 -All
```

## Run individual checks

```bash
python dev_quality.py --mypy
python dev_quality.py --ruff --fix
python dev_quality.py --flake8
python dev_quality.py --pytest -k test_device
python dev_quality.py --coverage
```

## New Integration Tests

```bash
# Integration tests (cross-manager scenarios)
python -m pytest Dev/pytests/test_integration.py -v

# Performance benchmarks
python -m pytest Dev/pytests/test_performance.py -v

# All tests including new ones
python -m pytest Dev/pytests/ -v
```

## CI

A GitHub Actions workflow is included at `.github/workflows/ci.yml`. It runs `python dev_quality.py --all` on push and PR for `main` and `refacto` branches.

## Pre-commit (recommended)

Pre-commit is configured in `.pre-commit-config.yaml`. To install and enable hooks locally:

```bash
pip install pre-commit
pre-commit install
# run all hooks on the repository once
pre-commit run --all-files
```

This will run `black`, `isort`, `ruff` and `flake8` automatically on staged files.

## Performance Environment Variables

```bash
# Enable debug mode (verbose logging)
export DEBUG=true

# Disable for production (reduced logging)
export DEBUG=false
```

## Notes

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD` is set by scripts to avoid flaky plugin auto-loading.
- The `dev_quality.py` script prints a compact summary at the end of a run.
- New integration tests validate the refactored architecture and performance optimizations.
