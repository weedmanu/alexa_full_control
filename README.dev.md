README - développement local

But: guide minimal pour contributeurs et instructions de test local.

Prerequis

- Python 3.8+
- Optional: graphviz, plantuml (pour diagrammes)

Installer l'environnement virtuel (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Exécuter les tests et la couverture:

```powershell
python -m pytest --cov=scripts --cov-report=term-missing
```

Configurer pre-commit:

```powershell
python -m pip install pre-commit
pre-commit install
```

Notes

- `requirements-dev.txt` contient des versions minimales recommandées; pinnez les versions pour CI si nécessaire.
- Pour reproduire les diagrammes, installez `graphviz` via votre gestionnaire système et `plantuml` si nécessaire.

## Quick developer commands

Quelques commandes pratiques (PowerShell) après avoir activé `.venv` :

```powershell
# installer les dépendances de dev
pip install -r requirements-dev.txt

# installer pre-commit hooks
pre-commit install

# lancer vulture (détection de code mort)
vulture . --config .vulture.toml

# lancer les tests unitaires
python -m pytest -q

# lancer un petit benchmark (si vous avez pytest-benchmark)
python -m pytest --benchmark-only

# profiler une exécution de tests avec pyinstrument
pyinstrument -o profile.html python -m pytest tests/pytest_install.py
start profile.html
```

## Utilitaires fournis

J'ai ajouté des scripts dans `scripts/dev_tools.ps1` et `scripts/dev_tools.sh` et une cible `Makefile` pour exécuter rapidement ces commandes sur Windows/Linux.
