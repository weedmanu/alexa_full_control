# 🧪 Exécution des Tests de Qualité - Commandes Directes

**Date:** 17 octobre 2025  
**Environnement:** Python 3.13+ (venv), Windows 11  
**Branche:** `refacto`  
**Périmètre:** `cli/`, `core/`, `utils/`, `services/`, `models/`, `alexa` (entry point)  
**Exclusions:** `Dev/`, `.venv/`, `.nodeenv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`

---

## ⚡ SETUP INITIAL (Une seule fois)

```powershell
cd c:\Users\weedm\Downloads\alexa_full_control
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip setuptools wheel black isort ruff flake8 mypy pytest
```

---

## 🎯 COMMANDES À TAPER - Un Test Après l'Autre

### 1️⃣ BLACK (Formatage du Code)

**Vérifier:**

```powershell
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
```

**Si erreurs → Corriger automatiquement:**

```powershell
.\.venv\Scripts\python.exe -m black cli core utils services models alexa
```

**Re-vérifier:**

```powershell
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
```

Expected: `All done! 0 files would be reformatted.` ✅

---

### 2️⃣ ISORT (Tri des Imports)

**Vérifier:**

```powershell
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
```

**Si erreurs → Corriger automatiquement:**

```powershell
.\.venv\Scripts\python.exe -m isort cli core utils services models alexa
```

**Re-vérifier:**

```powershell
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
```

Expected: `Skipped 0 files` ✅

---

### 3️⃣ RUFF (Linting Moderne)

**Vérifier:**

```powershell
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
```

**Si erreurs → Corriger automatiquement (ce qui peut l'être):**

```powershell
.\.venv\Scripts\python.exe -m ruff check --fix cli core utils services models alexa
```

**Voir les erreurs restantes:**

```powershell
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa --show-fixes
```

Expected: `All checks passed!` ✅

---

### 4️⃣ FLAKE8 (Vérification de Style)

**Vérifier:**

```powershell
.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291
```

**Voir les détails (si erreurs):**

```powershell
.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --show-source --statistics
```

**Corrections courantes:**

- `W291` - Espaces à la fin de ligne → Supprimer
- `E302` - 2 lignes vides attendues → Ajouter une ligne vide
- `F401` - Import non utilisé → Supprimer l'import

Expected: `(pas d'output)` ✅

---

### 5️⃣ MYPY (Vérification des Types)

**Vérifier:**

```powershell
.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports
```

**Voir les erreurs (si y'en a):**

```powershell
.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports > mypy_errors.txt
Get-Content mypy_errors.txt
```

**Corriger manuellement:**

- Ajouter imports: `from typing import List, Dict, Optional`
- Ajouter type hints aux fonctions: `def func(x: int) -> str:`
- Ajouter type hints aux classes

Expected: `Success: no issues found in X source files` ✅

---

### 6️⃣ PYTEST (Tests Unitaires - Doivent TOUJOURS Passer)

**Lancer tous les tests:**

```powershell
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -q --tb=line
```

**Verbose (si erreurs):**

```powershell
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -v --tb=short
```

**Avec couverture:**

```powershell
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ --cov=cli --cov=core --cov=services --cov=utils
```

Expected: `798 passed in ~3.45s` ✅

---

## ✅ RÉSUMÉ EXÉCUTION

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
