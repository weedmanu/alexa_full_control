# Module Config - Documentation

## Vue d'ensemble

Le module `config/` centralise **TOUTE** la configuration de l'application Alexa Full Control. Il élimine les duplications et établit une **Single Source of Truth** pour :

- 🌍 **Régions Amazon** (FR, DE, COM, UK, IT, ES, CA)
- 🔗 **Endpoints API** (30+ endpoints Alexa)
- ⚙️ **Constantes de l'application** (timeouts, retries, cache, volumes, etc.)
- 📁 **Chemins de fichiers** (config, auth, data, logs, cache)
- 🎛️ **Paramètres runtime** (depuis variables d'environnement ou CLI)

---

## Structure

```
config/
├── __init__.py          # Point d'entrée, exports
├── constants.py         # Constantes immuables
├── paths.py             # Chemins de fichiers/dossiers
├── settings.py          # Paramètres runtime (env vars)
└── README.md            # Cette documentation
```

---

## Installation / Import

```python
# Import simple
from config import (
    AmazonRegions,     # Régions Amazon
    AlexaAPI,          # Endpoints API
    AppConstants,      # Constantes
    AppPaths,          # Chemins
    get_settings       # Paramètres runtime
)
```

---

## 1. AmazonRegions - Régions Amazon

### Utilisation

```python
from config import AmazonRegions

# Obtenir une région
region = AmazonRegions.FR  # "amazon.fr"
region = AmazonRegions.DE  # "amazon.de"
region = AmazonRegions.COM  # "amazon.com"

# Région par défaut
default_region = AmazonRegions.DEFAULT  # "amazon.fr"

# Valider une région
if AmazonRegions.is_valid("amazon.fr"):
    print("Région valide!")

# Lister toutes les régions
all_regions = AmazonRegions.get_all()
# ['amazon.fr', 'amazon.de', 'amazon.com', 'amazon.co.uk', ...]
```

### Régions disponibles

| Constante | Valeur         | Région      |
| --------- | -------------- | ----------- |
| `FR`      | `amazon.fr`    | France      |
| `DE`      | `amazon.de`    | Allemagne   |
| `COM`     | `amazon.com`   | États-Unis  |
| `UK`      | `amazon.co.uk` | Royaume-Uni |
| `IT`      | `amazon.it`    | Italie      |
| `ES`      | `amazon.es`    | Espagne     |
| `CA`      | `amazon.ca`    | Canada      |

---

## 2. AlexaAPI - Endpoints API

### Utilisation

```python
from config import AlexaAPI, get_settings

settings = get_settings()

# URL de base Alexa
base_url = AlexaAPI.get_base_url(settings.region)
# "https://alexa.amazon.fr"

# URL Amazon (pour cookies)
amazon_url = AlexaAPI.get_amazon_url(settings.region)
# "https://www.amazon.fr"

# URL complète d'un endpoint
devices_url = AlexaAPI.get_full_url(AlexaAPI.DEVICES_LIST, settings.region)
# "https://alexa.amazon.fr/api/devices-v2/device"

# Utiliser directement les endpoints
response = requests.get(
    f"{AlexaAPI.get_base_url(settings.region)}{AlexaAPI.DEVICES_LIST}",
    headers=headers
)
```

### Endpoints disponibles

#### Appareils

- `DEVICES_LIST` : `/api/devices-v2/device`
- `DEVICE_STATE` : `/api/devices-v2/device/{serialNumber}/state`

#### Notifications

- `NOTIFICATIONS` : `/api/notifications`

#### Alarmes

- `ALARMS` : `/api/notifications`

#### Timers

- `TIMERS` : `/api/timers`

#### Multiroom

- `MULTIROOM_GROUPS` : `/api/lemur/group`

#### Music

- `MUSIC_QUEUE` : `/api/cloudplayer/queue-and-play`
- `MUSIC_PAUSE` : `/api/np/command?type=PauseCommand`
- `MUSIC_PLAY` : `/api/np/command?type=PlayCommand`

#### Et 20+ autres endpoints...

---

## 3. AppConstants - Constantes de l'application

### Utilisation

```python
from config import AppConstants

# Timeouts
timeout = AppConstants.DEFAULT_TIMEOUT  # 30 secondes
auth_timeout = AppConstants.AUTH_TIMEOUT  # 60 secondes

# Retries
max_retries = AppConstants.MAX_RETRIES  # 3
retry_delay = AppConstants.RETRY_DELAY  # 1 seconde

# Circuit breaker
threshold = AppConstants.CIRCUIT_BREAKER_THRESHOLD  # 5 erreurs

# Cache
cache_ttl = AppConstants.DEVICES_CACHE_TTL  # 300 secondes (5 min)

# Volumes
min_vol = AppConstants.MIN_VOLUME  # 0
max_vol = AppConstants.MAX_VOLUME  # 100
default_vol = AppConstants.DEFAULT_SPEAK_VOLUME  # 50

# User agents
user_agent = AppConstants.DEFAULT_USER_AGENT

# Locales
locale = AppConstants.DEFAULT_TTS_LOCALE  # "fr-FR"
```

### Catégories de constantes

| Catégorie           | Constantes                                                     |
| ------------------- | -------------------------------------------------------------- |
| **Timeouts**        | `DEFAULT_TIMEOUT`, `AUTH_TIMEOUT`, `LONG_TIMEOUT`              |
| **Retries**         | `MAX_RETRIES`, `RETRY_DELAY`, `RETRY_BACKOFF_FACTOR`           |
| **Circuit Breaker** | `CIRCUIT_BREAKER_THRESHOLD`, `CIRCUIT_BREAKER_TIMEOUT`         |
| **Cache**           | `DEFAULT_CACHE_TTL`, `DEVICES_CACHE_TTL`, `ROUTINES_CACHE_TTL` |
| **Volumes**         | `MIN_VOLUME`, `MAX_VOLUME`, `DEFAULT_SPEAK_VOLUME`             |
| **Rate Limiting**   | `RATE_LIMIT_CALLS`, `RATE_LIMIT_PERIOD`                        |
| **User Agents**     | `DEFAULT_USER_AGENT`, `API_USER_AGENT`                         |
| **Locales**         | `DEFAULT_LANGUAGE`, `DEFAULT_TTS_LOCALE`                       |

---

## 4. AppPaths - Chemins de fichiers

### Utilisation

```python
from config import AppPaths

# Dossiers principaux
config_dir = AppPaths.get_config_dir()  # ~/.alexa/
auth_dir = AppPaths.get_auth_dir()      # ~/.alexa/auth/
data_dir = AppPaths.get_data_dir()      # ~/.alexa/data/
logs_dir = AppPaths.get_logs_dir()      # ~/.alexa/logs/
cache_dir = AppPaths.get_cache_dir()    # ~/.alexa/cache/
temp_dir = AppPaths.get_temp_dir()      # /tmp/.alexa/ (Unix) ou %TEMP%\.alexa\ (Windows)

# Fichiers spécifiques
token_file = AppPaths.get_token_file()        # ~/.alexa/auth/cookie-resultat.json
cookie_file = AppPaths.get_cookie_file()      # /tmp/.alexa/.alexa.cookie
devices_file = AppPaths.get_device_list_file()  # /tmp/.alexa/.alexa.devicelist
favorites_file = AppPaths.get_favorites_file()  # ~/.alexa/data/favorites.json

# Logs personnalisés
log_file = AppPaths.get_log_file("my_module")  # ~/.alexa/logs/my_module.log

# Cache personnalisé
cache_file = AppPaths.get_cache_file("devices.json")  # ~/.alexa/cache/devices.json

# Chemins projet
project_root = AppPaths.get_project_root()  # Racine du projet
nodejs_dir = AppPaths.get_nodejs_dir()      # {project}/alexa_auth/nodejs/
refresh_script = AppPaths.get_refresh_script()  # {project}/alexa_auth/nodejs/auth-refresh.js

# Chemins personnalisés
custom_path = AppPaths.get_custom_path("my_data/file.json")
# ~/.alexa/my_data/file.json (crée les dossiers si nécessaire)
```

### Création automatique

Toutes les méthodes `get_*_dir()` créent le dossier s'il n'existe pas (avec `mkdir(parents=True, exist_ok=True)`).

---

## 5. AppSettings - Paramètres runtime

### Utilisation

```python
from config import get_settings, set_settings, AppSettings

# Obtenir les paramètres (chargés depuis env au 1er appel)
settings = get_settings()

# Accéder aux paramètres
region = settings.region  # "amazon.fr" (ou valeur de ALEXA_REGION)
timeout = settings.timeout  # 30 (ou valeur de ALEXA_TIMEOUT)
debug = settings.debug_mode  # False (ou valeur de ALEXA_DEBUG)

# Créer des paramètres personnalisés (pour tests ou override)
custom_settings = AppSettings(
    region="amazon.de",
    timeout=60,
    debug_mode=True,
    verbose=True
)
set_settings(custom_settings)

# Valider les paramètres
try:
    settings.validate()
except ValueError as e:
    print(f"Configuration invalide: {e}")

# Convertir en dict
config_dict = settings.to_dict()
```

### Variables d'environnement

| Variable               | Type | Défaut  | Description                                 |
| ---------------------- | ---- | ------- | ------------------------------------------- |
| `ALEXA_REGION`         | str  | `fr`    | Région Amazon                               |
| `ALEXA_REFRESH_TOKEN`  | str  | None    | Token de rafraîchissement                   |
| `ALEXA_CSRF_TOKEN`     | str  | None    | Token CSRF                                  |
| `ALEXA_TIMEOUT`        | int  | `30`    | Timeout HTTP (secondes)                     |
| `ALEXA_MAX_RETRIES`    | int  | `3`     | Nombre max de tentatives                    |
| `ALEXA_VERIFY_SSL`     | bool | `true`  | Vérifier les certificats SSL                |
| `ALEXA_CACHE_ENABLED`  | bool | `true`  | Activer le cache                            |
| `ALEXA_CACHE_TTL`      | int  | `300`   | Durée de vie du cache (secondes)            |
| `ALEXA_LOG_LEVEL`      | str  | `INFO`  | Niveau de log (DEBUG, INFO, WARNING, ERROR) |
| `ALEXA_LOG_TO_FILE`    | bool | `true`  | Logger dans un fichier                      |
| `ALEXA_LOG_TO_CONSOLE` | bool | `true`  | Logger en console                           |
| `ALEXA_DEBUG`          | bool | `false` | Mode debug                                  |
| `ALEXA_VERBOSE`        | bool | `false` | Mode verbose                                |
| `ALEXA_CONFIG_DIR`     | Path | None    | Dossier de configuration personnalisé       |
| `ALEXA_TOKEN_FILE`     | Path | None    | Fichier de tokens personnalisé              |

### Exemple avec env vars

```bash
# Linux/macOS
export ALEXA_REGION=de
export ALEXA_DEBUG=true
export ALEXA_TIMEOUT=60
python alexa device list

# Windows PowerShell
$env:ALEXA_REGION = "de"
$env:ALEXA_DEBUG = "true"
$env:ALEXA_TIMEOUT = "60"
python alexa device list
```

---

## Exemples complets

### Exemple 1 : Utilisation dans un manager

```python
from config import AlexaAPI, get_settings, AppPaths
import requests

class DeviceManager:
    def __init__(self):
        self.settings = get_settings()
        self.cache_file = AppPaths.get_cache_file("devices.json")

    def get_devices(self):
        url = AlexaAPI.get_full_url(AlexaAPI.DEVICES_LIST, self.settings.region)
        response = requests.get(
            url,
            timeout=self.settings.timeout,
            verify=self.settings.verify_ssl
        )
        return response.json()
```

### Exemple 2 : Configuration pour tests

```python
import pytest
from config import AppSettings, set_settings, reset_settings

@pytest.fixture
def test_settings():
    """Configuration pour les tests."""
    settings = AppSettings(
        region="amazon.com",
        timeout=10,
        cache_enabled=False,
        debug_mode=True
    )
    set_settings(settings)
    yield settings
    reset_settings()  # Réinitialiser après le test

def test_device_manager(test_settings):
    manager = DeviceManager()
    assert manager.settings.region == "amazon.com"
    assert manager.settings.timeout == 10
```

### Exemple 3 : Migration depuis l'ancien code

**Avant (code dupliqué) :**

```python
# Dans device_manager.py
ALEXA_BASE_URL = "https://alexa.amazon.fr"
DEVICES_ENDPOINT = "/api/devices-v2/device"
TIMEOUT = 30

url = f"{ALEXA_BASE_URL}{DEVICES_ENDPOINT}"
response = requests.get(url, timeout=TIMEOUT)
```

**Après (code centralisé) :**

```python
from config import AlexaAPI, get_settings

settings = get_settings()
url = AlexaAPI.get_full_url(AlexaAPI.DEVICES_LIST, settings.region)
response = requests.get(url, timeout=settings.timeout)
```

---

## Avantages

✅ **Single Source of Truth** : Une seule définition par constante  
✅ **Maintainabilité** : Changer une valeur = 1 seul endroit  
✅ **Testabilité** : Configuration injectable pour les tests  
✅ **Flexibilité** : Support env vars + configuration programmatique  
✅ **Type Safety** : Type hints complets (Python 3.13+)  
✅ **Cross-platform** : Chemins avec pathlib (Windows, Linux, macOS)  
✅ **Documentation** : Docstrings détaillées + exemples

---

## Migration Guide

Pour migrer du code existant :

1. **Remplacer les hardcoded values** :

   ```python
   # Avant
   url = "https://alexa.amazon.fr/api/devices-v2/device"

   # Après
   from config import AlexaAPI, get_settings
   settings = get_settings()
   url = AlexaAPI.get_full_url(AlexaAPI.DEVICES_LIST, settings.region)
   ```

2. **Remplacer les chemins hardcoded** :

   ```python
   # Avant
   token_file = Path.home() / ".alexa" / "auth" / "cookie-resultat.json"

   # Après
   from config import AppPaths
   token_file = AppPaths.get_token_file()
   ```

3. **Remplacer les constantes locales** :

   ```python
   # Avant
   DEFAULT_TIMEOUT = 30
   MAX_RETRIES = 3

   # Après
   from config import AppConstants
   timeout = AppConstants.DEFAULT_TIMEOUT
   max_retries = AppConstants.MAX_RETRIES
   ```

---

## Notes de version

### v1.0.0 (Initial release)

- ✅ Module `constants.py` : 50+ constantes centralisées
- ✅ Module `paths.py` : 15+ méthodes de chemins
- ✅ Module `settings.py` : Configuration runtime complète
- ✅ Support variables d'environnement
- ✅ Validation de configuration
- ✅ Type hints complets
- ✅ Documentation complète

---

## Support

Pour toute question ou problème :

1. Consulter cette documentation
2. Consulter le fichier `AUDIT_ARCHITECTURE.md` pour le contexte
3. Consulter les docstrings dans les fichiers sources

---

**🎯 Single Source of Truth établie !**
