# Architecture attendue du projet Alexa Voice Control

But: documenter l'architecture cible pour prendre des décisions sûres de suppression/flattening.

## Principes généraux

- Single responsibility: chaque module/paquet a une responsabilité claire et limitée.
- DI centralisée: `core/di_container.py` doit fournir les managers/services partagés (singletons ou factories). Les managers doivent préférer obtenir leurs dépendances via le DI container.
- Non-invasive migration: pendant la phase 1, garder des fallbacks (ex: managers acceptent `api_service` optionnel) et ne pas casser les API publiques.
- Tests obligatoires: tout mouvement de fichier ou suppression doit être accompagné d'un test unitaire et d'une validation de la suite de tests existante.
- Backward compatibility: CLI historique (`BaseCommand`) doit fonctionner pendant la migration; la coexistence est autorisée mais limitée dans le temps.

## Composants clés attendus

- `alexa` (point d'entrée)
  - Orchestration CLI, registration commands, configuration logging
- `cli/`

  - `command_template.py`: nouveau modèle orienté DI (ManagerCommand)
  - `base_command.py`: legacy BaseCommand (à migrer progressivement)
  - `command_adapter.py`: adapter temporaire pour compatibilité pendant migration
  - `command_parser.py`: centraliser argparse
  - `context.py`: wrapper simple pour tests mais favoriser l'utilisation du DIContainer
  - `commands/`: commandes concrètes; migrer progressivement vers `ManagerCommand`

- `core/`

  - Managers métiers (DeviceManager, TimerManager, AlarmManager, etc.)
  - `di_container.py`: conteneur d'injection des dépendances
  - `manager_factory.py`: mapping et construction des managers

- `services/`

  - `alexa_api_service.py`: abstraction centrale pour appels HTTP vers Alexa
  - autres services utilitaires (cache, favorites, voice command)

- `utils/`: utilitaires (http client, storage, logger)

## Règles de consolidation / suppression

1. Un sous-package de `core/` ou `cli/` contenant un seul module (ex: `core/reminders/reminder_manager.py`) peut être remonté d'un niveau (flatten) si:
   - Il n'y a pas d'autres modules liés (helpers, tests spécifiques) dans ce sous-package.
   - Les imports relatifs sont mis à jour et tous les tests passent.
2. Supprimer un module uniquement si:
   - Il est clairement déprécié (documenté) ET
   - Aucune autre partie du code n'importe le symbole (vérifier via grep search). Faire une PR dédiée contenant le move/delete et la mise à jour des imports.
3. Fusions possibles:
   - `core/timers` et `core/alarms` contiennent des logiques proches: proposer de garder `core/timers` et d'intégrer `alarms` s'ils partagent le même contrat et API interne.
   - `core/reminders` peut devenir `core/alerts` si convergence.

## Conversion CLI – stratégie

- Court terme (Phase 1): Adapter les commandes existantes pour supporter DI via `CommandAdapter`. Corriger l'exécution async des `ManagerCommand`.
- Moyen terme (Phase 2): Migrer commandes de `cli/commands/*` vers `ManagerCommand` une par une; ajouter `setup_parser` statique/cls pour éviter instanciation à l'enregistrement.
- Long terme (Phase 3): Retirer `BaseCommand` après migration complète et simplifier `cli/` (moins de couches d'adaptation).

## Critères d'acceptation pour suppression/flatten

- Tous les tests unitaires et d'intégration passent localement et en CI.
- Documentation mise à jour (`Dev/docs/`) et changelog.
- PR atomique: un commit -> une suppression/move.

## Roadmap de suppression safe (exemple pour `core/alarms`)

1. Créer branche `refactor/flatten-alarms`.
2. Déplacer `core/alarms/alarm_manager.py` -> `core/alarm_manager.py` (patch de moves, update imports).
3. Exécuter la suite tests unitaires ciblés.
4. Corriger imports brisés et lancer test complet.
5. Ouvrir PR avec description et checklist.

## Notes opérationnelles

- Avant chaque move: exécuter `grep` sur le repo pour lister usages.
- Fournir un script de migration (optionnel) pour mettre à jour les imports automatiquement.

---

Ce document servira comme source d'autorité pour décider quels dossiers/fichiers remonter ou supprimer en Phase A/B.
