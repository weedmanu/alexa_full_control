# 🔧 Guide de Développement - Setup & QA Tools

**Date** : 16 octobre 2025  
**Version** : 2.0.0  
**Public** : Développeurs contribuant au projet

---

## 🎯 Objectif

Guide complet pour configurer l'environnement de développement, exécuter les outils de qualité, et comprendre l'architecture du projet.

---

## 📋 Prérequis

- **Python 3.11+** (testé sur 3.11, 3.12)
- **Git** (pour le versioning)
- **Node.js 18+** (pour l'authentification, installé via `nodeenv`)
- **PowerShell 5.1+** sur Windows ou **Bash** sur Unix/macOS

---

## 🚀 Installation Initiale

### 1. Cloner le Dépôt

```bash
git clone https://github.com/weedmanu/alexa_full_control.git
cd alexa_full_control
```

### 2. Configuration Python (Windows PowerShell)

```powershell
# Créer environnement virtuel à la racine
python -m venv .venv

# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Installer dépendances de développement
pip install -r requirements-dev.txt
```

### 3. Configuration Python (Unix/macOS)

```bash
# Créer environnement virtuel à la racine
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Installer dépendances de développement
pip install -r requirements-dev.txt
```

### 4. Installation Complète (Auth Node.js + CLI)

```bash
# Windows
python scripts/install.py

# Unix/macOS
python3 scripts/install.py
```

---

## 🏗️ Architecture du Projet

### Structure des Répertoires

```
alexa_full_control/
├── .venv/                    # Environnement virtuel (racine, exclusif)
├── alexa                     # Point d'entrée CLI (exécutable)
├── alexa_auth/               # Authentification
│   ├── alexa_auth.py        # Gestion cookies/tokens
│   ├── nodejs/              # Backend Node.js (cookie retrieval)
│   └── data/                # Fichiers cookies (alexa_auth/data/)
├── cli/                      # Interface CLI
│   ├── commands/            # Commandes par catégorie
│   └── help_texts/          # Aides (générées automatiquement)
├── core/                     # Logique métier
│   ├── base_manager.py      # Classe de base (cache, API)
│   ├── device_manager.py    # Gestion appareils
│   └── [autres managers]    # Autres fonctionnalités
├── services/                 # Services métier
│   ├── cache_service.py     # Cache disque
│   └── voice_command_service.py # Commandes vocales
├── utils/                    # Utilitaires
│   ├── logger.py            # Logging
│   ├── http_client.py       # Client HTTP
│   └── colorizer.py         # Couleurs CLI
├── Dev/                      # Outils de développement
│   ├── tools/               # Scripts de QA
│   │   └── run_tests.ps1   # QA runner Windows
│   └── docs/                # Documentation
├── pyproject.toml           # Configuration Poetry
├── requirements.txt         # Dépendances production
├── requirements-dev.txt     # Dépendances développement
└── Makefile                 # Commandes raccourcies
```

### Points Clés d'Architecture

- **`.venv` à la racine exclusivement** : Tous les outils dev utilisent cet environnement
- **Authentification Node.js** : Conservée sous `alexa_auth/nodejs/` (voir `install.py` pour l'installer)
- **Données cookies** : `alexa_auth/data/` (JSON + TXT)
- **Tous les outils dev** : Dans `Dev/tools/` ou racine (`dev_quality.py`)
- **Tous les logs/cache** : `logs/` et `.cache/` (générés, pas versionnés)

---

## 🔧 Outils de Qualité de Code

### QA Runner Principal

```powershell
# Windows - Tous les outils
.\Dev\tools\run_tests.ps1 -All

# Ou depuis Python
python dev_quality.py --all

# Traiter Bandit/Safety comme des erreurs (strict)
.\Dev\tools\run_tests.ps1 -All -FailOnSecurity
```

```bash
# Unix/macOS - Tous les outils
bash Dev/tools/run_tests.sh --all

# Ou depuis Python
python dev_quality.py --all
```

### Outils Individuels

```bash
# Formatage (Black)
python dev_quality.py --black

# Imports (isort)
python dev_quality.py --isort

# Style (Ruff, Flake8)
python dev_quality.py --ruff
python dev_quality.py --flake8

# Typage (Mypy)
python dev_quality.py --mypy

# Tests & Coverage
python dev_quality.py --pytest
python dev_quality.py --coverage

# Sécurité
python dev_quality.py --bandit
python dev_quality.py --safety

# Code mort (Vulture)
python dev_quality.py --vulture
```

### Tests Spécifiques

```bash
# Tests d'intégration
pytest Dev/pytests/test_integration.py -v

# Tests de performance
pytest Dev/pytests/test_performance.py -v

# Un test spécifique
pytest Dev/pytests/ -k test_device_list -v
```

---

## 📊 Configuration QA

### Black (Formatage)

```
# Largeur ligne : 100 (configurable dans pyproject.toml)
# Target version : 3.11
```

### Ruff (Linting)

```
# Remplace Pylint, plus rapide
# Config dans pyproject.toml [tool.ruff]
```

### Mypy (Typage Statique)

```
# Mode strict activé
# Config dans mypy.ini
```

### Pytest (Tests)

```
# Coverage minimum : 60%
# Config dans pyproject.toml [tool.pytest.ini_options]
```

---

## 🛡️ Pre-commit Hooks

Automatiser la QA avant chaque commit :

```bash
# Installation
pip install pre-commit

# Configuration des hooks
pre-commit install

# Tester les hooks
pre-commit run --all-files

# Contournement (si urgent)
git commit --no-verify
```

**Fichier config** : `.pre-commit-config.yaml`

---

## 🚦 CI/CD - GitHub Actions

Le projet inclut un workflow GitHub Actions (`.github/workflows/ci.yml`) qui :

1. Exécute tous les outils QA à chaque push/PR
2. Cible les branches `main` et `refacto`
3. Fails le build si :
   - Mypy : erreurs typage
   - Black/Isort : formatage incorrect
   - Pytest : tests échouent
   - Coverage < 60%

**Vérifier le statut** : Voir l'onglet "Actions" sur GitHub

---

## 🔄 Workflow de Développement Recommandé

### Avant de Commencer

```bash
# 1. Mise à jour des branches
git fetch origin
git checkout main
git pull origin main

# 2. Créer une branche feature
git checkout -b feature/ma-fonctionnalite
```

### Pendant le Développement

```bash
# 1. Installer vos dépendances (si nouvelles)
pip install <package>
pip freeze > requirements.txt  # ou requirements-dev.txt

# 2. Écrire des tests d'abord (TDD)
pytest Dev/pytests/test_ma_feature.py -v

# 3. Exécuter les outils QA
python dev_quality.py --all

# 4. Fixer les erreurs
python dev_quality.py --black --fix
python dev_quality.py --isort --fix
python dev_quality.py --ruff --fix
```

### Avant de Pusher

```bash
# 1. Vérifier le status git
git status

# 2. Ajouter les changements
git add -A

# 3. Lancer la QA complète une dernière fois
python dev_quality.py --all

# 4. Commiter avec message explicite
git commit -m "feat: description de ma fonctionnalité"

# 5. Pusher
git push origin feature/ma-fonctionnalite
```

### Soumettre une PR

1. Aller sur GitHub
2. Créer une Pull Request vers `main`
3. Décrire les changements
4. Attendre que CI/CD passe
5. Demander une review

---

## 🐛 Débogage

### Logs Détaillés

```bash
# Activer debug logging
export DEBUG=true
python alexa device list

# Ou
DEBUG=true python alexa device list
```

### Inspecter les Requêtes API

```python
# Dans le code (temporaire)
import requests
requests.packages.urllib3.disable_warnings()

from utils.logger import setup_loguru_logger
setup_loguru_logger(level="DEBUG")
```

### Tests Locaux

```bash
# Run tests avec logs
pytest Dev/pytests/ -v -s

# Run avec couverture détaillée
pytest Dev/pytests/ --cov=core --cov-report=html
```

---

## 📚 Variables d'Environnement

| Variable                         | Valeur            | Usage                  |
| -------------------------------- | ----------------- | ---------------------- |
| `DEBUG`                          | `true`/`false`    | Logging verbose        |
| `ALEXA`                          | `alexa.amazon.fr` | Domaine Amazon         |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD` | `1`               | Éviter flakiness tests |

---

## 🆘 Dépannage

### Problème : Tests échouent avec `ImportError`

**Solution** :

```bash
# Vérifier que le .venv est activé
.\.venv\Scripts\Activate.ps1  # Windows

# Réinstaller les dépendances
pip install -r requirements-dev.txt
```

### Problème : Mypy errors sur les types

**Solution** :

```bash
# Vérifier la version Python
python --version  # Doit être 3.11+

# Forcer mypy à re-analyser
rm -rf .mypy_cache
python dev_quality.py --mypy
```

### Problème : Bandit/Safety warnings

**Solution** :

```bash
# Ces outils sont non-fatal par défaut
# Pour les forcer à fail la build :
.\Dev\tools\run_tests.ps1 -All -FailOnSecurity
```

---

## 📝 Logs et Rapports

### Générer un Rapport QA Complet

```bash
python dev_quality.py --all 2>&1 | tee qareport.txt
```

### Couverture de Code

```bash
pytest --cov=core --cov=cli --cov=services --cov-report=html
# Ouvre Dev/htmlcov/index.html
```

---

## 🔗 Ressources Utiles

- **Architecture** : `Dev/docs/ARCHITECTURE.md`
- **API Endpoints** : `Dev/docs/API_ENDPOINTS.md`
- **CLI Help** : `Dev/docs/CLI_HELP_GUIDE.md`
- **Logging** : `Dev/docs/LOGGING_SYSTEM.md`
- **Installation** : `Dev/docs/INSTALL_UNINSTALL.md`

---

**Dernière mise à jour** : 16 octobre 2025  
**Responsable** : M@nu
