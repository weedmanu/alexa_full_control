# 📦 Système de Cache Multi-Niveaux

## Vue d'ensemble

Le système de cache d'Alexa Advanced Control utilise une architecture à **2 niveaux + fallback** pour optimiser les performances et réduire les appels API vers Amazon.

## 📊 Diagrammes Visuels

Cette section présente les diagrammes PlantUML illustrant le fonctionnement du système de cache. Pour visualiser ces diagrammes dans VS Code, installez l'extension **PlantUML** (jebbs.plantuml) et ouvrez les fichiers `.puml` avec Alt+D.

### Flux de Cache Multi-Niveaux

Le diagramme suivant illustre les **trois scénarios possibles** lors de la récupération de la liste des appareils :

**Fichier source :** [`diagrams/cache_flow_diagram.puml`](diagrams/cache_flow_diagram.puml)

- **Scénario 1** : Cache mémoire valide (< 5 min) → ⚡ 1-2 ms
- **Scénario 2** : Cache mémoire expiré → Lecture disque (sans TTL) → 💾 10-50 ms
- **Scénario 3** : Pas de cache → Appel API → 🌐 200-1000 ms

### Architecture Globale

**Fichier source :** [`diagrams/cache_architecture.puml`](diagrams/cache_architecture.puml)

Vue d'ensemble de l'architecture montrant les interactions entre :

- CLI Commands
- DeviceManager (cache_ttl=300s)
- Cache Mémoire (Niveau 1 - Volatile)
- CacheService + Cache Disque (Niveau 2 - Persistent, sans TTL)
- Amazon Alexa API

### Machine à États du Cache

**Fichier source :** [`diagrams/cache_state_machine.puml`](diagrams/cache_state_machine.puml)

Le cache évolue entre différents états selon l'utilisation :

- **Empty** : Premier démarrage
- **BothValid** : État optimal (mémoire + disque)
- **DiskOnly** : État de secours (après expiration mémoire)

### Comparaison de Performances

**Fichier source :** [`diagrams/cache_performance.puml`](diagrams/cache_performance.puml)

Analyse des performances pour chaque scénario avec :

- Latence mesurée
- Probabilité d'occurrence
- Étapes détaillées du processus

---

## 🔧 Architecture Textuelle

```
┌─────────────────────────────────────────────────────────────┐
│                   ALEXA DEVICE LIST                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  NIVEAU 1 : CACHE MÉMOIRE (RAM)                             │
│  • TTL : 5 minutes (300s)                                   │
│  • Stockage : Variable Python _devices_cache                │
│  • Performance : ⚡ Instantané (~1ms)                       │
│  • Persistance : ❌ Perdu au redémarrage                   │
└─────────────────────────────────────────────────────────────┘
                            ↓ (si expiré)
┌─────────────────────────────────────────────────────────────┐
│  NIVEAU 2 : CACHE DISQUE FALLBACK (FICHIER)                 │
│  • TTL : ∞ AUCUN - Toujours valide si présent              │
│  • Stockage : data/cache/devices.json.gz                    │
│  • Compression : gzip (~70% réduction)                      │
│  • Performance : 💾 Rapide (~10-50ms)                       │
│  • Persistance : ✅ Survit au redémarrage                  │
│  • Usage : Fallback au démarrage uniquement                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ (si absent)
┌─────────────────────────────────────────────────────────────┐
│  NIVEAU 3 : API AMAZON (HTTP)                               │
│  • URL : alexa.amazon.com/api/devices-v2/device             │
│  • Performance : 🌐 Lent (~200-1000ms)                      │
│  • Action : Met à jour cache mémoire ET disque              │
└─────────────────────────────────────────────────────────────┘
```

**⚠️ IMPORTANT** : Le cache disque n'a **pas de TTL**. Il est utilisé uniquement comme **fallback persistant** :

- Au premier démarrage de l'application
- Après expiration du cache mémoire (5 min) ET absence de connexion API
- Jamais pendant l'utilisation normale (cache mémoire suffit)

---

## 🏗️ Architecture Technique

### Composants Principaux

#### 1. **DeviceManager** (`core/device_manager.py`)

Gestionnaire principal des appareils avec cache mémoire intégré.

