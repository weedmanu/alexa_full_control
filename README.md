# Alexa Full Control CLI - v0.2.0-refacto

**Repository:** https://github.com/weedmanu/alexa_full_control (branch: refacto)  
**Status:** ✅ Development Complete - Ready for Enhancements

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest Dev/pytests/cli/ -v
python -m alexa_cli --help
```

---

### ✅ Quality checks and git hooks

To ensure consistent quality, this repository includes scripts to run unit tests and static type checks before pushing.

- Install the git hooks directory (one-time):

  git config core.hooksPath .githooks

- Populate the hooks (PowerShell):

  powershell.exe -NoProfile -ExecutionPolicy Bypass -File Dev\scripts\install_git_hooks.ps1

- The pre-push hook runs `Dev/scripts/run_quality_checks.ps1`, which executes `pytest` then `mypy` (using `mypy.ini`). If either step fails the push is blocked.

If you need to bypass the hook for an exceptional case, use `git push --no-verify` but prefer to fix failing checks.

## 📚 Documentation

**All documentation in `Dev/docs/`:**

- **`reference/ARCHITECTURE.md`** - System design & patterns
- **`reference/MIGRATION_GUIDE.md`** - CLI upgrade guide
- **`reference/PHASE_7_SUMMARY.md`** - Phase overview
- **`reference/PROJECT_COMPLETION_REPORT.md`** - Final report
- **`phases/INDEX.md`** - Development phases archive

---

## 📊 Status

| Metric        | Value           |
| ------------- | --------------- |
| Commands      | 40/40 (100%) ✅ |
| Tests         | 88/88 (100%) ✅ |
| Type Safety   | 100% ✅         |
| Documentation | 6,700+ lines    |

---

## 🏗️ Structure

```
Dev/
├── config/          (Makefile, mypy.ini, .flake8)
├── docs/
│   ├── reference/   (Main documentation)
│   └── phases/      (Phase archive)
└── pytests/         (Test suite)

cli/                 (40 refactored commands)
core/                (Managers, DIContainer)
services/            (Business logic)
utils/               (Utilities)
```

---

**See `Dev/docs/reference/` for complete documentation** 📖
