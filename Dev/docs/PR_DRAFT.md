# Brouillon de PR : refacto-phase1-di-wiring

## Titre

refactor(di): phase1 - DI wiring and CLI ManagerCommand pilots

## Résumé

Ce PR propose une migration non-invasive vers un service centralisé `AlexaAPIService`, et prépare la base pour l'injection de dépendances progressive dans les managers. Les changements maintiennent la compatibilité descendante : les managers acceptent un paramètre optionnel `api_service` et retombent sur les appels historiques `_api_call` si le service n'est pas fourni.

Il contient également des modifications sûres dans la CLI pour permettre l'enregistrement et l'exécution de `ManagerCommand` (pattern async + DI) sans casser les commandes héritées `BaseCommand`. Trois pilotes (`device`, `timers`, `music_playback`) démontrent la migration progressive.

## Fichiers clés modifiés / ajoutés

- services/alexa_api_service.py (squelette, singleton dans DI)
- core/\* (migrations non-invasives partielles : reminders, playback, routines, lists, alarms, device tests)
- cli/command_adapter.py (exécution safe de ManagerCommand)
- cli/command_template.py (ajout d'un hook classmethod `setup_parser`)
- cli/command_parser.py (support pour `setup_parser` sans instanciation)
- cli/context.py (expose `di_container` dans le contexte CLI)
- cli/commands/device_manager.py (nouveau ManagerCommand pilote)
- cli/commands/timers_manager.py (nouveau ManagerCommand pilote)
- cli/commands/music_playback_manager.py (nouveau ManagerCommand pilote)
- Dev/docs/CLI_SCAN_REPORT.md (résultats du scan CLI)
- Dev/docs/EXPECTED_ARCHITECTURE.md (architecture cible)
- Dev/docs/design_alexa_api_service.md (design doc)

Liste complète des fichiers modifiés :

```text
.gitignore
AUDIT_ARCHITECTURE.md
AmeliorationV1.md
Dev/config/pytest.ini
Dev/docs/CLI_SCAN_REPORT.md
Dev/docs/EXPECTED_ARCHITECTURE.md
Dev/docs/PROFESSIONAL_DEVELOPMENT.md
Dev/docs/PR_DRAFT.md
Dev/docs/Refacto_phase1.md
Dev/docs/Refacto_phase2.md
Dev/docs/Refacto_phase3.md
Dev/docs/TEST_RUN_INSTRUCTIONS.md
Dev/pytests/services/test_alexa_api_service.py
Dev/pytests/test_cli/__init__.py
Dev/pytests/test_cli/commands/test_favorite_command.py
Dev/pytests/test_cli/test_command_parser.py
Dev/pytests/test_cli/test_command_template.py
Dev/pytests/test_core/__init__.py
Dev/pytests/test_core/multiroom/test_multiroom_manager.py
Dev/pytests/test_core/scenario/__init__.py
Dev/pytests/test_core/scenario/test_scenario_manager.py
Dev/pytests/test_core/test_device_manager.py
Dev/pytests/test_core/test_di_injection.py
Dev/pytests/test_core/test_manager_injection.py
Dev/pytests/test_services/test_favorite_service.py
Dev/pytests/test_utils/test_json_storage.py
Dev/tests/run_scenario_tests.py
Dev/tests/test_scenario_all.py
Dev/tests/test_scenario_cli.py
alexa
cli/command_adapter.py
cli/command_parser.py
cli/command_template.py
cli/commands/__init__.py
cli/commands/device_manager.py
cli/commands/favorite.py
cli/commands/music_playback_manager.py
cli/commands/scenario.py
cli/commands/timers_manager.py
cli/context.py
cli/help_texts/activity_help.py
cli/help_texts/alarm_help.py
cli/help_texts/alexa_help.py
cli/help_texts/announcement_help.py
cli/help_texts/auth_help.py
cli/help_texts/cache_help.py
cli/help_texts/calendar_help.py
cli/help_texts/device_help.py
cli/help_texts/dnd_help.py
cli/help_texts/lists_help.py
cli/help_texts/multiroom_help.py
cli/help_texts/music_help.py
cli/help_texts/notification_help.py
cli/help_texts/reminder_help.py
cli/help_texts/routine_help.py
cli/help_texts/scenario_help.py
cli/help_texts/smarthome_help.py
cli/help_texts/timers_help.py
config/PHASE1_COMPLETE.md
config/README.md
config/__init__.py
config/constants.py
config/paths.py
config/settings.py
core/alarms/alarm_manager.py
core/base_persistence_manager.py
core/device_manager.py
core/di_container.py
core/dnd_manager.py
core/lists/lists_manager.py
core/manager_factory.py
core/multiroom/multiroom_manager.py
core/music/playback_manager.py
core/notification_manager.py
core/reminders/reminder_manager.py
core/routines/routine_manager.py
core/scenario/scenario_manager.py
core/settings/device_settings_manager.py
core/timers/timer_manager.py
docs/MIGRATION.md
docs/audit_report.md
docs/design_alexa_api_service.md
docs/endpoints_mapping.json
mypy.ini
pyproject.toml
requirements-dev.txt
services/alexa_api_service.py
services/favorite_service.py
utils/json_storage.py
utils/short_help_formatter.py
utils/text_utils.py
```

Changelog (résumé rapide) :

- Architecture : introduction du squelette `AlexaAPIService` et enregistrement via DI.
- CLI : ajout de pilotes `ManagerCommand` (device, timers, music playback), adaptation du parser/adapter pour supporter les nouveaux patterns.
- Core : migrations non-invasives pour plusieurs managers (reminders, playback, routines, lists, alarms) et tests unitaires associés.
- Docs & Tests : ajout de rapports d'audit, guides de migration, instructions de test, et mise à jour des tests unitaires et de scenario.

> Remarque : adapter la liste ci-dessus avant ouverture du PR si vous voulez exclure des fichiers temporaires.

## Checklist de validation locale (obligatoire avant merge)

- [ ] Exécuter la suite complète de tests :

```powershell
python -m pytest -q
```

- [ ] Tests ciblés CLI/adapters (vérifier que les pilotes fonctionnent) :

```powershell
python -m pytest -q -k "command or cli or adapter"
```

- [ ] Linter / typecheck (si applicable) :

```powershell
# exemple : ruff . && mypy
```

- [ ] Relire les docs : `Dev/docs/CLI_SCAN_REPORT.md`, `Dev/docs/EXPECTED_ARCHITECTURE.md`, `Dev/docs/design_alexa_api_service.md`

- [ ] Vérifier les commits atomiques et messages (one feature per commit)

- [ ] Préparer un changelog succinct décrivant le pattern de migration et la compatibilité descendante

## Notes d'implémentation

- Pattern de migration : non-invasive DI — ajouter un paramètre optionnel `api_service` aux constructeurs de managers et privilégier `self._api_service` si disponible ; sinon utiliser le fallback `self._api_call`.
- CLI : `ManagerCommand` doit implémenter `@classmethod setup_parser(cls, parser)` pour s'enregistrer sans instantiation. `CommandAdapter` exécute `ManagerCommand.validate_and_execute(args_dict)` (ou exécute la coroutine renvoyée si nécessaire).
- DI : `alexa_api_service` est enregistré dans `core/di_container.py` et exposé via `cli/context.py` pour usage progressif.

## Risques et points d'attention

- Risque de régression si un manager modifié est instancié ailleurs avec des paramètres différents. Mitigation : non-invasive — constructeur compatible.
- Types et lint : certains patterns dynamiques (injection via `setattr`, class-level parser hooks) peuvent déclencher des warnings. Ajout de tests et correction progressive recommandés.

## Étapes post-merge recommandées

- Migrer les managers restants par petits lots (Batch 2: dnd, notification, timers full)
- Ajouter tests d'intégration Phase1 (`Dev/pytests/integration/test_phase1_integration.py`)
- Mettre à jour la documentation d'architecture et le guide de migration

## Revue souhaitée

- Prioriser la vérification des tests unitaires et d'intégration
- Contrôler l'impact sur la CLI et la compatibilité ascendante

---

Fini. Mettre à jour la section "Fichiers modifiés" avant d'ouvrir la PR pour éviter d'inclure des changements accidentels.
