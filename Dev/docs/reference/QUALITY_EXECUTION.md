# 🧪 Tests de Qualité - Mémo Commandes

**Environnement:** Python 3.13+ (venv) | **Branche:** `refacto`

---

## ⚡ SETUP

```powershell
cd c:\Users\weedm\Downloads\alexa_full_control
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip black isort ruff flake8 mypy pytest
```

---

## 1️⃣ BLACK

### Avec `.venv`

```powershell
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
.\.venv\Scripts\python.exe -m black cli core utils services models alexa
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
```

### Global (Python dans PATH)

```powershell
python -m black --check cli core utils services models alexa
python -m black cli core utils services models alexa
python -m black --check cli core utils services models alexa
```

---

## 2️⃣ ISORT

### Avec `.venv`

```powershell
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
```

### Global (Python dans PATH)

```powershell
python -m isort --check-only cli core utils services models alexa
python -m isort cli core utils services models alexa
python -m isort --check-only cli core utils services models alexa
```

---

## 3️⃣ RUFF

### Avec `.venv`

```powershell
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check --fix cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
```

### Global (Python dans PATH)

```powershell
python -m ruff check cli core utils services models alexa
python -m ruff check --fix cli core utils services models alexa
python -m ruff check cli core utils services models alexa
```

---

## 4️⃣ FLAKE8

### Avec `.venv`

```powershell
.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291
```

### Global (Python dans PATH)

```powershell
python -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291
```

---

## 5️⃣ MYPY

### Avec `.venv`

```powershell
.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports
```

### Global (Python dans PATH)

```powershell
python -m mypy cli core utils services models --ignore-missing-imports
```

---

## 6️⃣ PYTEST

### Avec `.venv`

```powershell
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -q --tb=line
```

### Global (Python dans PATH)

```powershell
python -m pytest Dev/pytests/ -q --tb=line
```

---

## 🔄 TOUT D'UN COUP

| #   | Étape  | Vérifier                            | Corriger                |
| --- | ------ | ----------------------------------- | ----------------------- |
| 1   | BLACK  | `black --check ...`                 | `black ...`             |
| 2   | ISORT  | `isort --check-only ...`            | `isort ...`             |
| 3   | RUFF   | `ruff check ...`                    | `ruff check --fix ...`  |
| 4   | FLAKE8 | `flake8 ... --max-line-length=120`  | Correction manuelle     |
| 5   | MYPY   | `mypy ... --ignore-missing-imports` | Correction manuelle     |
| 6   | PYTEST | `pytest Dev/pytests/ -q --tb=line`  | Corriger le code source |

---

## 🔄 POUR TESTER TOUT À LA FOIS

```powershell
# Format
.\.venv\Scripts\python.exe -m black cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check --fix cli core utils services models alexa

# Vérifications
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291
.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -q --tb=line
```

---

## ✨ TESTS PRODUCTION-READY

```powershell
# Entry point test
.\.venv\Scripts\python.exe alexa --version

# CLI help
.\.venv\Scripts\python.exe alexa --help

# Imports verification
.\.venv\Scripts\python.exe -c "from cli import create_context, create_parser; print('✅ Imports OK')"

# Config verification
.\.venv\Scripts\python.exe -c "from config import Config; print('✅ Config OK')"

# Auth verification
.\.venv\Scripts\python.exe -c "from alexa_auth.alexa_auth import AlexaAuth; print('✅ Auth OK')"
```

---

**Mode:** Référence pour développement - À ajuster au fur et à mesure
