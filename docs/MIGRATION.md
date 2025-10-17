# Migration vers AlexaAPIService

Ce document décrit les étapes recommandées pour migrer les managers et services afin d'utiliser `AlexaAPIService`.

But

- Remplacer tous les appels directs `self._auth.get/post` et les endpoints hardcodés par des appels via `AlexaAPIService`.
- Effectuer la migration par lots pour limiter la surface de régression.

Pré-requis

- `services/alexa_api_service.py` disponible et injectable
- Tests unitaires positionnés et exécutables
- `tools/audit_api_calls.py` exécuté pour récolter les endpoints

Stratégie générale

1. Audit: exécuter `python tools/audit_api_calls.py` et examiner `docs/endpoints_mapping.json`.
2. Créer une branche feature: `git checkout -b feature/phase1-api-centralization/<batch-name>`
3. Migrer un manager (ex: device_manager):
   - Injecter `AlexaAPIService` dans le constructeur
   - Remplacer `self._auth.get/post` par `self._api_service.<method>`
   - Adapter les tests (mock de `AlexaAPIService` au lieu d'AlexaAuth)
   - Exécuter les tests unitaires du manager
   - Commit atomique: `refactor(<manager>): migrate to AlexaAPIService`
4. Pousser la branche et ouvrir PR
5. Répéter par lots (music, multiroom, routines, etc.)

Bonnes pratiques

- Un seul manager modifié par commit.
- Tests verts locaux avant push.
- Utiliser des commits atomiques et messages descriptifs.
- Ajoutez un test d'intégration léger après chaque batch pour valider l'injection.

Commandes utiles

```powershell
# Créer une branche pour le batch "device"
git checkout -b feature/phase1-api-centralization/device

# Exécuter tests pour le manager
pytest Dev/pytests/core/managers/test_device_manager.py -v

# Rechercher occurrences restantes après migration
python tools/audit_api_calls.py
# Vérifier qu'aucune occurrence de self._auth.post/get n'existe dans core/managers
grep -R "self\._auth\.post\|self\._auth\.get" core/managers || echo "No direct auth calls found"
```

Rollback

- Si une migration casse trop de tests, revert le commit et crée une branche secondaire pour isoler les modifications.

Checklist avant merge

- [ ] Tous les tests unitaires pour le manager passent
- [ ] Pas de `self._auth.post/get` restant dans le manager
- [ ] Ajout d'un test qui vérifie l'injection d'`AlexaAPIService` (mock)
- [ ] Documentation et message de commit explicite

Notes

- Préférer l'injection via `di_container`/`di_setup` si possible pour simplifier la propagation de dépendances.
- Si `AlexaAPIService` n'est pas encore implémenté complètement, injecter un stub pour avancer sur la migration des tests.
