# Makefile for common developer tasks
.PHONY: vulture test bench profile precommit

vulture:
	vulture . --config .vulture.toml

test:
	python -m pytest --cov=scripts --cov-report=term-missing

bench:
	python -m pytest --benchmark-only

profile:
	pyinstrument -o profile.html python -m pytest tests/pytest_install.py
	@echo "Profile written to profile.html"

precommit:
	pre-commit run --all-files
