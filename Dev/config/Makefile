# Makefile for common developer tasks

.PHONY: venv install lint typecheck test devtools bench profile precommit vulture

# Python executable inside project virtualenv
PYTHON := .venv\Scripts\python.exe

vulture:
	vulture . --config .vulture.toml

# Create a local virtualenv
venv:
	python -m venv .venv

# Install development dependencies into the venv
install: venv
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -r requirements-dev.txt

lint:
	# lint with ruff and check formatting with black/isort (checks only)
	$(PYTHON) -m ruff check . --exclude Dev
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .

typecheck:
	# static typing checks
	$(PYTHON) -m mypy core/ cli/ services/ --strict

test:
	# Run pytest covering core, cli and services (ignore Dev/ by default)
	$(PYTHON) -m pytest --cov=core --cov=cli --cov=services --cov-report=term-missing -q --ignore=Dev

devtools:
	# Run the Dev PowerShell helper (pass ARGS to script via DEVARGS)
	@powershell -NoProfile -ExecutionPolicy Bypass -Command "& './Dev/scripts/dev_tools.ps1' $(DEVARGS)"

bench:
	$(PYTHON) -m pytest --benchmark-only

profile:
	@echo "Profiling disabled - no test file available"
	# $(PYTHON) -m pyinstrument -o profile.html $(PYTHON) -m pytest tests/pytest_install.py
	@echo "Profile written to profile.html"

precommit:
	$(PYTHON) -m pre_commit run --all-files
