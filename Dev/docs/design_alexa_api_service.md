# Design: AlexaAPIService

## Objectif

Centraliser tous les appels HTTP destinés au service Alexa dans une unique couche testable et remplaçable : `AlexaAPIService`.

Contract (2–3 bullets)

- Entrées : endpoint key (ou chemin relatif), méthode HTTP, payload/params, headers optionnels, timeout et correlation_id optionnel.
- Sorties : données JSON décodées (dict/list) ou lève une exception typée `AlexaAPIError`.
- Modes d'échec : exceptions réseau (requests.exceptions.RequestException) mappées sur `NetworkError`, réponses HTTP non 2xx mappées sur `ApiError`, et fallback sur cache local en `CacheFallbackError` si activé.

## Comportement attendu

- Fournir des méthodes : `get(path, **kwargs)`, `post(path, **kwargs)`, `put(...)`, `delete(...)`.
- Résoudre un mapping `ENDPOINTS` (nom logique -> chemin relatif) : ex. `ENDPOINTS = {"devices": "/api/devices"}` et accepter soit la clé soit le chemin complet.
- Ajouter un `correlation_id` aux headers (`X-Correlation-ID`) si fourni pour tracer les requêtes.
- Gestion d'erreurs :

  - `AlexaAPIError` (base)
  - `ApiError(status: int, body: Any, endpoint: str)` pour réponses non-2xx
  - `NetworkError(cause: Exception)` pour exceptions requests
  - `CacheFallbackError` pour signaler que la valeur retournée provient du cache

- Circuit breaker : utiliser `pybreaker.CircuitBreaker` (optionnel dependency) pour protéger endpoints critiques. Le breaker est configurable par nom d'endpoint via `breaker_registry` (ou defaults).

- Cache fallback : utiliser `cache_service` (injection) si présent. Sur échec réseau / ApiError, si `cache_key` connu ou dérivable, retourner la valeur en cache et lever `CacheFallbackError` ou bien logger et re-raise selon `raise_on_fallback` flag.

## Thread-safety / sessions

- Réutiliser une `requests.Session` injectable (pour tests/mocking). Par défaut créer une session locale.
- Ne pas conserver d'état mutable côté service à part la session et la configuration immuable.

## Instrumentation & logging

- Chaque appel logge : correlation_id, endpoint/key, duration, status_code, and error if present.
- Exposer des hooks (callbacks) optionnels pour telemetry (ex: metrics increment).

## Usage minimal (pseudo)

```python
from services.alexa_api_service import AlexaAPIService

svc = AlexaAPIService(session=session, cache_service=cache, breaker_registry=breaker_registry)
devices = svc.get("devices")  # résout ENDPOINTS['devices'] -> '/api/devices'
```

## Tests à écrire (TDD)

- test_get_success_returns_json
- test_get_api_error_raises_ApiError
- test_get_network_error_raises_NetworkError_and_fallback_cache_returns_cache_value
- test_post_success_calls_session_post_with_headers_and_payload
- test_circuit_breaker_trips_after_failures

## Design details

- Méthode interne `_resolve_path(key_or_path)` : si `key_or_path` dans `ENDPOINTS` -> renvoie chemin; sinon si commence par `/` ou `http` -> renvoie tel quel.
- `_request(method, path, **kwargs)` : assembler headers (X-Correlation-ID), exécuter via `self._session.request(method, url, **kwargs)`, mesurer temps, décode JSON si possible, raise ApiError si status >= 400.
- Hook cache fallback : accept params `cache_key=None, raise_on_fallback=False`. Si exception et cache exists: logger.info + return cached value and raise CacheFallbackError if raise_on_fallback True else return cached payload.
- Breaker usage : `with self._breaker_for(endpoint).call():` ou utiliser l'api pybreaker wrapper. Fournir method wrapper `_call_with_breaker(endpoint, func)`.

## Backward compatibility

- Managers pourront recevoir optionnel `api_service: AlexaAPIService | None`. Si None, managers continuent d'utiliser l'implémentation legacy `_api_call(...)`.

## API shape examples

- get(path_or_key, params=None, timeout=10, correlation_id=None, cache_key=None, raise_on_fallback=False)
- post(path_or_key, json=None, timeout=10, headers=None, correlation_id=None)

## Implementation notes

- Dépendances : ajouter `pybreaker` au `Dev/requirements-dev.txt` et `requirements.txt` si besoin. Tests utiliseront `responses` ou `requests_mock` pour simuler endpoints.
- Écrire tests unitaires dans `Dev/pytests/services/`.

## Next steps

- Écrire les tests TDD (fichiers sous `Dev/pytests/services`) puis implémenter `services/alexa_api_service.py` en faisant passer les tests.