```python
class DeviceManager:
    def __init__(self, auth, state_machine, cache_ttl=300, cache_service=None):
        self._devices_cache: Optional[List[Dict]] = None  # Cache Niveau 1
        self._cache_timestamp: float = 0.0
        self._cache_ttl = cache_ttl  # 5 minutes par défaut
        self._cache_service = cache_service or CacheService()
        self._lock = RLock()  # Thread-safe
```

**Méthode clé** : `get_devices(force_refresh=False)`

#### 2. **CacheService** (`services/cache_service.py`)

Service de persistance sur disque avec compression.

```python
class CacheService:
    def __init__(self, cache_dir=None, use_compression=True, save_json_copy=True):
        self.cache_dir = cache_dir or Path("data/cache")
        self.use_compression = use_compression  # gzip
        self.save_json_copy = save_json_copy   # JSON lisible pour debug
        self._lock = RLock()  # Thread-safe
        self._stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "compression_ratio": 0.0
        }
```

**Méthodes principales** :

- `get(key)` : Récupère depuis le cache disque
- `set(key, data, ttl_seconds)` : Sauvegarde avec TTL
- `invalidate(key)` : Supprime du cache
- `get_stats()` : Statistiques d'utilisation

---

## 🔄 Flux de Récupération des Données

### Scénario 1 : Cache Mémoire Valide ⚡

```
Utilisateur exécute : alexa device list
                              ↓
         DeviceManager.get_devices()
                              ↓
         _is_cache_valid() → True (< 5 min)
                              ↓
         RETOUR IMMÉDIAT (1-2ms)
         ✅ Aucun I/O disque
         ✅ Aucun appel réseau
```

**Performance** : ~1-2 ms  
**Log** : `✅ Cache mémoire: 8 appareils`

---

### Scénario 2 : Cache Disque Fallback 💾

```
Utilisateur exécute : alexa device list
                              ↓
         DeviceManager.get_devices()
                              ↓
         _is_cache_valid() → False (> 5 min)
                              ↓
         cache_service.get("devices", ignore_ttl=True)
                              ↓
         Fichier devices.json.gz trouvé
         Décompression gzip (SANS vérification TTL)
         Mise à jour cache mémoire
                              ↓
         RETOUR RAPIDE (10-50ms)
         ✅ Pas d'appel réseau
         ✅ Données potentiellement anciennes mais disponibles
```

**Performance** : ~10-50 ms  
**Log** : `💾 Cache disque: 8 appareils (fallback)`

**⚠️ Note** : Ce scénario est typique au **démarrage de l'application** ou après une **longue période d'inactivité** (> 5 min). Les données proviennent du dernier appel API réussi, quelle que soit leur ancienneté.

---

### Scénario 3 : Appel API 🌐

```
Utilisateur exécute : alexa device list
                              ↓
         DeviceManager.get_devices()
                              ↓
         _is_cache_valid() → False
         cache_service.get("devices") → None (expiré)
                              ↓
         _refresh_cache()
                              ↓
         GET https://alexa.amazon.com/api/devices-v2/device
                              ↓
         Réponse API (200 OK)
                              ↓
         ┌─────────────────────────────────┐
         │ Sauvegarde Multi-Niveaux :      │
         │ 1. Cache mémoire ← devices      │
         │ 2. Cache disque  ← devices.json │
         └─────────────────────────────────┘
                              ↓
         RETOUR LENT (200-1000ms)
         🌐 Données fraîches depuis Amazon
```

**Performance** : ~200-1000 ms  
**Log** : `🌐 Récupération de la liste des appareils depuis l'API`  
**Log** : `✅ 8 appareils récupérés et mis en cache (mémoire + disque)`

---

## 📁 Structure des Fichiers Cache

### Répertoire de cache

```
data/cache/
├── .metadata.json           # Métadonnées TTL et expiration
├── devices.json.gz          # Cache principal compressé (prioritaire)
└── devices.json             # Copie lisible (debug)
```

### Format devices.json.gz

```json
{
  "devices": [
    {
      "accountName": "Salon Echo",
      "deviceType": "A2UONLFQW0PADH",
      "serialNumber": "G6G2MM125193038...",
      "deviceFamily": "KNIGHT",
      "online": true,
      "capabilities": ["AUDIO_PLAYER", "VOICE_ASSISTANT", ...],
      "softwareVersion": "..."
    },
    ...
  ]
}
```

