# 🧪 Tests de Qualité - Commandes

**Setup:** `cd c:\Users\weedm\Downloads\alexa_full_control; .\.venv\Scripts\Activate.ps1`

---

## 1️⃣ BLACK

```powershell
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
.\.venv\Scripts\python.exe -m black cli core utils services models alexa
.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa
```

---

## 2️⃣ ISORT

```powershell
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort cli core utils services models alexa
.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa
```

---

## 3️⃣ RUFF

```powershell
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check --fix cli core utils services models alexa
.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa
```

---

## 4️⃣ FLAKE8

```powershell
.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291
```

---

## 5️⃣ MYPY

```powershell
.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports
```

---

## 6️⃣ PYTEST

```powershell
.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -q --tb=line
```
