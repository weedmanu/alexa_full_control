# Real-user tests (pytests_real_user_api)

Ce dossier contient des tests qui interrogent l'API Alexa réelle et qui
peuvent produire des échantillons JSON (dumps) pour inspection manuelle.

Principe de fonctionnement

- Par défaut la suite de tests fonctionne en "mock-first" : aucun cookie
  réel n'est utilisé, et les tests restent exécutables localement.
- Pour activer l'exécution contre l'API réelle, lancer pytest avec l'option
  `--real`. Exemple :

  ```powershell
  pytest --real
  ```

- Si `--real` est fourni, le runner va chercher `ALEXA_TEST_COOKIES` dans
  l'environnement. Si cette variable n'est pas définie, le dossier
  `Dev/pytests/pytests_real_user_api/data` sera utilisé comme fallback **seulement
  si** `--real` est présent.

Sécurité pour les tests mutatifs

- Les tests qui peuvent muter l'état (timers, DND, etc.) sont marqués
  `@pytest.mark.mutation` et ne s'exécutent que si 2 conditions sont vraies :

  1. des cookies réels ont été chargés avec succès, et
  2. la variable d'environnement `ALEXA_ALLOW_MUTATION` est définie (ex: `1`).

  Exemple pour exécuter les tests réels et autoriser les mutations :

  ```powershell
  $env:ALEXA_TEST_COOKIES = 'C:\chemin\vers\cookies'
  $env:ALEXA_ALLOW_MUTATION = '1'
  pytest --real
  ```

Fichiers de données et confidentialité

- Les réponses API sauvegardées sont stockées sous `api_samples/*.json`.
  Ces fichiers peuvent contenir des informations sensibles (identifiants
  d'appareil, tokens partiels). Ne jamais commiter/pusher ces fichiers sur
  un dépôt public.

Conseils pour push sécurisé

- Avant de pousser, nettoyez ou excluez les fichiers sensibles. Vous pouvez
  utiliser le script `clean_sensitive.ps1` fourni pour déplacer les fichiers
  sensibles hors de l'arborescence de travail.

Support

- Si tu veux que je restaure automatiquement l'état modifié par un test
  mutatif (ex: remettre DND à off), on peut convertir ces scripts en
  tests à sauvegarder l'état avant/après. Je peux aider à l'implémentation.