**Compression gzip** : Réduit la taille de ~70%

- JSON non compressé : ~15 KB
- JSON compressé : ~4.5 KB

### Format .metadata.json

```json
{
  "devices": {
    "created_at": 1728662400.123,
    "ttl_seconds": 3600,
    "expires_at": 1728666000.123,
    "size_bytes": 4521,
    "compressed": true
  }
}
```

---

## 🔧 Configuration

### TTL (Time To Live)

| Niveau  | TTL par défaut   | Comportement               | Configurable via               |
| ------- | ---------------- | -------------------------- | ------------------------------ |
| Mémoire | 5 minutes (300s) | Expiration stricte         | `DeviceManager(cache_ttl=...)` |
| Disque  | ∞ AUCUN          | Toujours valide (fallback) | Non applicable                 |

**Implications** :

- Le cache mémoire expire après 5 minutes → force re-vérification
- Le cache disque **ne expire jamais** → données persistantes indéfiniment
- Le cache disque est mis à jour **uniquement** lors d'un appel API réussi
- Pas de "double expiration" ni de "double validation"

### Exemple de configuration personnalisée

```python
from core.device_manager import DeviceManager
from services.cache_service import CacheService

# Cache mémoire 10 minutes
cache_service = CacheService(use_compression=True)
device_mgr = DeviceManager(
    auth=auth,
    state_machine=state_machine,
    cache_ttl=600,  # 10 minutes
    cache_service=cache_service
)

# Le cache disque n'a pas de TTL, il est toujours utilisé comme fallback
    cache_service=cache_service
)

# Sauvegarde avec TTL personnalisé
cache_service.set("devices", data, ttl_seconds=7200)  # 2 heures
```

---

## 🛡️ Thread Safety

Les deux composants sont **thread-safe** grâce à `threading.RLock` :

```python
# DeviceManager
with self._lock:
    if self._is_cache_valid():
        return self._devices_cache
    # ...

# CacheService
with self._lock:
    if self._is_expired(key):
        return None
    # ...
```

✅ **Sûr pour** :

- Utilisation en multi-threading
- Applications concurrentes
- Accès simultanés

---

## 📊 Statistiques et Monitoring

### Récupération des statistiques

```python
cache_service = CacheService()
stats = cache_service.get_stats()

print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Hit Rate: {stats['hit_rate']:.2%}")
print(f"Compression: {stats['compression_ratio']:.1%}")
```

### Exemple de sortie

```
Hits: 145
Misses: 12
Hit Rate: 92.36%
Compression Ratio: 69.8%
Total Writes: 12
Invalidations: 2
```

---

## 🔄 Invalidation du Cache

### Méthode 1 : Force Refresh (API)

```bash
# Force un appel API même si cache valide
python alexa device list --force-refresh
```

```python
devices = device_mgr.get_devices(force_refresh=True)
```

### Méthode 2 : Invalidation Manuelle

```python
# Invalider le cache disque
cache_service.invalidate("devices")

# Invalider le cache mémoire
device_mgr._devices_cache = None
device_mgr._cache_timestamp = 0.0
```

### Méthode 3 : Suppression Fichier

```bash
# Windows PowerShell
Remove-Item data\cache\devices.json.gz

# Linux/Mac
rm data/cache/devices.json.gz
```

---

## ⚡ Optimisations

### 1. **Compression gzip**

- Réduit la taille de ~70%
- Temps de décompression négligeable (~5-10ms)
- Économise l'espace disque et la bande passante I/O

### 2. **Double cache (mémoire + disque)**

- Cache mémoire évite I/O disque (99% des cas)
- Cache disque évite appels réseau coûteux
- Équilibre parfait performance/persistance

### 3. **TTL différenciés**

- Mémoire : 5 min (données ultra-fraîches)
- Disque : 1h (raisonnable pour appareils)
- API : Seulement si nécessaire

### 4. **Copie JSON lisible**

- `save_json_copy=True` crée `devices.json`
- Utile pour debug et inspection
- Peut être désactivé en production

---

## 🐛 Debugging

### Activer les logs détaillés

