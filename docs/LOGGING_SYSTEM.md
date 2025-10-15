# 📋 Système de Logging Alexa Advanced Control

## Vue d'ensemble

Le projet utilise un **système de logging hybride** qui combine :

- **Logger basique** (par défaut) : Affichage simple avec headers stylisés et émojis
- **Loguru** (optionnel) : Logs détaillés avec timestamps, niveaux, modules et lignes de code

---

## 🎯 Choix du niveau de logging

### Mode par défaut (sans options)

```bash
python scripts/install.py
python alexa device list
```

**Comportement :** Affiche uniquement les headers stylisés et messages importants (Logger basique).  
**Idéal pour :** Utilisation normale, affichage propre et minimal.

### Mode Verbose (`-v`)

```bash
python scripts/install.py -v
python alexa device list -v
```

**Comportement :** Active Loguru en mode **INFO**. Affiche tous les logs d'information.  
**Format :**

```
2025-10-15 05:05:50 | ℹ️  INFO         | module:function:line | Message
2025-10-15 05:05:50 | ✅  SUCCESS      | module:function:line | Opération réussie
```

**Idéal pour :** Suivre le déroulement détaillé des opérations.

### Mode Debug (`--debug` ou `-vv`)

```bash
python scripts/install.py --debug
python scripts/install.py -vv
python alexa device list --debug
```

**Comportement :** Active Loguru en mode **DEBUG**. Affiche TOUS les logs incluant debug.  
**Format :**

```
2025-10-15 05:05:50 | 🐞 DEBUG        | module:function:line | Détails techniques
2025-10-15 05:05:50 | ℹ️  INFO         | module:function:line | Information
2025-10-15 05:05:50 | ✅  SUCCESS      | module:function:line | Succès
```

**Idéal pour :** Débogage, développement, analyse des problèmes.

---

## 📊 Niveaux de logging Loguru

| Niveau     | Émoji | Utilisation                                         |
| ---------- | ----- | --------------------------------------------------- |
| `TRACE`    | 🔍    | Traçage très détaillé (rarement utilisé)            |
| `DEBUG`    | 🐞    | Informations de débogage                            |
| `INFO`     | ℹ️    | Informations normales                               |
| `SUCCESS`  | ✅    | Opérations réussies                                 |
| `WARNING`  | ⚠️    | Avertissements                                      |
| `ERROR`    | ❌    | Erreurs                                             |
| `CRITICAL` | 🆘    | Erreurs critiques                                   |
| `AUTH`     | 🔐    | Opérations d'authentification (niveau personnalisé) |
| `INSTALL`  | 🔧    | Opérations d'installation (niveau personnalisé)     |

---

## 🛠️ Configuration

### Installation de Loguru

```bash
pip install loguru
```

**Note :** Le système fonctionne sans Loguru (fallback vers Logger basique).

### Fichier de log optionnel

```bash
# Sauvegarder les logs dans un fichier
python scripts/install.py -v --log-file install.log

# Avec rotation automatique (10 MB) et compression
python scripts/install.py --debug --log-file logs/debug.log
```

Les fichiers de log sont automatiquement :

- **Rotés** à 10 MB
- **Compressés** en `.gz`
- **Conservés** 1 semaine

---

## 📝 Utilisation dans le code

### 1. Import et configuration

```python
from utils.logger import setup_loguru_logger
from pathlib import Path

# Configuration basique
setup_loguru_logger(level="INFO")

# Configuration avec fichier
log_file = Path("logs/app.log")
setup_loguru_logger(
    log_file=log_file,
    level="DEBUG",
    rotation="10 MB",
    retention="1 week"
)
```

### 2. Utilisation de Loguru

```python
from loguru import logger

# Logs simples
logger.debug("Message de débogage")
logger.info("Message d'information")
logger.success("Opération réussie !")
logger.warning("Attention !")
logger.error("Erreur détectée")

# Logs avec contexte
logger.info(f"Connexion réussie pour {username}")
logger.debug(f"Configuration chargée: {config}")

# Logs avec bind (ajouter du contexte)
logger.bind(user=username).info("Action effectuée")

# Logs d'exceptions
try:
    dangerous_operation()
except Exception as e:
    logger.exception("Erreur lors de l'opération")
```

### 3. Niveaux personnalisés

```python
from loguru import logger

# Définir un niveau personnalisé
logger.level("AUTH", no=25, color="<cyan>", icon="🔐")

# Utiliser le niveau personnalisé
logger.log("AUTH", "Authentification réussie")
```

---

## 🎨 Format des logs

### Format Loguru (avec `-v` ou `--debug`)

```
<timestamp> | <emoji> <niveau> | <module>:<fonction>:<ligne> | <message>
```

**Exemple :**

