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
$(git diff --name-only origin/main...HEAD)
```

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