```python
from loguru import logger

# Niveau DEBUG pour voir tous les accès cache
logger.add("cache_debug.log", level="DEBUG", filter=lambda record: "cache" in record["message"].lower())
```

### Logs typiques

```
DEBUG: ✅ Cache mémoire: 8 appareils
DEBUG: 💾 Cache disque: 8 appareils
DEBUG: 📦 Cache MISS (expired): devices
DEBUG: 🌐 Récupération de la liste des appareils depuis l'API
INFO:  ✅ 8 appareils récupérés et mis en cache (mémoire + disque)
```

### Inspection manuelle du cache

```python
import gzip
import json
from pathlib import Path

# Lire le cache compressé
cache_file = Path("data/cache/devices.json.gz")
with gzip.open(cache_file, "rt") as f:
    data = json.load(f)

print(f"Appareils en cache: {len(data['devices'])}")
for device in data['devices']:
    print(f"- {device['accountName']}: {device['online']}")
```

---

## 📈 Benchmarks

### Comparaison des performances

| Scénario             | Temps moyen | Appels API | I/O Disque |
| -------------------- | ----------- | ---------- | ---------- |
| Cache mémoire valide | 1-2 ms      | 0          | 0          |
| Cache disque valide  | 10-50 ms    | 0          | 1 lecture  |
| Appel API            | 200-1000 ms | 1          | 1 écriture |

### Économies sur 1000 requêtes

Supposons :

- 1000 requêtes sur 24h
- Distribution : 95% mémoire, 4% disque, 1% API

```
Sans cache :
  1000 appels API × 500ms = 500 secondes = 8.3 minutes

Avec cache :
  950 × 2ms    = 1.9 secondes   (mémoire)
  40  × 30ms   = 1.2 secondes   (disque)
  10  × 500ms  = 5.0 secondes   (API)
  TOTAL        = 8.1 secondes

GAIN : 98.4% de réduction du temps total !
```

---

## 🔒 Sécurité

### Données sensibles

⚠️ Le cache contient des informations sur vos appareils :

- Noms d'appareils
- Numéros de série
- Types d'appareils
- Statuts en ligne

### Recommandations

✅ **À faire** :

- Ajouter `data/cache/` au `.gitignore`
- Ne pas partager les fichiers cache
- Utiliser des permissions restrictives (600)

❌ **À éviter** :

- Commiter les caches dans Git
- Partager les caches sur cloud public
- Logs verbeux en production

---

## 🚀 Utilisation Avancée

### Cache pour autres données

Le `CacheService` est générique et peut cacher n'importe quoi :

```python
# Cache des routines
cache_service.set("routines", {"routines": routines_list}, ttl_seconds=1800)
routines = cache_service.get("routines")

# Cache des alarmes
cache_service.set("alarms", {"alarms": alarms_list}, ttl_seconds=300)
alarms = cache_service.get("alarms")

# Cache des smart home devices
cache_service.set("smarthome", {"devices": sh_devices}, ttl_seconds=3600)
```

### Pré-chargement du cache

```python
# Au démarrage de l'application
async def preload_caches():
    """Pré-charge les caches au démarrage."""
    device_mgr.get_devices()  # Force chargement
    routine_mgr.get_routines()
    alarm_mgr.get_alarms()
    logger.info("Caches pré-chargés")
```

---

## 📚 Références

- **Code source** :
  - `core/device_manager.py` - Gestionnaire avec cache mémoire
  - `services/cache_service.py` - Service de cache disque
- **Documentation** :
  - [Python threading.RLock](https://docs.python.org/3/library/threading.html#rlock-objects)
  - [gzip compression](https://docs.python.org/3/library/gzip.html)
  - [JSON serialization](https://docs.python.org/3/library/json.html)

---

## 📝 Changelog

| Version | Date       | Changements                            |
| ------- | ---------- | -------------------------------------- |
| 2.0.0   | 2025-10-11 | Système de cache multi-niveaux initial |
| 2.1.0   | 2025-10-11 | Ajout compression gzip + copie JSON    |
| 2.2.0   | 2025-10-11 | Thread-safety avec RLock               |
| 2.3.0   | 2025-10-11 | Statistiques et monitoring             |

---

**Auteur** : M@nu  
**Dernière mise à jour** : 11 octobre 2025  
**Projet** : Alexa Advanced Control - CLI