```
2025-10-15 16:07:50 | ℹ️  INFO         | core.config:__init__:103 | ✅ Configuration initialisée
2025-10-15 16:07:50 | 🐞 DEBUG        | core.config:_log_config:220 | 📋 Configuration:
2025-10-15 16:07:50 | 🐞 DEBUG        | core.config:_log_config:221 |   - Langue: fr_FR
2025-10-15 16:07:50 | ✅  SUCCESS      | services.sync_service:sync_devices_only:107 | ✅ 8 appareils Alexa synchronisés
```

### Format Logger basique (mode par défaut)

```
══════════════════════════════════════════════════════════════════════════════
║                   🚀 INSTALLATION ALEXA ADVANCED CONTROL                   ║
══════════════════════════════════════════════════════════════════════════════

ℹ️  Système: Windows 11
✅  Python 3.13.5 détecté
✅  pip disponible (pip 25.2)
```

---

## 🔧 Configuration avancée

### Modifier le format

```python
from loguru import logger
import sys

# Format personnalisé
custom_format = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan> | "
    "<level>{message}</level>"
)

logger.add(
    sys.stdout,
    format=custom_format,
    level="INFO",
    colorize=True
)
```

### Filtrer par module

```python
from loguru import logger

# Logs uniquement pour un module spécifique
logger.add(
    "logs/auth.log",
    filter=lambda record: record["name"] == "alexa_auth.alexa_auth",
    level="DEBUG"
)
```

### Rotation et rétention

```python
from loguru import logger

logger.add(
    "logs/app.log",
    rotation="500 MB",      # Rotation à 500 MB
    retention="10 days",    # Garder 10 jours
    compression="zip",      # Compression en zip
    enqueue=True           # Async pour performances
)
```

---

## 📚 Exemples complets

### Exemple 1: Installation avec logs

```bash
# Installation normale (affichage minimal)
python scripts/install.py

# Installation avec logs INFO
python scripts/install.py -v

# Installation avec logs DEBUG + fichier
python scripts/install.py --debug --log-file install-debug.log

# Installation en dry-run avec logs DEBUG
python scripts/install.py --debug --dry-run --yes
```

### Exemple 2: Commandes Alexa avec logs

```bash
# Liste des appareils (affichage minimal)
python alexa device list

# Liste avec logs INFO
python alexa device list -v

# Liste avec logs DEBUG
python alexa device list --debug

# Commande avec logs sauvegardés
python alexa device list --debug --log-file logs/devices.log
```

### Exemple 3: Script Python personnalisé

```python
#!/usr/bin/env python3
from utils.logger import setup_loguru_logger
from loguru import logger
from pathlib import Path

# Configuration
log_file = Path("logs/my_script.log")
setup_loguru_logger(log_file=log_file, level="DEBUG")

# Utilisation
logger.info("Démarrage du script")
logger.debug(f"Arguments: {sys.argv}")

try:
    # Votre code ici
    result = do_something()
    logger.success(f"Opération réussie: {result}")
except Exception as e:
    logger.exception("Erreur lors de l'exécution")
    sys.exit(1)

logger.info("Script terminé")
```

---

## 🐛 Dépannage

### Problème : Les émojis ne s'affichent pas correctement

**Sous Windows PowerShell :**

```powershell
# Configurer l'encodage UTF-8
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001

# Puis relancer la commande
python scripts/install.py -v
```

**Solution permanente :** Utiliser Windows Terminal au lieu de PowerShell classique.

### Problème : Loguru non disponible

```
⚠️  Loguru non disponible. Installation: pip install loguru
```

**Solution :**

```bash
pip install loguru
```

### Problème : Trop de logs en mode DEBUG

**Solution :** Utiliser `-v` (INFO) au lieu de `--debug` :

```bash
python scripts/install.py -v
```

---

## 📖 Références

- [Documentation Loguru](https://loguru.readthedocs.io/)
- [Émojis Unicode](https://unicode.org/emoji/charts/full-emoji-list.html)
- `utils/logger.py` - Module de configuration Loguru
- `scripts/install.py` - Exemple d'intégration

---

## ✅ Résumé

| Mode               | Commande                   | Logs Loguru | Niveau | Cas d'usage             |
| ------------------ | -------------------------- | ----------- | ------ | ----------------------- |
| **Normal**         | `python alexa ...`         | ❌ Non      | -      | Utilisation quotidienne |
| **Verbose**        | `python alexa ... -v`      | ✅ Oui      | INFO   | Suivi détaillé          |
| **Debug**          | `python alexa ... --debug` | ✅ Oui      | DEBUG  | Débogage                |
| **Double Verbose** | `python alexa ... -vv`     | ✅ Oui      | DEBUG  | Alias de --debug        |

**Recommandation :** Utilisez le mode par défaut pour l'utilisation normale, `-v` pour suivre les opérations, et `--debug` uniquement pour le débogage.

---

_Documentation générée le 15 octobre 2025_
