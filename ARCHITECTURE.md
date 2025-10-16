# Architecture du projet Alexa Advanced Control

Ce document décrit la structure actuelle du dépôt, les composants principaux, le flux CLI, les outils de développement et quelques notes sur les récentes migrations (suppression de `help_texts`, intégration des outils dev dans `Dev/`, et emplacement de l'installateur).

## Arborescence principale

- `alexa/` : Entrée principale du paquet (logiciel Alexa). Contient le module principal.
- `cli/` : Interface en ligne de commande.
  - `cli/command_parser.py` : Construction du parser argparse et gestion du `formatter_class`.
  - `cli/alexa_cli.py` et `cli/commands/` : Sous-commandes modulaires pour actions (alarm, calendar, device, music, timers, etc.).
  - Les aides personnalisées `help_texts` ont été supprimées ; les descriptions utilisent maintenant les chaînes d'`argparse` standard.
- `core/` : Logique métier et managers (device_manager, activity_manager, dnd_manager, notification_manager, etc.).
- `services/` : Services de bas niveau (auth, cache_service, music_library, sync_service, voice_command_service).
- `utils/` : Utilitaires transverses (http_client, logger, term, help_formatter, smart_cache, etc.).
- `data/` : Données statiques et mapping utilisés par l'application.
- `models/` : Modèles de données utilisés par le projet.
- `alexa_auth/` : Authentification Amazon & utilitaires Node.js (sous-dossier `nodejs/`).
- `Dev/` : Outils et dépendances de développement.
  - `Dev/requirements-dev.txt` : Dépendances pour le développement (mypy, ruff, black, isort, pytest, pytest-cov, bandit, safety, vulture, pedostyle, ...).
  - `Dev/tests/` : Emplacement prévu pour les tests de développement (les tests unitaires et d'intégration doivent être placés ici).
- `install.py` : Script d'installation principal du projet (maintenu au niveau du projet — a été déplacé vers `Install/` si nécessaire).
- `dev_quality.py` : Runner Python pour exécuter linting, typage, tests, couverture et outils de sécurité.
- `run_tests.ps1`, `run_tests.sh` : Wrappers qui préparent (optionnellement) un environnement virtuel puis invoquent `dev_quality.py` ou d'autres outils via une variable `PYTHON_EXE`.

## Flux CLI

1. L'exécutable principal `alexa` appelle `cli/alexa_cli.py`.
2. Le `command_parser` construit l'arbre de sous-commandes à partir des fichiers dans `cli/commands/`.
3. Chaque commande implémente son propre comportement et appelle des managers dans `core/` et `services/`.
4. Les aides textuelles sont fournies inline via `argparse` (pas de modules `help_texts` externes).

## Outils de développement

- Typage : `mypy` (configuration stricte dans `mypy.ini`).
- Linting & formatting : `ruff`, `black`, `isort`.
- Tests : `pytest` (+ `pytest-cov` pour la couverture).
- Sécurité : `bandit`, `safety`.
- Autres : `vulture` (dead code), `pedostyle` (règles internes de qualité)
- Le runner `dev_quality.py` invoque ces outils via `sys.executable -m <tool>` pour garantir qu'ils s'exécutent dans le même interpréteur (et donc dans le même venv quand on l'utilise).

## Notes sur l'environnement et comportements récents

- Les wrappers `run_tests.ps1` / `run_tests.sh` supportent une option `--no-venv` pour forcer l'exécution hors d'un environnement virtuel. Par défaut, si elles créent/activent un `.venv`, le runner utilisera `sys.executable` pour exécuter les outils dans ce venv.
- Les échecs récents sur `coverage`, `bandit` ou `safety` sont généralement liés à des paquets manquants ou incompatibles dans l'environnement Python actif (installer `Dev/requirements-dev.txt` dans le venv résout la plupart des problèmes).

## Notes sur les changements récents

- La logique d'aide a été simplifiée : les modules `help_texts/` ont été retirés et les descriptions sont maintenant directement dans les commandes (argparse).
- `dev_quality.py` a été mis à jour pour intégrer `pedostyle` et pour utiliser `sys.executable` afin d'éviter d'exécuter les outils en dehors du venv si le runner est lancé depuis le venv.
- Un script d'installation multi-plateforme existe (`install.py`) qui gère la création du `.venv`, l'installation des dépendances Python et Node.js et la configuration du projet. Il bloque les opérations dangereuses si lancé depuis le `.venv` du projet.

## Emplacement des tests

- Les tests doivent être regroupés sous `Dev/tests/`.
- Supprimez les tests éphémères ou générés à la racine (ex : `tests/test_help_output.py`) pour éviter la confusion.

## Checklist de migration / tâches à suivre

- [x] Créer `architecture.md` à la racine (ce fichier).
- [ ] Déplacer les tests racine vers `Dev/tests` et supprimer la copie à la racine.
- [ ] Vérifier que `install.py` est bien positionné dans le code projet (`Install/` ou à la racine selon la préférence) et que `scripts/install.py` et autres wrappers sont cohérents.
- [ ] Optionnel : faire en sorte que `run_tests.*` installe automatiquement `Dev/requirements-dev.txt` dans le `.venv` s'il est absent (ajout d'un flag `--bootstrap`).

---

Fichier généré automatiquement par l'agent. Contribuez en ouvrant une PR si vous souhaitez modifier le style ou le contenu.
