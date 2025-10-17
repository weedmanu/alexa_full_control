# Guide court — Développement professionnel

Ce document donne des recommandations concrètes et applicables pour travailler sur ce dépôt en mode "développement professionnel" : workflow Git, bonnes pratiques pour les PR, tests, revue et CI. Il est volontairement concis.

## 1 — Workflow Git

- Créez une branche par fonctionnalité ou correctif : `feature/<objet>` ou `fix/<objet>`.
- Faites des commits atomiques et bien nommés (`type(scope): courte description`), par exemple : `feat(cli): add ManagerCommand pilot for device` ou `docs: update CLI scan report`.
- Gardez vos commits petits et réversibles — évitez les gros monoblocs.
- Rebase interactif pour nettoyer l'historique avant PR : `git fetch origin; git rebase -i origin/main` (ou la branche de base).

## 2 — Préparer une Pull Request (PR)

- Rédigez un titre clair et une description courte (problème, solution, impact, tests exécutés).
- Ajoutez une checklist (tests unitaires, tests d'intégration, lint, manuels) et cochez les éléments passés.
- Regroupez les changements logiquement : code, tests et docs séparés si possible.
- Décrivez les risques et les mesures de mitigation (retours en arrière, fallbacks).

## 3 — Tests et validation locale

- Exécutez d'abord les tests unitaires ciblés lors d'un changement :

```powershell
python -m pytest -q -k "<mot-clé>"
```

- Ensuite lancez la suite complète avant d'ouvrir la PR :

```powershell
python -m pytest -q
```

- Ajouter des tests unitaires pour toute logique métier nouvelle ou modifiée. Un test d'intégration léger pour Phase1 est conseillé.

## 4 — Linter, types et qualité

- Exécutez un linter (par ex. `ruff` ou `flake8`) et un outil de typecheck (par ex. `mypy`) si configurés.
- Corrigez les warnings critiques ; pour les warnings non-fixés, documentez-les dans la PR avec un plan d'actions.

## 5 — Revue de code

- Fournissez un contexte succinct dans la PR (pourquoi le changement est nécessaire).
- Les reviewers doivent vérifier : tests, compatibilité descendante, documentation, risques de sécurité.
- Privilégiez des commentaires constructifs et demandez des modifications claires (ou proposez des patches).

## 6 — CI / Déploiement

- Assurez-vous que la CI exécute les tests et le linter automatiquement.
- N'acceptez pas de PR avec des tests cassés en CI.

## 7 — Bonnes pratiques spécifiques pour cette refactorisation Phase1 (DI)

- Pattern non-invasive : préférez ajouter un paramètre optionnel `api_service` aux managers et garder le fallback `_api_call`.
- Ajoutez des tests qui valident à la fois le chemin via `AlexaAPIService` et le fallback legacy.
- Effectuez des migrations par lots (petites étapes), validez chaque lot via tests unitaires ciblés.

## 8 — Format de commit et messages

- Utilisez le style "conventional commits" léger : `type(scope): message`.
- Types recommandés : `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

## 9 — Règles d'urgence / rollback

- Si un changement casse la CI ou la production, ouvrez un revert minimal avec `git revert` du commit problématique.
- Documentez l'incident dans l'issue correspondante et notez la stratégie corrective.

## 10 — Ressources et contact

- Lisez `Dev/docs/Refacto_phase1.md` pour la stratégie complète de migration.
- Pour questions d'architecture, contactez le responsable du refactor (indiqué dans le README ou le ticket associé).

---

Gardez ce guide court à portée de main et référez-vous-y lors des PRs pour garder une qualité et une traçabilité constantes.
