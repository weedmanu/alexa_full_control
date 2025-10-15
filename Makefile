# Makefile for common developer tasks
.PHONY: vulture test bench profile precommit

vulture:
	vulture . --config .vulture.toml

lint:
	# lint with ruff and check formatting with black/isort (checks only)
	ruff check .
	black --check .
	isort --check-only .

typecheck:
	# static typing checks
	mypy core/ cli/ services/ --strict

test:
	# Run pytest covering core, cli and services
	python -m pytest --cov=core --cov=cli --cov=services --cov-report=term-missing

bench:
	python -m pytest --benchmark-only

profile:
	pyinstrument -o profile.html python -m pytest tests/pytest_install.py
	@echo "Profile written to profile.html"

precommit:
	pre-commit run --all-files
