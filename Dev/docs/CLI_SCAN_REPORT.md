# Rapport de scan — dossier `cli/`

Objectif : fournir un inventaire clair des fichiers, indiquer quels fichiers utilisent le modèle legacy (`BaseCommand`) vs le modèle DI (`ManagerCommand`), et proposer une feuille de route de consolidation non-invasive.

---

## Inventaire rapide (fichiers racine)

- `alexa_cli.py` — point d'entrée CLI (orchestration, enregistrement des commandes via `register_all_commands`, création du context et exécution). Utilise `BaseCommand` pattern (instancie `command = command_class(context)` puis `success = command.execute(args)`).
- `base_command.py` — modèle legacy `BaseCommand` (synchronous). Contient utilitaires partagés (formatage, output, validation de connection, helpers pour appeler managers depuis `context`).
- `command_template.py` — nouveau modèle `ManagerCommand` (async execute() + DI via `DIContainer`).
- `command_adapter.py` — adapter / factory entre patterns. J'ai appliqué un correctif pour exécuter correctement `ManagerCommand` (utilise `validate_and_execute`) et injecter `di_container` via `setattr`.
- `command_parser.py` — wrapper argparse pour enregistrement des catégories; crée une instance temporaire de la commande pour configurer le parser (potentiel point d'amélioration pour `ManagerCommand`).
- `context.py` — contexte concrete (lazy-load managers) utilisé par `BaseCommand`; crée/instancie managers directement (actuellement n'utilise pas le `di_container` central, même si ce dernier existe dans `core/di_container.py`).
- `types.py` — `ContextProtocol` (typing) utilisé par les commandes.
- `command_examples.py` — exemples de `ManagerCommand` (démonstration) — non utilisés par la CLI principale.

## Inventaire des commandes concrètes (dossier `cli/commands/`)

Tous les fichiers listés contiennent des classes de commandes héritant de `BaseCommand`. Exemples :

- `auth.py` — `AuthCommand(BaseCommand)`
- `device.py` — `DeviceCommand(BaseCommand)`
- `device_communicate.py` — `DeviceCommunicateCommand(BaseCommand)`
- `music.py`, `music_playback.py`, `music_playback_commands.py` — lectures et commandes musicales (BaseCommand)
- `timers.py`, `timers_alarm.py`, `timers_reminder.py`, `timers_countdown.py` — timers et sous-catégories
- `alarm.py`, `reminder.py` — commandes liées (BaseCommand)
- `favorite.py`, `lists.py`, `dnd.py`, `calendar.py`, `routine.py`, `scenario.py`, `multiroom.py`, `smarthome.py`, `cache.py`, `announcement.py`, `activity.py`, etc.

Remarque : `command_examples.py` contient `ManagerCommand`-based examples, mais ils ne sont pas wired dans `alexa` (register_all_commands uses the BaseCommand classes from `cli.commands`).

## Observations et risques

1. Majorité des commandes utilisent `BaseCommand`. Migration à `ManagerCommand` est un effort manuel par commande.
2. `alexa_cli.py` instancie la commande via `command_class(context)` et appelle `command.execute(args)` — ceci suppose `execute` est synchrone (BaseCommand). Tant que les commandes restent legacy, le runtime est correct.
3. `CommandParser.register_command` instancie une instance temporaire `temp_instance = command_class(context=None)` pour configurer le parser. Ceci casse si une `ManagerCommand` n'accepte pas `context=None` ou a signature différente; une solution consiste à standardiser une méthode de classe `setup_parser(cls, parser)` pour éviter instantiation au registre.
4. `Context` crée ses propres managers, contournant partiellement le DI central : il faut un plan pour harmoniser `Context` et `di_container`.

## Recommandations immédiates (Phase A safe actions)

Priorité A (faible risque) — conserver compatibilité et clarifier l'architecture :

- 1. Garder `BaseCommand` en place durant la migration. Migration command-by-command.
- 2. Conserver `command_adapter.CommandAdapter` comme point unique pour obtenir `di_container` et managers. Correction appliquée : `execute_command` now handles `ManagerCommand` correctly.
- 3. Ajouter un decorateur ou méthode statique `setup_parser` pour `ManagerCommand` afin que `CommandParser.register_command` puisse configurer le parser sans instancier de commande. Implémentation progressive : si `command_class` a `setup_parser` en méthode de classe, l'utiliser ; sinon, instancier temporairement (fallback). Cela permet d'enregistrer proprement les `ManagerCommand` quand on en migrera.

Priorité B (moyen risque) — harmonisation :

- 4. Exposer `di_container` dans `cli/context.py` (`self.di_container = get_di_container()`), et adapter `Context` pour que les propriétés lazy-loaded essayent d'obtenir le manager depuis le DI si disponible. Migration par manager (device, playback, timers...).
- 5. Écrire tests unitaires pour chaque commande migrée, vérifier compatibilité avec `alexa_cli.main()`.

Priorité C (après migration) — nettoyage :

- 6. Une fois majoritairement migré, retirer `BaseCommand` et `CommandAdapter` et simplifier `alexa_cli.py` pour créer `ManagerCommand` via `CommandFactory`.
- 7. Flatten les packages `core/*` qui ne contiennent qu'un seul module (après validation tests).

## Plan concret — petites étapes (safe, 1-2 fichiers par PR)

1. Fix minimal (je l'ai appliqué) : `cli/command_adapter.execute_command` -> done.
2. Add support for class-based setup_parser for `ManagerCommand` (change `command_parser.register_command`) — small patch + tests.
3. Add `cli/context` attribute `di_container` and adapt one manager to use it (e.g., `device_mgr`) — test and commit.
4. Migrate commands in priority order: device, timers, music playback, lists, reminders. Each migration:
   - Implement new `ManagerCommand` subclass (or adapt existing command to ManagerCommand)
   - Provide `setup_parser` classmethod for argparse config
   - Update `alexa.register_all_commands` to register the new class
   - Add unit tests and run local suite
5. After a batch of 3-5 commands migrated, run full test suite and open PR.

## Fichiers à considérer pour flattening (cibles potentielles)

- `core/reminders` -> flatten to `core/reminder_manager.py` (if only one file)
- `core/alarms` and `core/timers` -> consider merging alarm logic into `core/timers` if APIs converge
- `cli/command_examples.py` -> move under `cli/examples/` or `cli/commands/_examples.py`

## Livrables que je peux produire maintenant

- Patch pour `command_parser.register_command` afin de supporter `ManagerCommand.setup_parser(cls, parser)` (si tu veux, je peux l'implémenter maintenant).
- Script d'inventaire plus détaillé (CSV/JSON) listant chaque commande, sa classe, et si elle est ready-for-migration.
- Lancement des tests CLI adaptés.

---

Fin du rapport. Si tu veux que j'applique directement l'une des recommandations (par ex. modifier `command_parser.register_command` pour supporter `ManagerCommand`), dis laquelle et je le fais en mode développeur (patch + tests ciblés et run des tests).
