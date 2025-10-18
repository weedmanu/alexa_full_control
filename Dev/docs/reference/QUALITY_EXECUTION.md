# 🧪 Tests de Qualité - Commandes

**Setup:** `cd c:\Users\weedm\Downloads\alexa_full_control; .\.venv\Scripts\Activate.ps1`

**Exclusions:** `--exclude=__pycache__,*.pyc,.git,.venv,Dev/,logs/,data/,node_modules/,*.egg-info`

---

## 1️⃣ BLACK

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
.\.venv\Scripts\python.exe -m black cli core utils services models alexa
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\black.exe --check cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\black.exe cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\black.exe --check cli core utils services models alexa
```

---

## 2️⃣ ISORT

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\isort.exe --check-only cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\isort.exe cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\isort.exe --check-only cli core utils services models alexa
```

---

## 3️⃣ RUFF

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check --fix cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\ruff.exe check cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\ruff.exe check --fix cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\ruff.exe check cli core utils services models alexa
```

---

## 4️⃣ FLAKE8

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\flake8.exe cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291
```

---

## 5️⃣ MYPY

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\mypy.exe cli core utils services models --ignore-missing-imports
```

---

## 6️⃣ PYTEST

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -q --tb=line
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ --cov=alexa --cov-report=html
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -v
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\pytest.exe Dev/pytests/ -q --tb=line
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\pytest.exe Dev/pytests/ --cov=alexa --cov-report=html
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\pytest.exe Dev/pytests/ -v
```

---

## 7️⃣ BANDIT (Sécurité)

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m bandit -r cli core utils services models alexa
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\bandit.exe -r cli core utils services models alexa
```

---

## 8️⃣ VULTURE (Code Mort)

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m vulture cli core utils services models alexa
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\vulture.exe cli core utils services models alexa
```

---

## 9️⃣ PYLINT (Linting Complet)

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m pylint cli core utils services models alexa
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\pylint.exe cli core utils services models alexa
```

---

## 🔟 PYDOCSTYLE (Docstrings)

**Venv:**

```powershell
.\.venv\Scripts\python.exe -m pydocstyle cli core utils services models alexa
```

**Global (avec chemin complet):**

```powershell
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\pydocstyle.exe cli core utils services models alexa
```

---

## 🔧 Commandes Utiles Supplémentaires

### Installation des outils (venv)

```powershell
.\.venv\Scripts\python.exe -m pip install -r Dev/requirements-dev.txt
```

### Mise à jour des outils

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade black isort ruff flake8 mypy bandit vulture pylint pydocstyle pytest
```

### Vérification de l'environnement

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip list | grep -E "(black|isort|ruff|flake8|mypy|bandit|vulture|pylint|pydocstyle|pytest)"
```

### Nettoyage des caches

```powershell
Remove-Item -Recurse -Force __pycache__,*.pyc,.mypy_cache,.ruff_cache -ErrorAction SilentlyContinue
```

### Tests complets (tous les outils)

```powershell
# Formatage
.\.venv\Scripts\python.exe -m black cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort cli core utils services models alexa

# Linting
.\.venv\Scripts\python.exe -m ruff check --fix cli core utils services models alexa
.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291

# Types
.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports

# Sécurité
.\.venv\Scripts\python.exe -m bandit -r cli core utils services models alexa

# Tests
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -q --tb=line
```

---

## 🌐 Commandes Globales (hors venv)

### Installation globale des outils

```powershell
python -m pip install --upgrade black isort ruff flake8 mypy bandit vulture pylint pydocstyle pytest
```

### Vérification de l'environnement (global)

```powershell
python --version
python -m pip list | findstr -E "(black|isort|ruff|flake8|mypy|bandit|vulture|pylint|pydocstyle|pytest)"
```

### Tests complets (global avec chemins complets)

```powershell
# Formatage
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\black.exe cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\isort.exe cli core utils services models alexa

# Linting
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\ruff.exe check --fix cli core utils services models alexa
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\flake8.exe cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291

# Types
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\mypy.exe cli core utils services models --ignore-missing-imports

# Sécurité
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\bandit.exe -r cli core utils services models alexa

# Tests
C:\Users\weedm\AppData\Roaming\Python\Python313\Scripts\pytest.exe Dev/pytests/ -q --tb=line
```

### Nettoyage des caches (global)

```powershell
Remove-Item -Recurse -Force __pycache__,*.pyc,.mypy_cache,.ruff_cache -ErrorAction SilentlyContinue
```

---

## 🗂️ Générateur de rapports d'API (`Dev/utils/generate_api_reports.py`)

Ce petit utilitaire lit les échantillons JSON dans `Dev/api_samples/` et produit :

- `Dev/docs/api_samples_summary.md` — résumé et exemples
- `Dev/qualitytests/reports/notifications_stats.json` — statistiques agrégées
- `Dev/qualitytests/reports/devices_map.json` — liste des devices (JSON)

Usage depuis le dépôt (PowerShell) :

```powershell
# exécution avec chemins par défaut
python Dev\utils\generate_api_reports.py

# override des chemins
python Dev\api_reports\generate_api_reports.py --samples-dir Dev\api_samples --out-docs Dev\docs --out-analysis Dev\qualitytests\reports
```

Notes:

- Le générateur est non-destructif et lit uniquement les fichiers JSON. Il peut être invoqué depuis la CI ou localement.
- Si vous préférez CSV pour l'analyse, la version actuelle génère JSON (pour conserver la structure complète des objets).
