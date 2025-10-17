# 🏛️ ARCHITECTURE DÉTAILLÉE - Projet Alexa Control

**Date**: Octobre 2025 | **Version**: 2.0.0 | **Statut**: Production-Ready

---

## 📖 Table des Matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Entry Point](#-entry-point--alexa)
3. [Architecture Globale](#-architecture-globale)
4. [Couche par Couche](#-analyse-par-couche)
5. [Dossiers & Fichiers Détaillés](#-dossiers--fichiers-détaillés)
6. [Flux de Données](#-flux-de-données)
7. [Patterns & Principes](#-patterns--principes)
8. [Dépendances](#-dépendances)

---

## 🎯 Vue d'ensemble

### Objectif du Projet

Interface CLI Python pour contrôler **Amazon Alexa** de manière avancée :

- Gestion des appareils Echo
- Contrôle de la musique, timers, alarmes, rappels
- Domotique (lumières, thermostats)
- Routines et scénarios
- Groupes multiroom
- Calendrier, listes, activités

### Architecture Type

```
CLI USER (Shell Command)
    ↓
ENTRY POINT (alexa script)
    ↓
COMMAND PARSER (argument parsing)
    ↓
CONTEXT (DI Container - managers injection)
    ↓
COMMAND CLASS (cli/commands/)
    ↓
MANAGER (core/) or SERVICE (services/)
    ↓
ALEXA API SERVICE (centralized HTTP calls)
    ↓
AUTHENTICATION (alexa_auth/)
    ↓
HTTP SESSION (utils/http_session.py)
    ↓
AMAZON ALEXA API (remote endpoint)
```

### Stack Technologique

```
Framework:      Python 3.8+
HTTP Client:    requests + requests-cache
API Layer:      AlexaAPIService (centralized)
Validation:     Pydantic v2 (DTOs)
Logging:        loguru (emoji-enhanced)
Dependency:     Custom DI Container
Resilience:     pybreaker (circuit breaker)
CLI Parser:     argparse-based
Type Hints:     100% for core/services/cli
Testing:        pytest (798 tests)
```

---

## 🚀 Entry Point: `alexa`

### Localisation

```
📄 c:\Users\weedm\Downloads\alexa_full_control\alexa (no extension)
```

### Type

- **Exécutable Python** (shebang: `#!/usr/bin/env python3`)
- Point d'entrée unique pour toutes les commandes CLI

### Taille

- **Lignes de code**: ~324 (optimisé, pas obèse)
- **Dépendances**: cli/, config/, utils/, core/, services/

### Rôle Principal

```
"Point d'entrée central qui coordonne:
1. Configuration du logging (loguru)
2. Parsing des arguments CLI
3. Injection de dépendances (contexte)
4. Routage vers la bonne commande
5. Gestion globale des erreurs
6. Code de sortie approprié"
```

### Code Structure Simplifié

```python
def main() -> int:
    try:
        # 1️⃣ Setup logging avec loguru
        setup_logging(verbose, debug, no_color)

        # 2️⃣ Parser arguments CLI
        parser = create_parser(version="2.0.0")
        register_all_commands(parser)  # 40 commands
        args = parser.parse_args()

        # 3️⃣ Créer contexte (DI container)
        context = create_context(auth_required=True)
        # ✅ Injecte: DeviceManager, MusicManager, etc.

        # 4️⃣ Router vers commande
        command = get_command_adapter(args.command)
        result = command.execute(context, args)

        # 5️⃣ Retourner code de sortie
        return result

    except KeyboardInterrupt:
        return 1
    except Exception as e:
        logger.error(f"Fatal: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Appels Typiques

```bash
# Exemple 1: Lister les appareils
alexa device list

# Exemple 2: Jouer de la musique
alexa music play -d "Salon Echo" -s "Artist Track"

# Exemple 3: Créer un timer
alexa timer create -d "Kitchen Echo" --duration 10

# Exemple 4: Voir l'aide
alexa --help
```

### Flux d'Exécution Détaillé

```
1. User: alexa music play -d "Salon"
   ↓
2. Entry Point Parsing:
   - Détecte: category="music", action="play", device="Salon"
   ↓
3. Context Creation (DI):
   - Initialise DeviceManager, PlaybackManager, etc.
   - Charge configuration (config/settings.py)
   - Setup authentication (alexa_auth/)
   ↓
4. Command Routing:
   - Trouve cli/commands/music.py → MusicCommand
   - Crée instance: cmd = MusicCommand()
   ↓
5. Command Execution:
   - cmd.execute(context, args)
   - Valide arguments via Pydantic
   ↓
6. Business Logic:
   - PlaybackManager.play(device="Salon", track="...")
   - Appelle AlexaAPIService.play_music()
   ↓
7. API Call:
   - POST https://alexa.amazon.fr/api/music/play
   - Avec authentication tokens (alexa_auth/)
   ↓
8. Response:
   - Reçoit résultat JSON
   - Valide avec DTOs Pydantic
   - Affiche à l'utilisateur
```

### Points Clés

| Aspect             | Détail                                        |
| ------------------ | --------------------------------------------- |
| **Version**        | "2.0.0" (centralisée)                         |
| **Encoding**       | UTF-8 sur Windows (TextIOWrapper)             |
| **Logging**        | Loguru configuré (WARNING/INFO/DEBUG)         |
| **Commands**       | 40+ enregistrées dans register_all_commands() |
| **Error Handling** | Try/catch global + exit codes (0/1)           |
| **Test Support**   | Importable depuis cli/alexa_cli.py            |

---

## 🏗️ Architecture Globale

### Diagram en Couches

```
┌─────────────────────────────────────────────────────┐
│           CLI USER SHELL                            │
│  (alexa device list, alexa music play, etc.)        │
└────────────────┬──────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────┐
│  ENTRY POINT (alexa script)                          │
│  - Parse args + setup logging + create context       │
└────────────────┬──────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────┐
│  CLI COMMAND PARSER & ROUTER (cli/command_parser.py) │
│  - Argparse + custom routing (40 commands)           │
└────────────────┬──────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────┐
│  CONTEXT & DEPENDENCY INJECTION (cli/context.py)     │
│  - Creates: DeviceManager, MusicManager, etc.        │
│  - Loads: Config, Auth, Logger                       │
└────────────────┬──────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────┐
│  COMMAND CLASS (cli/commands/*.py - 40 files)        │
│  - Validates input                                   │
│  - Calls appropriate manager/service                 │
│  - Formats output                                    │
└────────────────┬──────────────────────────────────────┘
                 │
     ┌───────────┴───────────┬─────────────────┐
     │                       │                 │
┌────▼─────────────┐  ┌─────▼─────────┐  ┌────▼──────────────┐
│ MANAGERS (core/) │  │ SERVICES()    │  │ UTILITIES (utils/)│
│ - DeviceManager  │  │ - CacheServ.  │  │ - logger          │
│ - MusicManager   │  │ - FavServ.    │  │ - colorizer       │
│ - TimerManager   │  │ - MusicLib    │  │ - json_storage    │
│ - etc. (15+)     │  │ - SyncService │  │ - http_client     │
└────┬─────────────┘  └─────┬─────────┘  │ - etc. (15+)      │
     │                       │            └───────────────────┘
     └───────────┬───────────┘
                 │
        ┌────────▼──────────────────┐
        │ ALEXA API SERVICE         │
        │ (services/alexa_api_...)  │
        │ - Centralized API calls   │
        │ - DTO validation          │
        │ - Error handling          │
        │ - Circuit breaker         │
        └────────┬───────────────────┘
                 │
        ┌────────▼──────────────────┐
        │ AUTHENTICATION (alexa_auth)│
        │ - OAuth2 flow             │
        │ - Token refresh           │
        │ - Cookie management       │
        └────────┬───────────────────┘
                 │
        ┌────────▼──────────────────┐
        │ HTTP SESSION (utils/http) │
        │ - requests library        │
        │ - Retry logic             │
        │ - Caching                 │
        │ - SSL/TLS                 │
        └────────┬───────────────────┘
                 │
        ┌────────▼──────────────────┐
        │ AMAZON ALEXA API          │
        │ https://alexa.amazon.fr   │
        │ (et autres endpoints)     │
        └───────────────────────────┘
```

### Configuration Centralisée

```
config/ (Single Source of Truth)
├── settings.py      → Pydantic Settings (env vars, config)
├── constants.py     → API endpoints, regions, timeouts
└── paths.py         → Cross-platform paths (Windows/Linux/macOS)
```

### Validation des Données

```
Pydantic DTOs (core/schemas/)
├── Schemas IN  → Valident les requests utilisateur
├── Schemas OUT → Valident les responses API
└── Types → 50+ DTOs spécifiques (Music, Timer, Alarm, etc.)
```

---

## 📊 Analyse par Couche

### COUCHE 1: CLI INTERFACE (40 Commands)

#### Localisation

```
cli/
├── __init__.py                 # Exports: create_context, create_parser
├── alexa_cli.py               # Re-export main() pour tests
├── base_command.py            # Classe parent BaseCommand
├── command_adapter.py         # Adapter pattern pour legacy commands
├── command_parser.py          # Argparse wrapper + custom routing
├── command_template.py        # Template pour créer nouvelles commandes
├── context.py                 # CLI Context (DI container)
├── types.py                   # Type definitions (enums, etc.)
└── commands/ (40 files)
    ├── base_subcommand.py     # Base pour subcommands
    ├── auth.py                # Authentication flow
    ├── device.py              # Device management
    ├── music.py               # Music playback
    ├── timer.py               # Timer management
    ├── alarm.py               # Alarm management
    ├── reminder.py            # Reminder management
    ├── routine.py             # Routine automation
    ├── scenario.py            # Scenario management
    ├── multiroom.py           # Multiroom groups
    ├── dnd.py                 # Do Not Disturb
    ├── favorite.py            # Favorite management
    ├── smart_home.py          # Smart home devices
    ├── calendar.py            # Calendar sync
    ├── activity.py            # Activity log
    ├── lists.py               # List management
    ├── cache.py               # Cache control
    └── ... (24 more)
```

#### Responsabilité

```
"Chaque fichier command/*.py contient:
1. Class <CategoryCommand> héritant de BaseCommand
2. Méthodes pour chaque action (list, create, update, delete, etc.)
3. Argument parsing + validation Pydantic
4. Appel du manager/service approprié
5. Formatting output pour terminal"
```

#### Exemple: `cli/commands/music.py`

```python
class MusicCommand(BaseCommand):
    """Contrôle de la musique."""

    def list_devices(self, context, args):
        """Liste les appareils disponibles."""
        # 1. Valide arguments
        # 2. Appelle context.device_manager.list_devices()
        # 3. Format résultat (tableau, JSON, etc.)
        # 4. Print à l'écran

    def play(self, context, args):
        """Joue une musique."""
        # 1. Valide: device_id, track, artist
        # 2. Appelle context.playback_manager.play(...)
        # 3. Format résultat
        # 4. Print feedback

    def pause(self, context, args):
        # ... idem pour pause

    def get_subparsers(self):
        """Retourne les arguments spécifiques à cette commande."""
        return {
            'play': {'help': 'Play music', 'args': ['-d', '-s', ...]},
            'pause': {'help': 'Pause music'},
            ...
        }
```

#### Routing (40 Commands)

```
Command Registry (register_all_commands):
✅ auth          → AuthCommand
✅ device        → DeviceManagerCommand
✅ music         → MusicCommand
✅ timer         → TimerCommand
✅ alarm         → AlarmCommand
✅ reminder      → ReminderCommand
✅ routine       → RoutineCommand
✅ scenario      → ScenarioCommand
✅ multiroom     → MultiroomCommand
✅ favorite      → FavoriteCommand
✅ dnd           → DNDCommand
✅ cache         → CacheCommand
✅ calendar      → CalendarCommand
✅ activity      → ActivityCommand
✅ lists         → ListsCommand
✅ smarthome     → SmartHomeCommand
... (24 autres)
```

#### Context (Dependency Injection)

Fichier: `cli/context.py`

```python
class Context:
    """Conteneur pour tous les managers et services."""

    def __init__(self):
        # Managers
        self.device_manager = DeviceManager()
        self.playback_manager = PlaybackManager()
        self.timer_manager = TimerManager()
        self.alarm_manager = AlarmManager()
        # ... (12+ plus)

        # Services
        self.cache_service = CacheService()
        self.sync_service = SyncService()
        self.favorite_service = FavoriteService()
        # ...

        # Utils
        self.logger = logger
        self.config = Config()
        self.http_session = OptimizedHTTPSession()
```

---

### COUCHE 2: CONFIGURATION CENTRALISÉE

#### Localisation

```
config/
├── __init__.py           # Exports Config, Settings, etc.
├── settings.py           # Pydantic Settings (env vars)
├── constants.py          # API endpoints, regions, etc.
└── paths.py             # Cross-platform paths
```

#### `settings.py` - Configuration Externalisée

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration via variables d'environnement."""

    # Authentification
    AMAZON_DOMAIN: str = os.getenv("AMAZON", "amazon.fr")
    ALEXA_DOMAIN: str = os.getenv("ALEXA", "alexa.amazon.fr")

    # Localisation
    LANGUAGE: str = os.getenv("LANGUAGE", "fr_FR")
    TTS_LOCALE: str = os.getenv("TTS_LOCALE", "fr-FR")

    # Timeouts & Retries
    HTTP_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    CACHE_TTL: int = 300  # 5 minutes

    # Features
    DEBUG: bool = False
    ENABLE_CACHE: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
```

#### `constants.py` - Endpoints & Constantes

```python
# API Endpoints
ENDPOINTS = {
    "devices": "/api/devices-v2/device",
    "music_play": "/api/music/play",
    "timer_create": "/api/timers",
    "alarm_list": "/api/alarms",
    ...
}

# Regions
REGIONS = {
    "fr": "amazon.fr",
    "en": "amazon.com",
    "de": "amazon.de",
    ...
}

# Default Timeouts
TIMEOUT_DEVICE_LIST = 10
TIMEOUT_API_CALL = 30
TIMEOUT_AUTH = 60
```

#### `paths.py` - Chemins Cross-Platform

```python
from pathlib import Path

class Paths:
    """Chemins pour Windows/Linux/macOS."""

    @staticmethod
    def get_config_dir():
        """Retourne le répertoire config approprié."""
        if sys.platform == "win32":
            return Path(os.getenv("APPDATA")) / "AlexaControl"
        else:
            return Path.home() / ".config" / "alexa"

    @staticmethod
    def get_cache_dir():
        """Retourne le répertoire cache."""
        return Paths.get_config_dir() / "cache"

    @staticmethod
    def get_logs_dir():
        """Retourne le répertoire logs."""
        return Paths.get_config_dir() / "logs"
```

---

### COUCHE 3: MANAGERS MÉTIER (core/)

#### Localisation

```
core/
├── __init__.py                    # Exports managers
├── base_manager.py                # Classe parent BaseManager
├── di_container.py                # Dependency Injection setup
├── device_manager.py              # Device discovery & management
├── notification_manager.py        # Notifications
├── dnd_manager.py                 # Do Not Disturb
│
├── alarms/
│   └── alarm_manager.py           # Alarm management
├── timers/
│   ├── timer_manager.py           # Timer management
│   ├── alarm_manager.py           # Alarm management (repeat)
│   └── reminder_manager.py        # Reminder management
├── music/
│   ├── playback_manager.py        # Music playback control
│   ├── library_manager.py         # Music library
│   └── tunein_manager.py          # TuneIn radio
├── multiroom/
│   └── multiroom_manager.py       # Multiroom groups
├── routines/
│   └── routine_manager.py         # Routine automation
├── scenario/
│   └── scenario_manager.py        # Scenario management
├── calendar/
│   └── calendar_manager.py        # Calendar sync
├── smart_home/
│   ├── device_controller.py       # Smart home devices
│   ├── light_controller.py        # Lights
│   └── thermostat_controller.py   # Thermostats
├── settings/
│   └── device_settings_manager.py # Device settings
├── security/
│   ├── csrf_manager.py            # CSRF token management
│   ├── secure_headers.py          # HTTP headers
│   └── validators.py              # Input validation
│
├── schemas/ (50+ DTOs)
│   ├── base.py                    # Base schemas
│   ├── device_schemas.py          # Device DTOs
│   ├── music_schemas.py           # Music DTOs
│   ├── timer_schemas.py           # Timer DTOs
│   ├── alarm_schemas.py           # Alarm DTOs
│   ├── reminder_schemas.py        # Reminder DTOs
│   ├── routine_schemas.py         # Routine DTOs
│   ├── smart_home_schemas.py      # Smart home DTOs
│   └── ... (15+ plus)
│
├── circuit_breaker.py             # Circuit breaker pattern
├── breaker_registry.py            # Registry de circuit breakers
├── state_machine.py               # Connection state management
├── config.py                      # Legacy config wrapper
├── exceptions.py                  # Custom exceptions
├── types.py                       # Type definitions
└── manager_factory.py             # Factory pattern
```

#### Rôle des Managers

```
"Chaque manager encapsule la logique métier pour une catégorie:

Manager Pattern:
├── Device Manager       → Gère appareils Alexa (list, get details)
├── Music Manager        → Contrôle musique (play, pause, next)
├── Timer Manager        → Crée/gère timers
├── Alarm Manager        → Gère alarmes
├── Reminder Manager     → Gère rappels
├── Multiroom Manager    → Groupes multiroom
├── Routine Manager      → Routines automatisées
├── Scenario Manager     → Scénarios (groupes commandes)
├── Smart Home Manager   → Domotique (lights, thermostats)
├── Calendar Manager     → Synchronisation calendrier
├── Notification Manager → Notifications
└── DND Manager          → Do Not Disturb mode
"
```

#### Architecture d'un Manager

Fichier: `core/device_manager.py`

```python
class DeviceManager(BaseManager):
    """Gestion des appareils Alexa."""

    def __init__(self, api_service, cache_service):
        """Initialisation avec dépendances injectées."""
        super().__init__()
        self.api_service = api_service
        self.cache_service = cache_service

    # MÉTHODE LEGACY (backward compatible)
    def list_devices(self) -> dict:
        """Retourne dict non-typé (legacy)."""
        try:
            response = self.api_service.get("/api/devices-v2/device")
            return response
        except Exception as e:
            logger.error(f"Failed to list devices: {e}")
            return {}

    # MÉTHODE TYPÉE v2 (Phase 3.7)
    def list_devices_dto(self) -> List[DeviceDTO]:
        """Retourne list de DeviceDTO (typée)."""
        try:
            raw = self.list_devices()  # Appelle legacy
            # Valide et convertit avec Pydantic
            devices = [DeviceDTO(**device) for device in raw['devices']]
            return devices
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return []

    # Propriété pour graceful fallback
    HAS_DTO_SUPPORT = True

    def get_device(self, device_id: str) -> dict:
        """Retourne détails d'un device."""
        devices = self.list_devices()
        return next((d for d in devices['devices'] if d['id'] == device_id), None)

    def control_device(self, device_id: str, action: str, params=None):
        """Contrôle un device."""
        payload = {
            "deviceId": device_id,
            "action": action,
            "parameters": params or {}
        }
        return self.api_service.post("/api/np/command", payload)
```

#### DTOs Pydantic (Schemas)

Fichier: `core/schemas/device_schemas.py`

```python
from pydantic import BaseModel, Field

class DeviceDTO(BaseModel):
    """Schéma validé pour un device Alexa."""

    id: str = Field(..., description="Device ID")
    name: str = Field(..., description="Device name")
    device_type: str = Field(..., description="Echo Dot, Show, etc.")
    online: bool = Field(default=False)
    mac_address: str = Field(default="")
    capabilities: List[str] = Field(default_factory=list)

    class Config:
        # Validation stricte
        validate_assignment = True

    def is_online(self) -> bool:
        return self.online

    def __str__(self) -> str:
        return f"{self.name} ({self.device_type})"
```

---

### COUCHE 4: SERVICES (services/)

#### Localisation

```
services/
├── __init__.py                    # Exports des services
├── alexa_api_service.py           # ⭐ CENTRALISÉ (Phase 1)
├── auth.py                        # Auth protocol/client
├── cache_service.py               # Smart cache
├── favorite_service.py            # Favorites management
├── music_library.py               # Music library access
├── sync_service.py                # Data synchronization
└── voice_command_service.py       # Voice commands
```

#### `alexa_api_service.py` - Service API Centralisé (Phase 1)

**Rôle**: Point unique pour TOUS les appels API

```python
class AlexaAPIService:
    """
    Service centralisé pour TOUS les appels API Alexa.

    Phase 1 Objective:
    - Centraliser ALL API calls (évite duplication)
    - Logging/monitoring/metrics
    - Retry logic + circuit breaker
    - DTO validation
    - Error handling
    """

    def __init__(self, session, auth_client, logger):
        self.session = session
        self.auth = auth_client
        self.logger = logger
        self.breaker = CircuitBreaker(name="alexa_api")

    @with_circuit_breaker
    def get(self, endpoint: str, params=None) -> Dict:
        """GET request avec circuit breaker."""
        url = f"{ALEXA_DOMAIN}{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    @with_circuit_breaker
    def post(self, endpoint: str, data: Dict) -> Dict:
        """POST request avec circuit breaker."""
        url = f"{ALEXA_DOMAIN}{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_devices(self) -> List[DeviceDTO]:
        """Spécifique: Lister appareils."""
        raw = self.get("/api/devices-v2/device")
        # Valide avec DTOs
        devices = [DeviceDTO(**d) for d in raw['devices']]
        return devices

    def play_music(self, device_id: str, track: str) -> PlaybackResultDTO:
        """Spécifique: Jouer musique."""
        payload = {"deviceId": device_id, "track": track}
        raw = self.post("/api/music/play", payload)
        return PlaybackResultDTO(**raw)
```

#### `auth.py` - Authentification Protocol

```python
class AuthClient(Protocol):
    """Protocol pour l'authentification."""

    def get_session(self) -> requests.Session:
        """Retourne session avec tokens."""
        ...

    def refresh_token(self) -> bool:
        """Refresh les tokens expirés."""
        ...

    def is_authenticated(self) -> bool:
        """Vérifie si authentifié."""
        ...
```

#### `cache_service.py` - Cache Intelligent

```python
class CacheService:
    """Cache avec TTL, tags, invalidation intelligente."""

    def get(self, key: str) -> Any:
        """Récupère from cache."""
        entry = self.storage.get(key)
        if entry and not entry.is_expired():
            return entry.value
        return None

    def set(self, key: str, value: Any, ttl: int = 300, tags: List[str] = None):
        """Stocke en cache avec TTL et tags."""
        self.storage[key] = CacheEntry(value, ttl, tags)

    def invalidate_by_tag(self, tag: str):
        """Invalide toutes les entrées avec ce tag."""
        self.storage.invalidate(tag=tag)
```

#### `music_library.py` - Librairie Musicale

```python
class MusicLibraryService:
    """Accès à la librairie musicale Amazon."""

    def search(self, query: str) -> List[TrackDTO]:
        """Recherche des pistes."""
        ...

    def get_library(self) -> LibraryDTO:
        """Récupère la librairie complète."""
        ...

    def add_to_library(self, track_id: str) -> bool:
        """Ajoute une piste à la librairie."""
        ...
```

---

### COUCHE 5: AUTHENTIFICATION (alexa_auth/)

#### Localisation

```
alexa_auth/
├── __init__.py
├── alexa_auth.py                  # Main OAuth2 flow
├── alexa_cookie_retriever.py      # Cookie extraction
├── data/
│   ├── cookie-resultat.json       # Stored tokens/cookies
│   └── cookie.txt                 # Plain text cookies
└── nodejs/
    ├── package.json               # npm dependencies
    ├── alexa-cookie-lib.js        # Lib pour cookies
    ├── auth-initial.js            # Initial auth flow
    ├── auth-refresh.js            # Token refresh
    └── utils/
        ├── common.js              # Common utilities
        └── constants.js           # Constants
```

#### Rôle

```
"Module d'authentification pour Amazon Alexa:
1. OAuth2 flow (login)
2. Token refresh (expiration)
3. Cookie management
4. Session maintenance
5. Security (CSRF tokens, etc.)
"
```

#### `alexa_auth.py` - Main Authentication

```python
class AlexaAuth:
    """Gère l'authentification OAuth2."""

    def __init__(self):
        self.token_file = Path("alexa_auth/data/cookie-resultat.json")
        self.refresh_script = Path("alexa_auth/nodejs/auth-refresh.js")

    def login(self, email: str, password: str) -> bool:
        """Effectue login initial."""
        # 1. Execute auth-initial.js
        # 2. Récupère credentials
        # 3. Stocke dans cookie-resultat.json
        # 4. Retourne True/False
        ...

    def refresh_session(self) -> bool:
        """Refresh tokens expirés."""
        # 1. Execute auth-refresh.js
        # 2. Met à jour cookie-resultat.json
        # 3. Retourne True si succès
        ...

    def get_session(self) -> requests.Session:
        """Retourne session avec headers auth."""
        session = requests.Session()
        # 1. Charge tokens depuis cookie-resultat.json
        # 2. Ajoute headers: Authorization, X-CSRF-Token
        # 3. Retourne session prête
        return session

    def is_authenticated(self) -> bool:
        """Vérifie si tokens valides."""
        token = self.load_token()
        if not token:
            return False
        if token.is_expired():
            # Essaye refresh automatique
            return self.refresh_session()
        return True
```

#### `alexa_cookie_retriever.py` - Cookie Extraction

```python
class AlexaCookieRetriever:
    """Extrait les cookies d'Alexa."""

    def get_cookies(self) -> Dict:
        """Récupère cookies."""
        # Exécute alexa-cookie-lib.js
        # Retourne cookies dict
        ...

    def parse_cookie_jar(self, cookies: Dict) -> requests.cookies.RequestsCookieJar:
        """Parse cookies en RequestsCookieJar."""
        jar = RequestsCookieJar()
        for key, value in cookies.items():
            jar.set(key, value)
        return jar
```

#### `nodejs/*` - Scripts Node.js

```javascript
// alexa-cookie-lib.js - Librairie pour cookies
function getCookie(email, password) {
  // Utilise alexa-cookie2 npm package
  // Récupère cookies depuis login Alexa
  // Retourne JSON
}

// auth-initial.js - Initial authentication
// Exécuté: npm run auth-initial
// Paramètres: email, password
// Output: cookie-resultat.json

// auth-refresh.js - Refresh tokens
// Exécuté: npm run auth-refresh
// Lit: cookie-resultat.json
// Output: cookie-resultat.json (mis à jour)
```

---

### COUCHE 6: UTILITIES (utils/)

#### Localisation

```
utils/
├── __init__.py
├── logger.py              # Loguru centralisé + SharedIcons
├── colorizer.py           # ANSI colors + fallbacks
├── term.py                # Terminal detection
├── json_storage.py        # Thread-safe JSON I/O
├── http_client.py         # HTTP client avec circuit breaker
├── http_session.py        # Optimized requests session
├── smart_cache.py         # Advanced cache (tags, TTL)
├── device_index.py        # Device lookup index
├── help_formatter.py      # CLI help formatting
├── help_generator.py      # Dynamic help generation
├── short_help_formatter.py# Compact help
├── text_utils.py          # String utilities
├── network_discovery.py   # Local network detection
└── lazy_loader.py         # Dynamic module loading
```

#### `logger.py` - Logging Centralisé (Phase 2)

```python
from loguru import logger

class SharedIcons:
    """Emojis partagés pour logging."""
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    DEVICE = "🎙️"
    MUSIC = "🎵"
    TIMER = "⏱️"
    # etc.

def setup_loguru_logger(
    log_file: Path = None,
    level: str = "INFO",
    ensure_utf8: bool = True,
    no_color: bool = False
):
    """
    Configure loguru avec format structuré.
    - Couleurs (sauf si no_color=True)
    - Emojis (SharedIcons)
    - Timestamps
    - Logging à fichier (si log_file)
    """
    logger.remove()  # Remove default handler

    # Config format
    fmt = "[{time:YYYY-MM-DD HH:mm:ss}] {level} | {message}"

    # Add console handler
    logger.add(
        sys.stdout,
        format=fmt,
        level=level,
        colorize=not no_color,
    )

    # Add file handler (if specified)
    if log_file:
        logger.add(log_file, format=fmt, level=level)
```

#### `http_client.py` - HTTP Client Résilient

```python
class HTTPClient:
    """Client HTTP avec circuit breaker."""

    def __init__(self):
        self.session = OptimizedHTTPSession()
        self.breaker = CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
        )

    @with_circuit_breaker
    def get(self, url: str, **kwargs) -> requests.Response:
        """GET avec circuit breaker."""
        return self.session.get(url, **kwargs)

    @with_circuit_breaker
    def post(self, url: str, **kwargs) -> requests.Response:
        """POST avec circuit breaker."""
        return self.session.post(url, **kwargs)
```

#### `http_session.py` - Session Optimisée

```python
class OptimizedHTTPSession(requests.Session):
    """Session requests optimisée."""

    def __init__(self):
        super().__init__()

        # Setup retries
        retry = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

        # Setup cache (requests-cache)
        self.cache = requests_cache.CachedSession(
            cache_name="alexa_cache",
            expire_after=300,  # 5 minutes
        )
```

#### `smart_cache.py` - Cache Avancé

```python
class SmartCache:
    """Cache avec tags, TTL, invalidation intelligente."""

    def set(self, key: str, value: Any, ttl: int = 300, tags: List[str] = None):
        """Stocke avec tags."""
        ...

    def get(self, key: str) -> Any:
        """Récupère si pas expiré."""
        ...

    def invalidate_by_tag(self, tag: str):
        """Invalide par tag."""
        ...

    def invalidate_by_pattern(self, pattern: str):
        """Invalide par regex pattern."""
        ...
```

#### `colorizer.py` - ANSI Colors

```python
def colorize(text: str, color: str) -> str:
    """
    Ajoute couleur ANSI au texte.

    Fallbacks:
    - Si terminal non-colorisé: retourne texte plain
    - Si pas de TTY: retourne texte plain
    """
    if not should_colorize():
        return text

    color_codes = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        ...
    }

    return f"{color_codes[color]}{text}\033[0m"
```

#### `json_storage.py` - Thread-Safe Storage

```python
class JsonStorage:
    """Stockage JSON thread-safe."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.lock = RLock()

    def save(self, data: Dict):
        """Sauve au fichier (thread-safe)."""
        with self.lock:
            with open(self.filepath, 'w') as f:
                json.dump(data, f)

    def load(self) -> Dict:
        """Charge du fichier (thread-safe)."""
        with self.lock:
            with open(self.filepath) as f:
                return json.load(f)
```

---

### COUCHE 7: DATA & MODELS

#### `data/device_family_mapping.py`

```python
DEVICE_FAMILY_MAPPING = {
    "ECHO": {
        "product": "Amazon Echo",
        "icon": "🎙️",
        "capabilities": ["music", "timer", "alarm", ...],
    },
    "ECHO_DOT": {
        "product": "Amazon Echo Dot",
        "icon": "🔵",
        "capabilities": ["music", "timer", ...],
    },
    "ECHO_SHOW": {
        "product": "Amazon Echo Show",
        "icon": "📺",
        "capabilities": ["music", "timer", "display", ...],
    },
    # etc.
}
```

#### `models/command.py`

```python
class CommandAction(str, Enum):
    """Actions disponibles pour commandes."""
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    SET_BRIGHTNESS = "SET_BRIGHTNESS"
    SET_VOLUME = "SET_VOLUME"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    # etc.

class DeviceCommand:
    """Commande pour contrôler un device."""

    def __init__(self, device_id: str, action: CommandAction, parameters=None):
        self.device_id = device_id
        self.action = action
        self.parameters = parameters or {}
        self.timestamp = datetime.now()

class CommandResult:
    """Résultat d'exécution."""

    def __init__(self, success: bool, message: str, data=None):
        self.success = success
        self.message = message
        self.data = data
```

---

### COUCHE 8: INSTALLATION

#### `install/install.py` (~1,400 lines)

```python
class SystemChecker:
    """Vérifications système."""

    @staticmethod
    def check_python_version() -> Tuple[bool, str]:
        """Vérifie Python 3.8+."""
        ...

    @staticmethod
    def check_pip() -> Tuple[bool, str]:
        """Vérifie pip disponible."""
        ...

    @staticmethod
    def check_disk_space(required_gb: float = 2.0) -> Tuple[bool, str]:
        """Vérifie espace disque."""
        ...

class DependencyInstaller:
    """Installe dépendances."""

    def install_python_packages(self):
        """pip install -r requirements.txt."""
        ...

    def install_nodejs_packages(self):
        """npm install dans alexa_auth/nodejs."""
        ...

def main():
    """Installation automatique."""
    # 1. Parse arguments (--force, --skip-tests, --uninstall, --dry-run)
    # 2. Vérifie système
    # 3. Installe dépendances
    # 4. Teste configuration
    # 5. Génère config locale (.env, config.ini, etc.)
```

---

### COUCHE 9: LOGS (Répertoire Runtime)

```
logs/
└── (Généré à runtime par loguru)
    ├── alexa_cli.log         # Logs détaillés (debug mode)
    └── errors.log            # Errors seulement
```

---

## 🔄 Flux de Données

### Exemple 1: Jouer de la Musique

```
User Command:
  alexa music play -d "Salon Echo" -s "Soleil bleu"

1. Entry Point (alexa script)
   └─ parse_args() → category="music", action="play", device="Salon", track="Soleil bleu"

2. CLI Parser (cli/command_parser.py)
   └─ route → MusicCommand class

3. Command (cli/commands/music.py)
   └─ MusicCommand.play()
      └─ Valide arguments (Pydantic)
      └─ Appelle context.device_manager.get_device("Salon")
      └─ Appelle context.playback_manager.play(device, track)

4. Manager (core/music/playback_manager.py)
   └─ PlaybackManager.play()
      └─ Valide avec PlaybackDTO
      └─ Appelle self.api_service.play_music(device_id, track)

5. Service (services/alexa_api_service.py)
   └─ AlexaAPIService.play_music()
      └─ Valide input avec MusicPlayDTO
      └─ POST /api/music/play
      └─ Valide réponse avec PlaybackResultDTO

6. Authentication (alexa_auth/)
   └─ Ajoute headers: Authorization, X-CSRF-Token
   └─ Utilise refresh_token si expiré

7. HTTP Session (utils/http_session.py)
   └─ OptimizedHTTPSession.post()
      └─ Retry logic (3 tentatives)
      └─ Circuit breaker (si failure)
      └─ Timeout 30s

8. Network
   └─ POST https://alexa.amazon.fr/api/music/play
      ├─ Headers: Auth, CSRF, User-Agent, etc.
      └─ Body: {"deviceId": "...", "track": "Soleil bleu"}

9. Amazon Alexa API
   └─ Retourne: {"status": "playing", "track": {...}}

10. Back to Service
    └─ Valide response avec ResultDTO
    └─ Retourne PlaybackResultDTO

11. Back to Manager
    └─ Retourne résultat

12. Back to Command
    └─ Format output (tableau, JSON, texte)
    └─ Affiche: "✅ Musique jouée sur Salon Echo"

13. Back to Entry Point
    └─ logger.info("Command executed successfully")
    └─ Retourne exit code 0

14. Terminal
    └─ Affichage au user
    └─ Prompt retour
```

---

## 🎯 Patterns & Principes

### 1. Dependency Injection (DI Container)

```python
# cli/context.py
def create_context():
    return Context(
        device_manager=DeviceManager(api_service),
        music_manager=MusicManager(api_service),
        cache_service=CacheService(),
        # ... ALL managers injected
    )

# Usage in commands
def execute(self, context, args):
    context.device_manager.list_devices()  # Injected!
```

### 2. DTO Pattern (Data Transfer Objects)

```python
# Input DTO - valide requête user
class PlayMusicDTO(BaseModel):
    device_id: str = Field(..., min_length=1)
    track: str = Field(..., min_length=1)
    artist: Optional[str] = None

# Output DTO - valide réponse API
class PlaybackResultDTO(BaseModel):
    status: str  # "playing" | "paused" | "error"
    current_track: Optional[str]
    timestamp: datetime
```

### 3. Dual Methods (Legacy + Typed)

```python
class DeviceManager:
    # Legacy method (backward compat)
    def list_devices(self) -> dict:
        return {"devices": [...]}

    # Typed method (new, Phase 3.7)
    def list_devices_dto(self) -> List[DeviceDTO]:
        raw = self.list_devices()
        return [DeviceDTO(**d) for d in raw['devices']]

    # Flag pour graceful fallback
    HAS_DTO_SUPPORT = True
```

### 4. Circuit Breaker Pattern

```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(
    fail_max=5,        # Fail 5 times then break
    reset_timeout=60,  # Try again after 60s
)

@breaker
def call_api():
    return requests.get(url)
```

### 5. Adapter Pattern

```python
# cli/command_adapter.py
class CommandAdapter:
    """Adapte legacy commands vers nouvelle interface."""

    def adapt(self, command):
        # Si old style → convertir vers new
        # Si new style → passer through
        return adapted_command
```

---

## 📚 Dépendances

### Requirements.txt

```
pydantic==2.x           # DTOs, validation
requests==2.x           # HTTP client
requests-cache==0.x     # HTTP caching
loguru==0.x             # Logging
pybreaker==0.x          # Circuit breaker
click==8.x              # CLI (optional)
argparse-extended==x.x  # Argparse extensions
pathlib==x.x            # Path handling
typing-extensions==x.x  # Type hints
```

### Node.js (alexa_auth/)

```json
{
  "dependencies": {
    "alexa-cookie2": "latest",
    "yargs": "latest"
  }
}
```

---

## 🎬 Conclusion

### Architecture Résumée

```
User Shell Command
        ↓
Entry Point (alexa)
        ↓
CLI Parser (40 commands)
        ↓
Context (DI - all managers)
        ↓
Command Class (input validation)
        ↓
Manager / Service (business logic)
        ↓
AlexaAPIService (centralized API - Phase 1)
        ↓
Authentication (alexa_auth - OAuth2)
        ↓
HTTP Session (with retries, cache, circuit breaker)
        ↓
Amazon Alexa API (remote)
```

### Points Clés

✅ **Modular**: 10 couches bien séparées
✅ **Typed**: 100% type hints (Pydantic v2)
✅ **Testable**: 798 tests passing
✅ **Resilient**: Circuit breaker, retries, caching
✅ **Secure**: OAuth2, CSRF tokens, masking
✅ **Documented**: Docstrings, this guide, examples
✅ **Production-Ready**: All phases complete (1-3)

---

**Generated**: October 2025 | **Version**: 2.0.0 | **Status**: Production-Ready ✅
