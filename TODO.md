# 📋 TODO - Améliorations du Projet Alexa Full Control

**Date:** 16 octobre 2025  
**Branche:** refacto  
**Status:** 🟢 Code Quality Pass - Prêt pour améliorations architecturales

---

## 🎯 Analyse Globale

### État Actuel ✅

- **Code Quality:** 100% Pass (Black, isort, Ruff, Flake8)
- **Architecture:** Refactorisée (BaseManager eliminé 650+ lignes code dupliqué)
- **Thread-Safety:** Complète (RLock, état machine)
- **Caching:** 2-niveaux (mémoire + disque via CacheService)

### Opportunités d'Amélioration 🚀

1. **Redondance de Code:** Plusieurs managers non-BaseManager
2. **Inconsistance API:** Mélanges auth/http_client dans constructeurs
3. **Sécurité:** Headers CSRF dupliqués, gestion tokens
4. **Factorisation:** Patterns répétés dans CLI commands
5. **Distribution:** Tous managers créent leurs propres CircuitBreaker
6. **Configuration:** Config éparpillée, pas de validation centralisée

---

## 📑 Table des Matières

- [1. REDONDANCE & FACTORISATION](#1-redondance--factorisation)
- [2. ARCHITECTURE & DESIGN PATTERNS](#2-architecture--design-patterns)
- [3. SÉCURITÉ](#3-sécurité)
- [4. PERFORMANCE](#4-performance)
- [5. DISTRIBUTION & INITIALISATION](#5-distribution--initialisation)
- [6. INTÉGRATION CLI](#6-intégration-cli)
- [7. TESTS & VALIDATION](#7-tests--validation)
- [8. DOCUMENTATION](#8-documentation)

---

## 1. REDONDANCE & FACTORISATION

### 1.1 Merger Managers non-BaseManager dans BaseManager

**Impact:** 🔴 **CRITIQUE** | **Effort:** 🟡 **MOYEN** (2-3 jours)

**Problème:**

```
✗ RoutineManager: Duplicate circuit_breaker, cache_ttl, _lock, _api_call logic
✗ PlaybackManager: Duplicate state_machine, lock, headers construction
✗ TuneInManager: Duplicate http_client normalization logic
✗ LibraryManager: Duplicate cache logic
✗ ListsManager: Duplicate lock + state_machine check
```

**Managers à refactoriser (8 total):**

- `core/routines/routine_manager.py` - **~200 lignes** duplicates
- `core/music/playback_manager.py` - **~150 lignes** duplicates
- `core/music/tunein_manager.py` - **~80 lignes** duplicates
- `core/music/library_manager.py` - **~70 lignes** duplicates
- `core/lists/lists_manager.py` - **~60 lignes** duplicates
- `core/audio/bluetooth_manager.py` - **~50 lignes** duplicates
- `core/audio/equalizer_manager.py` - **~50 lignes** duplicates
- `core/settings/device_settings_manager.py` - **~60 lignes** duplicates

**Cible:** Réduire de **~560 lignes** code dupliqué

**Action:**

```python
# AVANT (8 managers)
class RoutineManager:
    def __init__(self, auth, config, state_machine=None, cache_service=None):
        self.breaker = CircuitBreaker(...)  # DUPLI
        self._lock = threading.RLock()      # DUPLI
        self.cache_service = cache_service or CacheService()  # DUPLI
        self._cache_ttl = 300               # DUPLI

# APRÈS (hérite BaseManager)
class RoutineManager(BaseManager[Dict[str, Any]]):
    def __init__(self, auth, config, state_machine=None, cache_service=None):
        super().__init__(
            http_client=create_http_client_from_auth(auth),
            config=config,
            state_machine=state_machine,
            cache_service=cache_service
        )
        # ✅ Hérite: breaker, _lock, cache_service, _api_call, headers, etc.
```

**Files à modifier:**

- [ ] `core/routines/routine_manager.py` - Hériter BaseManager
- [ ] `core/music/playback_manager.py` - Hériter BaseManager
- [ ] `core/music/tunein_manager.py` - Hériter BaseManager
- [ ] `core/music/library_manager.py` - Hériter BaseManager
- [ ] `core/lists/lists_manager.py` - Hériter BaseManager
- [ ] `core/audio/bluetooth_manager.py` - Hériter BaseManager
- [ ] `core/audio/equalizer_manager.py` - Hériter BaseManager
- [ ] `core/settings/device_settings_manager.py` - Hériter BaseManager

**Tests à ajouter:**

- [ ] `Dev/pytests/test_all_managers_inherit_base.py` - Vérifier tous managers héritent BaseManager
- [ ] Validation API calls uniformes

---

### 1.2 Centraliser Gestion CircuitBreaker

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (1-2 jours)

**Problème:**

```
Actuellement (33 instances CircuitBreaker distribuées):
- 15 instances dans core/managers
- 8 instances dans core/audio
- 5 instances dans core/music
- 5 instances autres

⚠️ Configuration incohérente:
  - DeviceManager: failure_threshold=3, timeout=30
  - AlarmManager: failure_threshold=2, timeout=20
  - PlaybackManager: failure_threshold=3, timeout=30
```

**Action:**

```python
# CRÉER: core/breaker_registry.py
class CircuitBreakerRegistry:
    """Registre centralisé des circuit breakers."""

    _registry = {}

    @classmethod
    def get_or_create(cls, name: str, **kwargs):
        """Récupère ou crée un breaker singleton."""
        if name not in cls._registry:
            config = cls.get_config(name)
            cls._registry[name] = CircuitBreaker(**config)
        return cls._registry[name]

    @classmethod
    def get_config(cls, name: str) -> Dict:
        """Configuration centralisée par manager."""
        configs = {
            "default": {"failure_threshold": 3, "timeout": 30, "recovery_timeout": 60},
            "music": {"failure_threshold": 2, "timeout": 20, "recovery_timeout": 40},
            "device": {"failure_threshold": 4, "timeout": 60, "recovery_timeout": 120},
        }
        return configs.get(name, configs["default"])

# DANS BaseManager
class BaseManager(Generic[T]):
    def __init__(self, ..., breaker_name: str = "default"):
        self.breaker = CircuitBreakerRegistry.get_or_create(breaker_name)
```

**Files à modifier:**

- [ ] `core/base_manager.py` - Intégrer registre
- [ ] `core/circuit_breaker.py` - Ajouter registry
- [ ] Tous 33 managers - Utiliser registre au lieu de créer localement

**Réductions:**

- Circuit breakers uniques par type: 15 au lieu de 33 (-54% mémoire)
- Configuration centralisée + testable

---

### 1.3 Extraire Patterns CLI Répétitifs

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (2-3 jours)

**Problème:**

```
Même pattern répété dans 15+ commands:

def execute(self, args):
    try:
        device_info = self.get_device_info(args.device)
        if not device_info:
            return False

        serial, device_type = device_info

        ctx = getattr(self, "context", None)
        if not ctx or not getattr(ctx, "manager_name", None):
            self.error("Manager non disponible")
            return False

        result = ctx.manager_name.do_something(serial, device_type, args.param)
        # ...
```

**Action:** Créer `CommandTemplate` base class

```python
# CRÉER: cli/command_template.py
class ManagerCommand(BaseCommand):
    """Template pour commandes utilisant managers."""

    manager_attr: str  # Ex: "device_mgr", "playback_mgr"

    def get_manager(self):
        """Récupère manager du contexte avec vérification."""
        ctx = getattr(self, "context", None)
        if not ctx:
            self.error("Contexte non disponible")
            return None

        manager = getattr(ctx, self.manager_attr, None)
        if not manager:
            self.error(f"{self.manager_attr} non disponible")
            return None
        return manager

    def execute_manager_action(
        self,
        manager_method: Callable,
        args: argparse.Namespace,
        action_name: str
    ) -> bool:
        """Exécute une action manager de façon uniforme."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info
            manager = self.get_manager()
            if not manager:
                return False

            result = manager_method(serial, device_type, *self.get_method_args(args))

            if result:
                self.success(f"✅ {action_name} réussi")
            else:
                self.error(f"❌ {action_name} échoué")
            return result
        except Exception as e:
            self.error(f"Erreur {action_name}: {e}")
            return False

    def get_method_args(self, args: argparse.Namespace) -> List[Any]:
        """À surcharger: retourner args additionnels pour la méthode."""
        return []

# UTILISATION
class PlayCommand(ManagerCommand):
    manager_attr = "playback_mgr"

    def execute(self, args):
        return self.execute_manager_action(
            self.get_manager().play,
            args,
            "Lecture"
        )
```

**Files à créer/modifier:**

- [ ] `cli/command_template.py` - Créer ManagerCommand base class
- [ ] `cli/commands/music/playback.py` - Refactoriser 8+ commands
- [ ] `cli/commands/device.py` - Refactoriser 5+ commands
- [ ] `cli/commands/alarm.py` - Refactoriser 4+ commands

**Impact:** Réduction **~300 lignes** code CLI dupliqué

---

## 2. ARCHITECTURE & DESIGN PATTERNS

### 2.1 Normaliser Initialisation Managers

**Impact:** 🟢 **BAS** | **Effort:** 🟡 **MOYEN** (1-2 jours)

**Problème:**

```python
# INCOHÉRENT - 3 patterns différents

# Pattern 1: auth + config
DeviceManager(auth, config, state_machine)

# Pattern 2: auth_or_http + config (PlaybackManager)
PlaybackManager(auth_or_http, config, state_machine)

# Pattern 3: Pas de state_machine par défaut
TuneInManager(auth_or_http, config, state_machine=None)

# Pattern 4: Lazy state_machine creation
class RoutineManager:
    def __init__(self, auth, config, state_machine=None):
        self.state_machine = state_machine or AlexaStateMachine()  # Lazy
```

**Solution - Factory Pattern:**

```python
# CRÉER: core/manager_factory.py
from dataclasses import dataclass
from typing import Type, TypeVar

@dataclass
class ManagerConfig:
    """Configuration centralisée pour tous les managers."""
    auth: Any
    config: Any
    state_machine: Optional[AlexaStateMachine] = None
    cache_service: Optional[CacheService] = None
    cache_ttl: int = 300
    breaker_name: str = "default"

    def __post_init__(self):
        """Valide et initialise les dépendances defaults."""
        if not self.state_machine:
            self.state_machine = AlexaStateMachine()
        if not self.cache_service:
            self.cache_service = CacheService()

class ManagerFactory:
    """Factory pour créer managers de façon uniforme."""

    _config: Optional[ManagerConfig] = None

    @classmethod
    def initialize(cls, config: ManagerConfig):
        """Initialise la configuration globale."""
        cls._config = config

    @classmethod
    def create(cls, manager_class: Type[T], **overrides) -> T:
        """Crée un manager avec configuration."""
        if not cls._config:
            raise RuntimeError("ManagerFactory non initialisé")

        # Fusionner config globale + overrides
        config = {**dataclasses.asdict(cls._config), **overrides}
        return manager_class(**config)

# UTILISATION
ManagerFactory.initialize(ManagerConfig(
    auth=auth,
    config=config,
    state_machine=state_machine,
    cache_ttl=300
))

device_mgr = ManagerFactory.create(DeviceManager)
playback_mgr = ManagerFactory.create(PlaybackManager, cache_ttl=600)
```

**Files à créer/modifier:**

- [ ] `core/manager_factory.py` - Créer factory + config
- [ ] `cli/context.py` - Utiliser factory pour initialiser managers
- [ ] Tous managers - Signature uniforme

---

### 2.2 Implémenter Repository Pattern pour Cache

**Impact:** 🟡 **MOYEN** | **Effort:** 🔴 **DIFFICILE** (3-4 jours)

**Problème:**

```python
# Actuellement: Cache mélangé avec logique métier
class DeviceManager(BaseManager):
    def get_devices(self, force_refresh=False):
        with self._lock:
            if self._cache and not force_refresh:
                return self._cache

            # API call + cache update
            response = self._api_call('get', '/api/devices-v2/device')
            devices = response.json() if response else []

            self._cache = devices
            self._cache_timestamp = time.time()
            return devices
```

**Solution - Repository Pattern:**

```python
# CRÉER: core/repositories/base_repository.py
class Repository(Generic[T]):
    """Pattern Repository avec abstraction cache."""

    def __init__(self, cache_service: CacheService, cache_ttl: int = 300):
        self.cache = cache_service
        self.cache_ttl = cache_ttl

    async def get(self, key: str, force_refresh=False) -> Optional[T]:
        """Récupère avec cache multi-niveaux."""
        if not force_refresh:
            # Cache mémoire
            cached = self._memory_cache.get(key)
            if cached:
                return cached

            # Cache disque
            cached = self.cache.get(key)
            if cached:
                self._memory_cache[key] = cached
                return cached

        # Récupère depuis source
        data = await self._fetch_source(key)
        if data:
            self.cache.set(key, data, ttl_seconds=self.cache_ttl)
            self._memory_cache[key] = data

        return data

    async def _fetch_source(self, key: str) -> Optional[T]:
        """À surcharger: récupère depuis API/DB/etc."""
        raise NotImplementedError

# CRÉER: core/repositories/device_repository.py
class DeviceRepository(Repository[Dict[str, Any]]):
    """Repository pour appareils."""

    def __init__(self, http_client: HTTPClientProtocol, config, cache_service):
        super().__init__(cache_service, cache_ttl=300)
        self.http_client = http_client
        self.config = config

    async def _fetch_source(self, key: str):
        """Récupère appareils depuis API."""
        response = self.http_client.get(
            f"https://{self.config.alexa_domain}/api/devices-v2/device"
        )
        response.raise_for_status()
        return response.json()

# UTILISATION
class DeviceManager(BaseManager):
    def __init__(self, ...):
        super().__init__(...)
        self.repository = DeviceRepository(
            self.http_client,
            self.config,
            self.cache_service
        )

    def get_devices(self, force_refresh=False):
        """Simplifié - logique métier séparée du cache."""
        return self.repository.get("devices", force_refresh)
```

**Bénéfices:**

- Séparation concerns (métier vs cache)
- Cache logic testable indépendamment
- Réutilisable dans services, CLI, API

**Files à créer:**

- [ ] `core/repositories/__init__.py`
- [ ] `core/repositories/base_repository.py` - Repository générique
- [ ] `core/repositories/device_repository.py`
- [ ] `core/repositories/alarm_repository.py`
- [ ] `core/repositories/timer_repository.py`
- [ ] `core/repositories/routine_repository.py`
- [ ] (+ 8 autres pour music, audio, etc.)

**Tests:**

- [ ] `Dev/pytests/test_repository_pattern.py`

---

## 3. SÉCURITÉ

### 3.1 Centraliser Gestion CSRF Tokens

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (2 jours)

**Problème:**

```python
# DUPLIQUÉ dans 50+ endroits:
headers = {
    "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))
}

# RISQUES:
✗ Pas de validation CSRF (accepte strings vides)
✗ Fallback implicite (auth vs http_client) - confus
✗ Pas de refresh CSRF après expiration
✗ Hardcodé partout
```

**Solution - Secure Headers Manager:**

```python
# CRÉER: core/security/csrf_manager.py
class CSRFManager:
    """Gestion centralisée CSRF tokens."""

    def __init__(self, auth: AlexaAuth):
        self.auth = auth
        self._csrf_cache = None
        self._csrf_timestamp = 0
        self._lock = threading.RLock()

    def get_csrf(self, validate=True) -> str:
        """Récupère CSRF token avec validation."""
        with self._lock:
            # Refresh si expiré (30 min)
            if self._should_refresh_csrf():
                self._refresh_csrf_from_auth()

            csrf = self._csrf_cache or ""

            if validate and not self._is_valid_csrf(csrf):
                raise SecurityError(f"CSRF token invalide: {csrf[:10]}...")

            return csrf

    def _should_refresh_csrf(self) -> bool:
        """Vérifie si refresh CSRF nécessaire."""
        return (time.time() - self._csrf_timestamp) > 1800  # 30 min

    def _is_valid_csrf(self, csrf: str) -> bool:
        """Valide format CSRF (pas vide, format Amazon)."""
        if not csrf or len(csrf) < 10:
            return False
        # Format typique: amzn.xx...
        return csrf.startswith("amzn.") or len(csrf) > 20

    def _refresh_csrf_from_auth(self):
        """Récupère CSRF depuis auth."""
        csrf = getattr(self.auth, "csrf", None)
        if csrf and self._is_valid_csrf(csrf):
            self._csrf_cache = csrf
            self._csrf_timestamp = time.time()

# CRÉER: core/security/secure_headers.py
class SecureHeadersBuilder:
    """Construit headers sécurisés de façon uniforme."""

    def __init__(self, config: Any, csrf_mgr: CSRFManager):
        self.config = config
        self.csrf_mgr = csrf_mgr

    def build(self, **extra_headers) -> Dict[str, str]:
        """Construit headers standards + extras."""
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Alexa-CLI/1.0",
            "Accept": "application/json",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Referer": f"https://{self.config.alexa_domain}/spa/index.html",
            "Origin": f"https://{self.config.alexa_domain}",
            "DNT": "1",
            "Connection": "keep-alive",
        }

        # CSRF sécurisé
        try:
            headers["csrf"] = self.csrf_mgr.get_csrf(validate=True)
        except SecurityError as e:
            logger.error(f"CSRF invalide: {e}")
            raise

        # Merge extras
        headers.update(extra_headers)
        return headers

# DANS BaseManager
class BaseManager:
    def __init__(self, ..., csrf_mgr: Optional[CSRFManager] = None):
        self.csrf_mgr = csrf_mgr or CSRFManager(self.auth)
        self.headers_builder = SecureHeadersBuilder(self.config, self.csrf_mgr)

    def _get_api_headers(self, extra=None):
        """Remplace ancienne logique."""
        return self.headers_builder.build(**(extra or {}))
```

**Files à créer/modifier:**

- [ ] `core/security/__init__.py`
- [ ] `core/security/csrf_manager.py` - CSRF centralisé
- [ ] `core/security/secure_headers.py` - Headers sécurisés
- [ ] `core/base_manager.py` - Intégrer SecureHeadersBuilder
- [ ] Tous managers - Utiliser `_get_api_headers()` uniformément

**Tests de sécurité:**

- [ ] `Dev/pytests/test_csrf_validation.py` - Validation tokens
- [ ] `Dev/pytests/test_headers_security.py` - Headers complets

---

### 3.2 Ajouter Sanitization & Validation Entrées

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (2-3 jours)

**Problème:**

```python
# ACTUELLEMENT: Pas de validation entrées
def create_alarm(self, device_serial: str, alarm_time: str, label: str = ""):
    # device_serial accepte n'importe quoi
    # alarm_time accepte n'importe quoi
    # label aceepte n'importe quoi (injections possibles)

    payload = {"label": label}  # 🚨 RISQUE INJECTION

def create_reminder(self, ..., text: str):
    payload = {"text": text}  # 🚨 RISQUE XSS/INJECTION
```

**Solution - Input Validators:**

```python
# CRÉER: core/security/validators.py
class InputValidator:
    """Validation centralisée des entrées."""

    @staticmethod
    def validate_device_serial(serial: str) -> str:
        """Valide numéro de série appareil."""
        if not serial or not isinstance(serial, str):
            raise ValueError("device_serial doit être string non-vide")
        if len(serial) < 8 or len(serial) > 50:
            raise ValueError(f"device_serial trop court/long: {len(serial)}")
        if not re.match(r'^[A-Z0-9-]+$', serial):
            raise ValueError(f"device_serial invalide: {serial}")
        return serial

    @staticmethod
    def validate_device_type(device_type: str) -> str:
        """Valide type appareil."""
        valid_types = {
            'ALEXA_CURRENT_DEVICE_TYPE',
            'ECHO_DOT', 'ECHO', 'ECHO_PLUS',
            'ECHO_SHOW', 'ECHO_SHOW_5', 'ECHO_SHOW_8',
            'ECHO_SPOT', 'ECHO_AUTO',
            'FIRE_TABLET', 'MOBILE'
        }
        if device_type not in valid_types:
            raise ValueError(f"device_type invalide: {device_type}")
        return device_type

    @staticmethod
    def validate_alarm_time(alarm_time: str) -> str:
        """Valide format temps alarme."""
        try:
            # Format: HH:MM ou ISO 8601
            if ':' in alarm_time:
                h, m = alarm_time.split(':')
                if not (0 <= int(h) <= 23 and 0 <= int(m) <= 59):
                    raise ValueError()
            else:
                datetime.fromisoformat(alarm_time)
            return alarm_time
        except:
            raise ValueError(f"Format time invalide: {alarm_time}")

    @staticmethod
    def sanitize_text(text: str, max_len: int = 500) -> str:
        """Nettoie texte (labels, descriptions, etc.)."""
        if not isinstance(text, str):
            raise ValueError("text doit être string")

        # Limite longueur
        if len(text) > max_len:
            raise ValueError(f"text trop long (max {max_len}): {len(text)}")

        # Enlève caractères contrôle
        text = ''.join(c for c in text if c.isprintable() or c in '\n\t')

        # Échappe caractères spéciaux pour JSON
        text = text.replace('\\', '\\\\').replace('"', '\\"')

        return text.strip()

# UTILISATION
class AlarmManager(BaseManager):
    def create_alarm(
        self,
        device_serial: str,
        device_type: str,
        alarm_time: str,
        label: str = ""
    ) -> Optional[Dict[str, Any]]:
        # Validation entrées
        device_serial = InputValidator.validate_device_serial(device_serial)
        device_type = InputValidator.validate_device_type(device_type)
        alarm_time = InputValidator.validate_alarm_time(alarm_time)
        label = InputValidator.sanitize_text(label, max_len=100) if label else ""

        # Reste du code...
```

**Files à créer/modifier:**

- [ ] `core/security/validators.py` - Créer InputValidator
- [ ] Tous managers - Ajouter validation entrées (20+ méthodes)
- [ ] CLI commands - Ajouter validation (`argparse` custom types)

**Tests:**

- [ ] `Dev/pytests/test_input_validation.py`

---

## 4. PERFORMANCE

### 4.1 Implémenter Pagination pour API Calls

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (1-2 jours)

**Problème:**

```python
# ACTUELLEMENT: Récupère tout d'un coup
def list_timers(self):
    response = self._api_call('get', '/api/timers')
    return response.json()  # Peut retourner 1000+ items

# 🐌 LENT si 1000+ timers/alarms/rappels
```

**Solution - Pagination Builder:**

```python
# CRÉER: core/pagination.py
class Pagination:
    """Pagination pour API calls."""

    def __init__(self, page_size: int = 100, max_pages: Optional[int] = None):
        self.page_size = page_size
        self.max_pages = max_pages

    def fetch_all(
        self,
        fetch_func: Callable,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Récupère tous les items pagine par page."""
        all_items = []
        page = 0

        while True:
            if self.max_pages and page >= self.max_pages:
                logger.warning(f"Limitation max_pages atteinte: {self.max_pages}")
                break

            # Ajouter pagination params
            params = kwargs.get('params', {})
            params['offset'] = page * self.page_size
            params['limit'] = self.page_size
            kwargs['params'] = params

            response = fetch_func(**kwargs)
            if not response or not response.get('items'):
                break

            items = response['items']
            all_items.extend(items)

            if len(items) < self.page_size:
                break  # Dernière page

            page += 1
            logger.debug(f"Fetched page {page}: {len(items)} items")

        return all_items

# UTILISATION
class AlarmManager(BaseManager):
    def list_alarms(self) -> List[Dict[str, Any]]:
        pagination = Pagination(page_size=50, max_pages=10)

        return pagination.fetch_all(
            self._api_call,
            method='get',
            endpoint='/api/alarms'
        )
```

**Files à créer/modifier:**

- [ ] `core/pagination.py` - Créer Pagination class
- [ ] `core/timers/alarm_manager.py` - Utiliser pagination
- [ ] `core/reminders/reminder_manager.py` - Utiliser pagination
- [ ] `core/alarms/alarm_manager.py` - Utiliser pagination

---

### 4.2 Async/Await pour Parallel API Calls

**Impact:** 🔴 **DIFFICILE** | **Effort:** 🔴 **DIFFICILE** (4-5 jours)

**Problème:**

```python
# ACTUELLEMENT: Séquentiel
def get_full_state(self, device_serial: str):
    player = self._api_call('get', '/api/np/player', params=...)   # 300ms
    media = self._api_call('get', '/api/media/state', params=...)  # 300ms
    queue = self._api_call('get', '/api/np/queue', params=...)     # 300ms
    # ⏱️ Total: ~900ms (séquentiel)
```

**Solution - Async Wrapper:**

```python
# CRÉER: core/async_wrapper.py
import asyncio

class AsyncBaseManager(BaseManager):
    """BaseManager avec support async/await."""

    async def _api_call_async(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Appel API asynchrone."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._api_call(method, endpoint, **kwargs)
        )

    async def _fetch_multiple(
        self,
        requests: List[Tuple[str, str, Dict]]
    ) -> List[Dict[str, Any]]:
        """Récupère plusieurs endpoints en parallèle."""
        tasks = [
            self._api_call_async(method, endpoint, **kwargs)
            for method, endpoint, kwargs in requests
        ]
        return await asyncio.gather(*tasks)

# UTILISATION
async def get_full_state_async(device_serial: str):
    requests = [
        ('get', '/api/np/player', {'params': {...}}),
        ('get', '/api/media/state', {'params': {...}}),
        ('get', '/api/np/queue', {'params': {...}}),
    ]
    results = await playback_mgr._fetch_multiple(requests)
    # ⏱️ Total: ~300ms (parallèle)
```

**Files à créer:**

- [ ] `core/async_wrapper.py` - AsyncBaseManager
- [ ] `core/music/playback_manager_async.py` - Version async

**Note:** À faire APRÈS Phase 1-3 (redondance éliminée)

---

## 5. DISTRIBUTION & INITIALISATION

### 5.1 Créer Dependency Injection Container

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (2 jours)

**Problème:**

```python
# ACTUELLEMENT: Initialisations dispersées dans cli/context.py (300+ lignes)
class Context:
    def __init__(self, auth, config):
        self.device_mgr = DeviceManager(auth, config, ...)
        self.alarm_mgr = AlarmManager(auth, config, ...)
        # ... 30 managers, code dupliqué
```

**Solution - DI Container:**

```python
# CRÉER: core/di_container.py
from typing import TypeVar, Generic, Callable, Dict, Any

T = TypeVar('T')

class DIContainer:
    """Conteneur IoC pour gestion dépendances."""

    def __init__(self):
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register_factory(self, name: str, factory: Callable):
        """Enregistre factory (nouvelle instance chaque fois)."""
        self._factories[name] = factory

    def register_singleton(self, name: str, factory: Callable):
        """Enregistre singleton (une seule instance)."""
        self._factories[name] = factory
        self._singletons[name] = None

    def get(self, name: str) -> Any:
        """Récupère instance."""
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]

        if name in self._factories:
            return self._factories[name]()

        raise KeyError(f"Service '{name}' non enregistré")

    def get_all(self) -> Dict[str, Any]:
        """Récupère tous les singletons."""
        return {
            name: self.get(name)
            for name in self._singletons
        }

# UTILISATION
# CRÉER: core/di_setup.py
def setup_container(auth: AlexaAuth, config: Config) -> DIContainer:
    """Initialise conteneur avec tous les managers."""
    container = DIContainer()

    # Singletons (une instance partagée)
    container.register_singleton(
        "state_machine",
        lambda: AlexaStateMachine()
    )
    container.register_singleton(
        "cache_service",
        lambda: CacheService()
    )

    # Managers
    container.register_singleton(
        "device_mgr",
        lambda: DeviceManager(
            auth,
            config,
            container.get("state_machine"),
            container.get("cache_service")
        )
    )

    container.register_singleton(
        "alarm_mgr",
        lambda: AlarmManager(
            auth,
            config,
            container.get("state_machine"),
            container.get("cache_service")
        )
    )

    # ... etc pour tous les 30+ managers

    return container

# DANS Context
class Context:
    def __init__(self, auth, config):
        self.container = setup_container(auth, config)

        # Lazy properties
        @property
        def device_mgr(self):
            return self.container.get("device_mgr")

        @property
        def alarm_mgr(self):
            return self.container.get("alarm_mgr")
```

**Files à créer/modifier:**

- [ ] `core/di_container.py` - Créer DIContainer
- [ ] `core/di_setup.py` - Setup conteneur
- [ ] `cli/context.py` - Utiliser DI container (réduire 300+ lignes)

---

## 6. INTÉGRATION CLI

### 6.1 Ajouter Autocomplete pour Arguments

**Impact:** 🟢 **BAS** | **Effort:** 🟡 **MOYEN** (2 jours)

**Problème:**

```bash
$ alexa device list --device <TAB>
# Rien n'apparaît - pas de completion

# Devrait proposer:
# - Noms devices depuis cache
# - Serials depuis API
```

**Solution - Argcomplete Integration:**

```python
# MODIFIER: cli/command_parser.py
import argcomplete

def setup_argcomplete(parser: argparse.ArgumentParser):
    """Configure argcomplete pour tous les parsers."""

    # Device completer
    def device_completer(prefix, **kwargs):
        """Complète names de devices."""
        try:
            ctx = Context.get_current()
            devices = ctx.device_mgr.list_devices()
            names = [d.get('deviceName', '') for d in devices]
            return [n for n in names if n.startswith(prefix)]
        except:
            return []

    # Ajouter à parser
    device_arg = parser.add_argument('--device', '-d')
    device_arg.completer = device_completer

    # Activer argcomplete
    argcomplete.autocomplete(parser)

# DANS cli/alexa_cli.py
parser = create_parser()
setup_argcomplete(parser)
```

**Installation:**

```bash
eval "$(register-python-argcomplete alexa)"
```

**Files à modifier:**

- [ ] `cli/command_parser.py` - Setup argcomplete
- [ ] `cli/alexa_cli.py` - Enable argcomplete

---

### 6.2 Ajouter Commandes Admin (setup, config, debug)

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (2 jours)

**Nouveaux Commands:**

```bash
# Setup initial
$ alexa admin setup

# Configuration
$ alexa admin config show
$ alexa admin config set DEBUG true
$ alexa admin config reset

# Debug/Diagnostics
$ alexa admin diagnose
$ alexa admin logs --tail 100
$ alexa admin cache status
$ alexa admin cache clear
```

**Files à créer:**

- [ ] `cli/commands/admin.py` - Admin commands group
- [ ] `cli/help_texts/admin_help.py` - Help texts

---

## 7. TESTS & VALIDATION

### 7.1 Augmenter Coverage à 85%+

**Impact:** 🟡 **MOYEN** | **Effort:** 🔴 **DIFFICILE** (4-5 jours)

**Coverage Actuel:** ~45% (Dev/pytests/)

**À tester en priorité:**

- [ ] `core/base_manager.py` - **\_api_call, \_get_api_headers** (30+ scenarios)
- [ ] `core/circuit_breaker.py` - **Tous états** (open, half-open, closed)
- [ ] `core/state_machine.py` - **Transitions d'états** (20+ scenarios)
- [ ] `core/security/validators.py` - **Tous validators** (50+ cas edge)
- [ ] `cli/commands/*` - **Commandes utilisateur** (100+ scenarios)

**Créer:**

- [ ] `Dev/pytests/test_base_manager_full.py` - ~300 lignes
- [ ] `Dev/pytests/test_circuit_breaker_full.py` - ~200 lignes
- [ ] `Dev/pytests/test_state_machine_full.py` - ~200 lignes
- [ ] `Dev/pytests/test_validators_full.py` - ~250 lignes
- [ ] `Dev/pytests/test_cli_commands.py` - ~400 lignes

**Commande:**

```bash
python -m pytest Dev/pytests/ --cov=. --cov-report=html
# Target: 85%+ coverage
```

---

### 7.2 Ajouter Performance Benchmarks

**Impact:** 🟡 **MOYEN** | **Effort:** 🟡 **MOYEN** (2 jours)

**Benchmarks à ajouter:**

```python
# Dev/pytests/test_performance.py

def benchmark_api_call_latency():
    """Mesure latence _api_call."""
    # Target: < 500ms pour appel API simple

def benchmark_cache_hit():
    """Mesure vitesse cache mémoire."""
    # Target: < 1ms pour cache hit

def benchmark_multiple_managers_init():
    """Mesure temps initialisation tous managers."""
    # Target: < 500ms pour 30+ managers

def benchmark_command_execution():
    """Mesure temps exécution commands CLI."""
    # Target: < 1s par command
```

---

## 8. DOCUMENTATION

### 8.1 Ajouter Architecture Decision Records (ADR)

**Impact:** 🟢 **BAS** | **Effort:** 🟡 **MOYEN** (1-2 jours)

**ADRs à créer:**

```
Dev/docs/adr/
├── ADR-001-basemanager-inheritance.md
├── ADR-002-circuit-breaker-registry.md
├── ADR-003-csrf-centralization.md
├── ADR-004-repository-pattern.md
├── ADR-005-di-container.md
└── ADR-006-async-implementation.md
```

**Template ADR:**

```markdown
# ADR-00X: Titre

## Status

[PROPOSED | ACCEPTED | SUPERSEDED]

## Context

Problème à résoudre...

## Decision

Solution choisie...

## Consequences

Avantages/Inconvénients...

## Alternatives Considérées

1. ...
2. ...
```

---

### 8.2 Générer API Documentation Sphinx

**Impact:** 🟢 **BAS** | **Effort:** 🟡 **MOYEN** (2 jours)

```bash
# Générer docs
sphinx-quickstart Dev/sphinx_docs
sphinx-apidoc -o Dev/sphinx_docs/source .
make html

# Output: Dev/sphinx_docs/_build/html/index.html
```

**Files à créer:**

- [ ] `Dev/sphinx_docs/conf.py` - Configuration Sphinx
- [ ] `Dev/sphinx_docs/Makefile` - Build sphinx

---

## 📊 Summary & Priority Matrix

| #   | Tâche                           | Impact      | Effort   | Priority | Days |
| --- | ------------------------------- | ----------- | -------- | -------- | ---- |
| 1.1 | Merger managers non-BaseManager | 🔴 CRITIQUE | 🟡 MOYEN | 🔴 P0    | 2-3  |
| 1.2 | Centraliser CircuitBreaker      | 🟡 MOYEN    | 🟡 MOYEN | 🟡 P1    | 1-2  |
| 1.3 | Extraire patterns CLI           | 🟡 MOYEN    | 🟡 MOYEN | 🟡 P1    | 2-3  |
| 2.1 | Normaliser initialisation       | 🟢 BAS      | 🟡 MOYEN | 🟡 P1    | 1-2  |
| 2.2 | Repository Pattern              | 🟡 MOYEN    | 🔴 DIFF  | 🟢 P2    | 3-4  |
| 3.1 | Centraliser CSRF                | 🟡 MOYEN    | 🟡 MOYEN | 🔴 P0    | 2    |
| 3.2 | Input Validation                | 🟡 MOYEN    | 🟡 MOYEN | 🔴 P0    | 2-3  |
| 4.1 | Pagination                      | 🟡 MOYEN    | 🟡 MOYEN | 🟢 P2    | 1-2  |
| 4.2 | Async/Await                     | 🟡 MOYEN    | 🔴 DIFF  | 🟢 P3    | 4-5  |
| 5.1 | DI Container                    | 🟡 MOYEN    | 🟡 MOYEN | 🟡 P1    | 2    |
| 6.1 | Autocomplete                    | 🟢 BAS      | 🟡 MOYEN | 🟢 P2    | 2    |
| 6.2 | Admin Commands                  | 🟡 MOYEN    | 🟡 MOYEN | 🟢 P2    | 2    |
| 7.1 | Coverage 85%                    | 🟡 MOYEN    | 🔴 DIFF  | 🟡 P1    | 4-5  |
| 7.2 | Benchmarks                      | 🟢 BAS      | 🟡 MOYEN | 🟢 P2    | 2    |
| 8.1 | ADRs                            | 🟢 BAS      | 🟡 MOYEN | 🟢 P2    | 1-2  |
| 8.2 | Sphinx Docs                     | 🟢 BAS      | 🟡 MOYEN | 🟢 P3    | 2    |

**Total Estimation:** **30-45 jours** (6-9 semaines)

### Recommended Phases

**Phase 1: Sécurité & Redondance (Semaine 1-2)**

- [ ] 3.1 CSRF Centralization ⚠️ SECURITÉ
- [ ] 3.2 Input Validation ⚠️ SÉCURITÉ
- [ ] 1.1 Merger managers
- [ ] 1.2 CircuitBreaker registry

**Phase 2: Architecture & Tests (Semaine 3-4)**

- [ ] 2.1 ManagerFactory
- [ ] 5.1 DI Container
- [ ] 1.3 CLI patterns
- [ ] 7.1 Coverage 85%

**Phase 3: Optimisations & Helpers (Semaine 5-6)**

- [ ] 2.2 Repository Pattern
- [ ] 4.1 Pagination
- [ ] 6.1 Autocomplete
- [ ] 6.2 Admin Commands

**Phase 4: Advanced & Docs (Semaine 7-9)**

- [ ] 4.2 Async/Await (optionnel)
- [ ] 7.2 Benchmarks
- [ ] 8.1 ADRs
- [ ] 8.2 Sphinx Docs

---

## 🚀 Next Steps

1. **Valider priorités** avec équipe
2. **Créer issues GitHub** pour chaque tâche
3. **Estimer velocité** (points story)
4. **Planifier sprints** (2 semaines)
5. **Commencer Phase 1** (Sécurité + Redondance)

---

**Auteur:** AI Assistant  
**Date Création:** 16 octobre 2025  
**Dernière Mise à Jour:** 16 octobre 2025  
**Status:** 🟡 EN RÉVISION
