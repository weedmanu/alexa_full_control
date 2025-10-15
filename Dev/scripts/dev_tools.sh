#!/usr/bin/env bash
action=${1:-help}
case "$action" in
  vulture)
    vulture . --config .vulture.toml
    ;;
  tests)
    python -m pytest --cov=scripts --cov-report=term-missing
    ;;
  bench)
    python -m pytest --benchmark-only
    ;;
  profile)
    pyinstrument -o profile.html python -m pytest tests/pytest_install.py
    xdg-open profile.html || open profile.html
    ;;
  *)
    echo "Usage: $0 [vulture|tests|bench|profile]"
    ;;
esac
