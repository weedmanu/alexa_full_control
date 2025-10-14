# 🎙️ Alexa Advanced Control CLI# 🎙️ Alexa Advanced Control CLI

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[![Tests](https://img.shields.io/badge/tests-207%20passed-brightgreen.svg)](tests/)[![Tests](https://img.shields.io/badge/tests-207%20passed-brightgreen.svg)](tests/)

[![Health](https://img.shields.io/badge/health-75%25-yellow.svg)](scripts/health_check.py)[![Health](https://img.shields.io/badge/health-75%25-yellow.svg)](scripts/health_check.py)

[![Files](https://img.shields.io/badge/python_files-149-blue.svg)](#)[![Files](https://img.shields.io/badge/python_files-149-blue.svg)](#)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 🚀 **Interface CLI professionnelle et robuste pour contrôler Amazon Alexa**> 🚀 **Interface CLI professionnelle et robuste pour contrôler Amazon Alexa**

> >

> Contrôlez votre écosystème Alexa complet depuis le terminal : appareils, musique, timers, smart home, routines, et bien plus. Architecture enterprise-grade avec circuit breaker, cache multi-niveaux, et state machine thread-safe.> Contrôlez votre écosystème Alexa complet depuis le terminal : appareils, musique, timers, smart home, routines, et bien plus. Architecture enterprise-grade avec circuit breaker, cache multi-niveaux, et state machine.

---

## 📋 Table des Matières## 📋 Table des Matières

- [Caractéristiques Clés](#-caractéristiques-clés)---

- [Architecture](#-architecture)

- [Installation](#-installation)- [Fonctionnalités](#-fonctionnalités)

- [Démarrage Rapide](#-démarrage-rapide)

- [Managers Disponibles](#-managers-disponibles)## ✨ Fonctionnalités- [Architecture](#-architecture)

- [Diagnostic & Monitoring](#-diagnostic--monitoring)

- [Développement](#-développement)- [Installation](#-installation)

- [Tests & Qualité](#-tests--qualité)

- [Contribution](#-contribution)### 🎯 Contrôle Complet- [Utilisation](#-utilisation)

---- 🔐 **Authentification** - Gestion sécurisée de la connexion Amazon- [Documentation](#-documentation)

## ✨ Caractéristiques Clés- 📱 **Appareils** - Liste, info, contrôle de tous vos Echo et appareils Alexa- [Développement](#-développement)

### 🎯 Fonctionnalités Complètes- 🎵 **Musique** - Lecture, pause, volume, playlists (Amazon Music, Spotify, TuneIn)- [Tests](#-tests)

**17+ Managers Opérationnels** - Tous testés et fonctionnels :- ⏰ **Timers & Alarmes** - Création, modification, suppression- [Contribution](#-contribution)

- 🔐 **Authentification** - Cookies sécurisés + CSRF token- 💡 **Smart Home** - Contrôle lumières, thermostats, prises, stores

- 📱 **Appareils** - Gestion complète (149 devices testés)

- 🎵 **Musique** - Amazon Music, Spotify, TuneIn- 🔔 **Notifications** - Envoi et gestion des notifications---

- ⏰ **Timers/Alarmes/Rappels** - Création, modification, suppression

- 💡 **Smart Home** - Lumières, thermostats, appareils connectés- 🔕 **Do Not Disturb** - Activation et programmation DND

- 🔔 **Notifications** - Liste, suppression, marquage lu

- 🔕 **DND** - Do Not Disturb par appareil- 📢 **Annonces** - Diffusion de messages sur vos appareils## ✨ Fonctionnalités

- 📢 **Annonces** - Messages multi-pièces

- 🔁 **Routines** - 44 routines récupérées ✅ (nouveau !)- 📝 **Listes** - Gestion listes de courses et todo

- 📝 **Listes** - Courses, tâches

- 📊 **Activités** - Historique interactions- 🔁 **Routines** - Exécution de vos routines Alexa### 🎵 Contrôle Multimédia

- 🔊 **Audio** - Égaliseur, Bluetooth

- ⚙️ **Paramètres** - Configuration appareils- ⚙️ **Paramètres** - Configuration avancée des appareils

### 🏗️ Architecture Enterprise-Grade- 🔊 **Audio** - Égaliseur, Bluetooth, mode audio- Lecture musique (Amazon Music, Spotify, TuneIn)

- ✅ **Thread-Safe** - `threading.RLock()` sur toutes les ressources partagées- 👥 **Multiroom** - Gestion des groupes audio- Contrôle playback (play, pause, next, prev, shuffle, repeat)

- ✅ **Circuit Breaker** - Protection contre cascades d'erreurs (threshold=3, timeout=30s)

- ✅ **State Machine** - 7 états robustes (DISCONNECTED, CONNECTING, CONNECTED, ERROR, RATE_LIMITED, REFRESHING_TOKEN, SHUTTING_DOWN)- 📊 **Activités** - Historique des interactions- Gestion playlists et files d'attente

- ✅ **Cache Multi-Niveaux** - Mémoire (TTL 5min) + Disque (TTL 1h) + API fallback

- ✅ **50+ Endpoints Validés** - Script `verify_endpoints.py` avec 0 invalides détectés- Recherche de musique et radios

- ✅ **Type Safety** - Type hints complets + mypy strict mode

- ✅ **Logging Structuré** - Loguru avec rotation automatique### 🚀 Architecture Moderne

### 📊 Qualité & Fiabilité- ✅ **171 tests unitaires** - 100% de réussite### ⏰ Gestion Temporelle

| Métrique | Valeur | Statut |- ✅ **Architecture modulaire** - MVC + Repository pattern

|----------|--------|--------|

| **Tests** | 207 tests (186 unitaires + 21 intégration) | ✅ 100% succès |- ✅ **Type hints** - Code entièrement typé (MYPY validated)- Timers (création, pause, reprise, annulation)

| **Santé Globale** | 75% (4 OK, 2 warnings mineurs) | ⚠️ Acceptable |

| **Fichiers Python** | 149 fichiers modulaires | ✅ |- ✅ **Circuit Breaker** - Gestion robuste des erreurs API- Alarmes (création, modification, suppression, récurrence)

| **Commits (10j)** | 39 commits session qualité | ✅ |

| **Endpoints API** | 50+ validés, 0 invalides | ✅ |- ✅ **Logging avancé** - Loguru pour debug facile- Rappels (création, liste, suppression)

| **Cache** | 10 fichiers (149.5 Ko), 3/3 critiques présents | ✅ |

| **Type Coverage** | 100% type hints (mypy validé) | ✅ |- ✅ **CLI intuitive** - ArgumentParser avec sous-commandes

---- ✅ **Code quality** - PYLINT 9.62/10, formaté Black/Isort### 🏠 Smart Home

## 🏗️ Architecture---- Contrôle lumières (on/off, luminosité, couleur, température)

### 📐 Structure du Projet- Thermostats (température, mode, ajustements)

```````## 📦 Installation- Appareils connectés (serrures, volets, prises)

alexa_cli-dev/

├── cli/                          # Interface ligne de commande- État des appareils smart home

│   ├── context.py                # Contexte centralisé (CacheService, Managers)

│   └── alexa_cli.py              # Point d'entrée CLI principal### Prérequis

│

├── core/                         # Managers métier- **Python 3.8+**### 📢 Communication

│   ├── routines/

│   │   └── routine_manager.py    # ✅ RoutineManager (310 lignes, cache, circuit breaker)- **Node.js 14+** (pour l'authentification initiale uniquement)

│   ├── timers/

│   │   ├── timer_manager.py      # ✅ Timers- **pip** (gestionnaire de paquets Python)- Annonces multi-pièces

│   │   ├── alarm_manager.py      # ✅ Alarmes

│   │   └── reminder_manager.py   # ✅ Rappels- Drop-In entre appareils

│   ├── smart_home/

│   │   ├── light_controller.py   # ✅ Lumières (on/off, brightness, color)### Installation rapide- Notifications (liste, suppression, marquage lu)

│   │   ├── thermostat_controller.py  # ✅ Thermostats

│   │   └── device_controller.py  # ✅ Appareils smart home- Mode Ne Pas Déranger (DND)

│   ├── music/

│   │   ├── playback_manager.py   # ✅ Lecture musique```bash

│   │   └── tunein_manager.py     # ✅ Radios TuneIn

│   ├── communication/# 1. Cloner le dépôt### 📝 Listes & Activités

│   │   └── announcement_manager.py  # ✅ Annonces

│   ├── audio/git clone https://github.com/weedmanu/alexa_advanced_control.git

│   │   ├── equalizer_manager.py  # ✅ Égaliseur

│   │   └── bluetooth_manager.py  # ✅ Bluetoothcd alexa_advanced_control- Listes de courses et tâches

│   ├── settings/

│   │   └── device_settings_manager.py  # ✅ Paramètres- Historique des activités

│   ├── device_manager.py         # ✅ Gestion appareils

│   ├── notification_manager.py   # ✅ Notifications# 2. Créer l'environnement virtuel (recommandé)- Historique vocal (consultation, suppression)

│   ├── dnd_manager.py            # ✅ Do Not Disturb

│   ├── state_machine.py          # ✅ Machine d'états (7 états)python3 -m venv venv

│   └── circuit_breaker.py        # ✅ Circuit breaker pattern

│source venv/bin/activate  # Linux/macOS### 🔊 Paramètres Audio

├── services/                     # Services transverses

│   ├── cache_service.py          # ✅ Cache centralisé (mémoire + disque)# ou

│   └── sync_service.py           # ✅ Synchronisation auto (devices, smart_home, routines)

│venv\Scripts\activate     # Windows- Égaliseur (basse, medium, aigus)

├── alexa_auth/                   # Authentification

│   ├── alexa_cookie_retriever.py # ✅ Gestion cookies- Bluetooth (connexion, déconnexion, appareils appairés)

│   └── nodejs/                   # Scripts Node.js auth

│       ├── auth-initial.js# 3. Installer les dépendances- Volume par appareil

│       └── auth-refresh.js

│pip install -r requirements.txt

├── scripts/                      # Outils diagnostic

│   ├── verify_endpoints.py       # ✅ Validation 50+ endpoints API### ⚙️ Configuration

│   └── health_check.py           # ✅ Diagnostic santé (6 vérifications)

│# 4. Installer les dépendances Node.js (pour l'auth)

├── tests/                        # 207 tests (100% succès)

│   ├── test_state_machine.pycd alexa_auth/nodejs- Paramètres appareils (wake word, timezone, locale)

│   ├── test_device_service.py

│   └── test_state_machine_integration.pynpm install- Groupes multi-pièces

│

└── utils/                        # Utilitairescd ../..- Routines (liste, exécution)

    ├── config.py                 # Configuration

    ├── logger.py                 # Logging Loguru

    └── validators.py             # Validateurs

```# 5. Rendre le script exécutable---



### 🔄 Diagramme de Flux - Architecture Globalechmod +x alexa



```## 🏗️ Architecture

┌─────────────────────────────────────────────────────────────┐

│                   CLI (alexa_cli.py)                        │# 6. Tester l'installation

│                    Point d'entrée                           │

└───────────────────────────┬─────────────────────────────────┘./alexa --version### Architecture Technique

                            │

                ┌───────────▼────────────┐```

                │   Context (Singleton)  │

                │  - CacheService        │````

                │  - AlexaAuth           │

                │  - StateMachine        │---┌─────────────────────────────────────────────────┐

                │  - 17+ Managers        │

                └───────────┬────────────┘│           alexa (CLI)          │

                            │

         ┌──────────────────┼──────────────────┐## 🚀 Démarrage Rapide└─────────────────────┬───────────────────────────┘

         │                  │                  │

    ┌────▼────┐     ┌──────▼──────┐    ┌─────▼──────┐                      │

    │ Managers│     │   Services  │    │   Cache    │

    │ (17+)   │◄────┤ - SyncServ  │◄───┤ - Mémoire  │### 1️⃣ Première connexion        ┌─────────────┴─────────────┐

    │         │     │ - Cache     │    │ - Disque   │

    └────┬────┘     └─────────────┘    └────────────┘        │                           │

         │

    ┌────▼─────────┐```bash┌───────▼────────┐         ┌────────▼───────┐

    │ StateMachine │

    │ (7 états)    │# Se connecter à votre compte Amazon│  CLI Commands  │         │  Core Managers │

    └────┬─────────┘

         │./alexa auth login│  (À venir)     │◄────────┤  (17 modules)  │

    ┌────▼──────────┐

    │CircuitBreaker │# → Un navigateur s'ouvrira pour l'authentification└────────────────┘         └────────┬───────┘

    │ (Auto-recov)  │

    └────┬──────────┘                                    │

         │

    ┌────▼────────┐# Vérifier la connexion                      ┌─────────────┴─────────────┐

    │  Alexa API  │

    │  (HTTPS)    │./alexa auth status                      │                           │

    └─────────────┘

``````            ┌─────────▼──────────┐    ┌──────────▼────────┐



### 🔐 Flux Authentification            │  State Machine     │    │  Circuit Breaker  │



```### 2️⃣ Découvrir vos appareils            │  (7 états)         │    │  (Auto-recovery)  │

User → CLI → NodeJS (auth-initial.js) → Amazon Login

                  ↓            └────────────────────┘    └───────────────────┘

           Cookies + CSRF token

                  ↓```bash                      │                           │

      AlexaAuth (alexa_cookie_retriever.py)

                  ↓# Lister tous vos appareils Alexa                      └───────────┬───────────────┘

         Stockage sécurisé (600 perms)

                  ↓./alexa device list                                  │

      Refresh token auto (auth-refresh.js)

```                        ┌─────────▼──────────┐



### 📊 Flux Données avec Cache# Afficher les détails d'un appareil                        │    Alexa API       │



```./alexa device info -d "Salon"                        │  (HTTPS + Cookies) │

CLI Command

    ↓```                        └────────────────────┘

Manager (ex: RoutineManager)

    ↓````

┌───▼────────────────────────────┐

│ Cache Check (CacheService)     │### 3️⃣ Exemples simples

│                                 │

│ 1. Mémoire (TTL 5min)          │ ← Hit? Return### Composants Principaux

│    ↓ Miss                       │

│ 2. Disque (TTL 1h)             │ ← Hit? Return + Store mémoire````bash

│    ↓ Miss                       │

│ 3. API Amazon                  │ ← Fetch + Store mémoire + disque# Jouer de la musique#### 🎯 Core Managers (Complets ✅)

└─────────────────────────────────┘

    ↓./alexa music play -d "Salon" -s "Bohemian Rhapsody"

CircuitBreaker (protection)

    ↓- **Timers:** `TimerManager`, `AlarmManager`, `ReminderManager`

Alexa API (HTTPS + Cookies)

    ↓# Créer un timer de 10 minutes- **Smart Home:** `LightController`, `ThermostatController`, `SmartDeviceController`

Response → Cache update → User

```./alexa timer create -d "Cuisine" --duration 10 --label "Pâtes"- **Musique:** `PlaybackManager`, `TuneInManager`, `LibraryManager`



---- **Communication:** `AnnouncementManager`



## 📦 Installation# Allumer une lumière à 80%- **Listes:** `ListManager`



### Prérequis./alexa light on --entity light.salon- **Audio:** `EqualizerManager`, `BluetoothManager`



- **Python 3.8+**./alexa light brightness --entity light.salon --value 80- **Paramètres:** `DeviceSettingsManager`

- **Node.js 14+** (pour authentification initiale uniquement)

- **pip** (gestionnaire paquets Python)- **Système:** `NotificationManager`, `DNDManager`, `ActivityManager`

- **Git**

# Envoyer une annonce

### Installation Rapide

./alexa announcement send -m "Le repas est prêt !"#### 🔧 Infrastructure Robuste

```bash

# 1. Cloner le dépôt

git clone https://github.com/weedmanu/alexa_advanced_control.git

cd alexa_advanced_control# Activer Do Not Disturb- **State Machine:** 7 états thread-safe (DISCONNECTED, CONNECTING, CONNECTED, ERROR, RATE_LIMITED, REFRESHING_TOKEN, SHUTTING_DOWN)



# 2. Créer environnement virtuel (recommandé)./alexa dnd enable -d "Chambre"- **Circuit Breaker:** Protection contre cascades d'erreurs (failure_threshold=3, timeout=30s)

python3 -m venv venv

source venv/bin/activate  # Linux/macOS```- **Sécurité:** Permissions fichiers 600, sanitization chemins, HTTPS uniquement

# ou

venv\Scripts\activate     # Windows- **Logging:** Loguru avec niveaux structurés



# 3. Installer dépendances Python---- **Type Safety:** Type hints complets (mypy strict mode)

pip install -r requirements.txt



# 4. Installer dépendances Node.js (auth)

cd alexa_auth/nodejs## 📖 Documentation#### 🧪 Tests (55 tests ✅)

npm install

cd ../..



# 5. Rendre script exécutable (Linux/macOS)- **[📘 Guide Utilisateur Complet](USER_GUIDE.md)** - Documentation détaillée avec tous les exemples- Tests unitaires pour tous les managers

chmod +x alexa

- **[🔧 Script de Qualité](tests/config/check_quality.sh)** - Vérification qualité du code- Tests d'intégration state machine + circuit breaker

# 6. Vérifier installation

./alexa --version- **[🧪 Tests](tests/)** - 171 tests unitaires- Mocks pour API (pas d'appels réels en tests)

```````

- Coverage cible: >80%

### Installation Développement

---

`````bash

# En plus de l'installation standard :---

pip install -r requirements-dev.txt

## 🏗️ Architecture du Projet

# Vérifier qualité code

./tests/config/check_quality.sh## 📦 Installation



# Lancer tests### Structure des Répertoires

pytest tests/ -v

```### Prérequis



---````



## 🚀 Démarrage Rapidealexa_advanced_control/- Python 3.8+



### 1️⃣ Première Authentification├── alexa # Point d'entrée CLI- Node.js (pour authentification cookies)



```bash├── cli/ # Interface ligne de commande- Git

# Se connecter à votre compte Amazon

./alexa auth login│ ├── commands/ # 18 commandes disponibles

# → Un navigateur s'ouvrira pour saisir identifiants Amazon

│ │ ├── auth.py # Authentification### Installation Rapide

# Vérifier connexion

./alexa auth status│ │ ├── device.py # Gestion appareils

# ✅ Authenticated: Yes

# 📧 Email: votre.email@example.com│ │ ├── music.py # Contrôle musique```bash

# 🌍 Domain: amazon.fr

```│ │ ├── timer.py # Timers# Cloner le dépôt (branche cli-dev)



### 2️⃣ Découvrir Vos Appareils│ │ ├── alarm.py # Alarmesgit clone -b cli-dev https://github.com/weedmanu/alexa_advanced_control.git



```bash│ │ ├── light.py # Lumièrescd alexa_advanced_control

# Lister tous appareils Alexa

./alexa device list│ │ ├── thermostat.py # Thermostats



# Sortie JSON pour scripts│ │ ├── smarthome.py # Smart home général# Créer environnement virtuel

./alexa device list --json

│ │ ├── notification.py # Notificationspython -m venv venv

# Infos détaillées d'un appareil

./alexa device info -d "Echo Salon"│ │ ├── dnd.py # Do Not Disturb

`````

│ │ ├── announcement.py # Annonces# Activer environnement

### 3️⃣ Exemples Simples

│ │ ├── list.py # Listessource venv/bin/activate # Linux/macOS

`````bash

# 🎵 Jouer de la musique│ │ ├── reminder.py # Rappelsvenv\Scripts\activate # Windows

./alexa music play -d "Salon" -s "Bohemian Rhapsody"

│ │ ├── activity.py # Historique

# ⏰ Créer un timer

./alexa timer create -d "Cuisine" --duration 10 --label "Pâtes"│ │ ├── settings.py # Paramètres# Installer dépendances



# 💡 Allumer lumière à 80%│ │ ├── audio.py # Audio avancépip install -r requirements.txt

./alexa light on --entity light.salon

./alexa light brightness --entity light.salon --value 80│ │ ├── routine.py # Routines



# 📢 Envoyer annonce│ │ └── multiroom.py # Multiroom# Installer dépendances développement (optionnel)

./alexa announcement send -m "Le repas est prêt !"

│ ├── base_command.py # Classe de basepip install -r requirements-dev.txt

# 🔕 Activer Do Not Disturb

./alexa dnd enable -d "Chambre"│ ├── command_parser.py # Parser principal



# 🔁 Lister routines (nouveau !)│ └── context.py # Contexte d'exécution# Installer dépendances Node.js (authentification)

./alexa routine list

# ✅ 44 routines récupérées├── core/ # Logique métiercd alexa_auth/nodejs



# 📋 Afficher notifications│ ├── activity_manager.py # Gestion activitésnpm install

./alexa notification list --limit 10

│ ├── dnd_manager.py # Gestion DNDcd ../..

# 📊 État du cache

./alexa cache status│ ├── notification_manager.py # Gestion notifications```

# 📁 10 fichiers (149.5 Ko total)

```│ ├── circuit_breaker.py # Pattern Circuit Breaker



---│ ├── state_machine.py # Machine d'états### Configuration



## 🎯 Managers Disponibles│ ├── audio/ # Modules audio



### Core Managers (17+ modules)│ ├── lists/ # Gestion listes```bash



| Manager | Fichier | Fonctionnalités | Tests | Statut |│ ├── music/ # Contrôle musique# Première connexion (génère cookies)

|---------|---------|-----------------|-------|--------|

| **RoutineManager** | `core/routines/routine_manager.py` | Liste/exécution routines, cache, stats | ✅ 3 | ✅ 310 lignes |│ ├── settings/ # Paramètrespython alexa --login

| **TimerManager** | `core/timers/timer_manager.py` | Create, pause, resume, cancel | ✅ 8 | ✅ |

| **AlarmManager** | `core/timers/alarm_manager.py` | Create, update, delete, récurrence | ✅ 6 | ✅ |│ ├── smart_home/ # Smart home

| **ReminderManager** | `core/timers/reminder_manager.py` | Create, list, delete | ✅ 4 | ✅ |

| **LightController** | `core/smart_home/light_controller.py` | On/off, brightness, color, temp | ✅ 12 | ✅ |│ ├── timers/ # Timers/Alarmes/Rappels# Vérifier connexion

| **ThermostatController** | `core/smart_home/thermostat_controller.py` | Température, mode, ajustements | ✅ 5 | ✅ |

| **SmartDeviceController** | `core/smart_home/device_controller.py` | Appareils connectés génériques | ✅ 7 | ✅ |│ └── communication/ # Annoncespython alexa --list-devices

| **PlaybackManager** | `core/music/playback_manager.py` | Play, pause, next, prev, shuffle | ✅ 9 | ✅ |

| **TuneInManager** | `core/music/tunein_manager.py` | Radios, podcasts | ✅ 3 | ✅ |├── utils/ # Utilitaires```

| **AnnouncementManager** | `core/communication/announcement_manager.py` | Messages multi-pièces | ✅ 4 | ✅ |

| **NotificationManager** | `core/notification_manager.py` | Liste, delete, mark read | ✅ 6 | ✅ |│ ├── logger.py # Configuration Loguru

| **DNDManager** | `core/dnd_manager.py` | Enable/disable par appareil | ✅ 3 | ✅ |

| **EqualizerManager** | `core/audio/equalizer_manager.py` | Bass, mid, treble | ✅ 4 | ✅ |│ ├── config.py # Configuration---

| **BluetoothManager** | `core/audio/bluetooth_manager.py` | Connect, disconnect, list | ✅ 5 | ✅ |

| **DeviceSettingsManager** | `core/settings/device_settings_manager.py` | Wake word, timezone, locale | ✅ 7 | ✅ |│ └── validators.py # Validateurs

| **DeviceManager** | `core/device_manager.py` | Liste appareils, infos | ✅ 10 | ✅ |

| **ListManager** | (intégré) | Listes courses, tâches | ⏳ | ⏳ |├── alexa_auth/ # Authentification## 🚀 Utilisation

| **ActivityManager** | (intégré) | Historique interactions | ⏳ | ⏳ |

│ ├── nodejs/ # Module Node.js auth

### Infrastructure

│ └── alexa_cookie_retriever.py # Récupération cookies### Commandes Actuelles (Format Plat)

| Composant | Fichier | Rôle | Tests | Statut |

|-----------|---------|------|-------|--------|└── tests/ # Tests unitaires

| **StateMachine** | `core/state_machine.py` | 7 états thread-safe | ✅ 25 | ✅ 200 lignes |

| **CircuitBreaker** | `core/circuit_breaker.py` | Protection cascades erreurs | ✅ 18 | ✅ |    └── cli/                      # Tests commandes CLI> **Note:** Une refonte complète en sous-commandes modulaires est en cours (voir ROADMAP.md)

| **CacheService** | `services/cache_service.py` | Mémoire + disque | ✅ 15 | ✅ |

| **SyncService** | `services/sync_service.py` | Sync auto (devices, routines) | ✅ 6 | ✅ |````

| **AlexaAuth** | `alexa_auth/alexa_cookie_retriever.py` | Authentification cookies | ✅ 12 | ✅ |

| **Context** | `cli/context.py` | Singleton centralisant managers | ✅ 8 | ✅ |```bash



---### 🔄 Diagramme de Flux - Architecture Globale# Authentification



## 🛠️ Diagnostic & Monitoringpython alexa --login



### Health Check Complet```mermaidpython alexa --logout



```bashgraph TB

# Diagnostic santé application

python3 scripts/health_check.py    A[Utilisateur] -->|Commande CLI| B[alexa script]# Appareils



# Sortie exemple :    B --> C[CommandParser]python alexa --list-devices

# ═══════════════════════════════════════════════════════════

#              🏥 ALEXA CLI - HEALTH CHECK    C --> D{Validation Connexion}python alexa -d "Chambre" -e "Alexa, quelle heure est-il ?"

# ═══════════════════════════════════════════════════════════

#     D -->|Non connecté| E[ErrorHandler]

# ✅ 1. Configuration               OK

#    └─ alexa_domain: amazon.fr (valide)    D -->|Connecté| F[Context]# Musique

#

# ⚠️  2. Authentification           WARNING    F --> G[CircuitBreaker]python alexa -d "Salon" -s "Bohemian Rhapsody"

#    ├─ Cookie: Présent ✅

#    └─ CSRF token: Manquant ⚠️ (rafraîchir avec ./alexa auth refresh)    G --> H{Appel API}python alexa -d "Salon" -r "France Inter"

#

# ✅ 3. Cache                       OK    H -->|Succès| I[Manager]

#    ├─ 10 fichiers (149.5 Ko total)

#    ├─ Caches critiques: 3/3 présents ✅    H -->|Échec| J[Retry Logic]# Volume

#    │  ├─ devices.json (19.8 Ko)

#    │  ├─ smart_home_all.json (47.4 Ko)    J -->|Max retries| Epython alexa -d "Cuisine" -z 50

#    │  └─ routines.json (39.1 Ko)

#    └─ Erreurs: 2 non-critiques (namedLists 503, activities 404)    J -->|Retry OK| H

#

# ⚠️  4. State Machine              WARNING    I --> K[Response]# Notifications

#    └─ État: 1 (DISCONNECTED) ⚠️

#     K --> L[Output Formatter]python alexa -n

# ✅ 5. Fichiers critiques          OK

#    └─ 8/8 fichiers présents    L --> M[Affichage Résultat]

#

# ✅ 6. Tests                       OK    E --> M# Routines

#    └─ 21 fichiers tests détectés

# ```python alexa --list-routines

# ═══════════════════════════════════════════════════════════

#                        📊 RÉSUMÉ````

# ═══════════════════════════════════════════════════════════

# ### 🔐 Diagramme de Flux - Authentification

# ✅ OK:       4

# ⚠️  Warnings: 2### Architecture Cible (En Développement)

# ❌ Errors:   0

# ````mermaid

# Score santé: 75.0% ⚠️ ACCEPTABLE

# sequenceDiagram```bash

# 💾 Rapport sauvegardé: health_report.json

```    participant User# Sous-commandes modulaires (à venir)



### Vérification Endpoints API    participant CLIpython alexa device list



```bash    participant NodeJSpython alexa music play -d "Salon" -s "Song Name"

# Valider 50+ endpoints Amazon Alexa API

python3 scripts/verify_endpoints.py    participant Amazonpython alexa timer create -d "Cuisine" --duration 10 --label "Pâtes"



# Résultats :    participant APIpython alexa light brightness --entity light.salon --value 80

# 📁 Fichiers analysés: 3

# ✅ Endpoints valides: 50    python alexa notification list --limit 10

# ❌ Endpoints invalides: 0

# ⚠️  Endpoints inconnus: 2 (doc uniquement)    User->>CLI: alexa auth login```

`````

    CLI->>NodeJS: Launch auth script

### État du Cache

    NodeJS->>Amazon: Open browser loginVoir [COMMANDES.md](COMMANDES.md) pour documentation complète.

`````bash

# Statistiques cache détaillées    User->>Amazon: Enter credentials

./alexa cache status

    Amazon->>NodeJS: Return cookies---

# Invalider cache spécifique

./alexa cache invalidate --type routines    NodeJS->>CLI: Save refresh_token



# Nettoyer cache complet    CLI->>API: Exchange token## 🛠️ Développement

./alexa cache clear

```    API->>CLI: Return session cookies



---    CLI->>User: ✅ Connected### Structure du Projet



## 👨‍💻 Développement````



### Structure du Code````



```bash### 🎵 Diagramme de Flux - Commande Musiquealexa_advanced_control/

# Activer environnement développement

source venv/bin/activate├── alexa      # Point d'entrée CLI



# Installer dépendances dev```mermaid├── core/                       # Managers API (17 modules)

pip install -r requirements-dev.txt

graph LR│   ├── state_machine.py

# Workflow standard :

# 1. Lancer tests    A[alexa music play] --> B[MusicCommand]│   ├── circuit_breaker.py

pytest tests/ -v

    B --> C{Validate Args}│   ├── config.py

# 2. Type checking

mypy core/ cli/ --strict    C -->|Invalid| D[Error]│   ├── timers/



# 3. Formatting    C -->|Valid| E[Get Device Serial]│   ├── smart_home/

black core/ cli/ tests/

isort core/ cli/ tests/    E --> F[CircuitBreaker]│   ├── music/



# 4. Linting    F --> G[PlaybackManager]│   ├── communication/

flake8 core/ cli/ tests/

    G --> H[Search Song/Artist]│   ├── lists/

# 5. Script qualité complet

./tests/config/check_quality.sh    H --> I[Get Media ID]│   ├── audio/

`````

    I --> J[Send Play Command]│   └── settings/

### Standards de Qualité

    J --> K[API Alexa]├── cli/                        # CLI modulaire (à venir)

- ✅ **Type Hints** - Obligatoires (mypy strict mode)

- ✅ **Docstrings** - Format Google/NumPy K --> L[Response]│ ├── command_parser.py

- ✅ **Tests** - >80% coverage visé

- ✅ **Thread-Safety** - `threading.RLock()` pour ressources partagées L --> M[Success ✅]│ ├── base_command.py

- ✅ **Multiplateforme** - `pathlib.Path` uniquement (Windows/Linux/macOS)

- ✅ **Logging** - Loguru avec niveaux structurés```│ ├── context.py

- ✅ **Sécurité** - Permissions fichiers 600, sanitization chemins

│ └── commands/

### Écrire un Nouveau Manager

### 💡 Diagramme de Flux - Smart Home├── tests/ # Tests pytest (55 tests)

```````python

# Exemple : core/example/example_manager.py├── alexa_auth/                 # Authentification Node.js



from threading import RLock```mermaid├── utils/                      # Utilitaires

from typing import Optional, Dict, Any

from alexa_auth.alexa_cookie_retriever import AlexaAuthgraph TD└── scripts/                    # Scripts install/uninstall

from core.state_machine import AlexaStateMachine

from services.cache_service import CacheService    A[alexa light brightness] --> B[LightCommand]```

from utils.logger import logger

    B --> C[Validate Entity ID]

class ExampleManager:

    """    C --> D[LightController]### Workflow Développement

    Gestionnaire pour [fonctionnalité].

        D --> E{Get Current State}

    Thread-safe avec cache et circuit breaker.

    """    E --> F[Build Command Payload]```bash



    def __init__(    F --> G[Send to Alexa API]# Activer environnement

        self,

        auth: AlexaAuth,    G --> H{Response OK?}source venv/bin/activate

        state_machine: AlexaStateMachine,

        cache_service: Optional[CacheService] = None    H -->|Yes| I[Update Local State]

    ):

        self._auth = auth    H -->|No| J[Error Handler]# Lancer tests

        self._state_machine = state_machine

        self._cache = cache_service or CacheService()    I --> K[Display Success]pytest tests/ -v --cov=core --cov-report=term-missing

        self._lock = RLock()

            J --> L[Display Error]

    def get_data(self) -> Optional[Dict[str, Any]]:

        """```# Vérifier qualité code

        Récupère données avec cache multi-niveaux.

        ./tests/config/check_quality.sh

        Returns:

            Dict avec données, None si erreur---

        """

        with self._lock:# Type checking

            # 1. Check cache mémoire (TTL 5min)

            cached = self._cache.get("example_data")## 🎯 Cas d'Usagemypy core/ --strict

            if cached:

                logger.debug("Cache hit (mémoire)")

                return cached

            ### 🤖 Automatisation avec Cron# Formatting

            # 2. Check cache disque (TTL 1h)

            disk_cached = self._cache.load_from_file("example_data.json")black core/ cli/ tests/

            if disk_cached:

                logger.debug("Cache hit (disque)")```bashisort core/ cli/ tests/

                self._cache.set("example_data", disk_cached, ttl=300)

                return disk_cached# Réveil doux le matin (crontab)```



            # 3. Fetch depuis API0 7 * * 1-5 /path/to/alexa light brightness --entity light.chambre --value 30

            try:

                response = self._auth.get("/api/example")5 7 * * 1-5 /path/to/alexa music play -d "Chambre" -s "Réveil en douceur"### Standards de Qualité

                if response and response.status_code == 200:

                    data = response.json()

                    # Store cache mémoire + disque

                    self._cache.set("example_data", data, ttl=300)# Extinction automatique le soir- **Type hints:** Obligatoires (mypy strict mode)

                    self._cache.save_to_file(data, "example_data.json")

                    return data0 23 * * * /path/to/alexa light off --entity all- **Docstrings:** Format Google/NumPy

            except Exception as e:

                logger.error(f"Erreur API: {e}")0 23 * * * /path/to/alexa dnd enable -d "Chambre"- **Tests:** >80% coverage

                return None

``````- **Linting:** Black, isort, flake8



### Ajouter des Tests- **Thread-safety:** `threading.RLock()` pour ressources partagées



```python### 📜 Scripts Bash- **Multiplateforme:** `pathlib.Path` uniquement (Windows/Linux/macOS)

# tests/test_example_manager.py



import pytest

from unittest.mock import Mock, patch```bash---

from core.example.example_manager import ExampleManager

#!/bin/bash

@pytest.fixture

def mock_auth():# Routine "Je pars de la maison"## 🧪 Tests

    auth = Mock()

    auth.get.return_value = Mock(status_code=200, json=lambda: {"data": "test"})

    return auth

echo "🏠 Activation mode absence..."### Lancer les Tests

@pytest.fixture

def mock_state_machine():

    sm = Mock()

    sm.state = 2  # CONNECTED# Éteindre toutes les lumières```bash

    return sm

./alexa light off --entity all# Tous les tests

def test_get_data_success(mock_auth, mock_state_machine):

    manager = ExampleManager(mock_auth, mock_state_machine)pytest tests/ -v



    with patch.object(manager._cache, 'get', return_value=None):# Activer DND partout

        result = manager.get_data()

    for device in Salon Chambre Cuisine Bureau; do# Tests spécifiques

    assert result is not None

    assert result["data"] == "test"    ./alexa dnd enable -d "$device"pytest tests/test_state_machine.py -v

    mock_auth.get.assert_called_once_with("/api/example")

donepytest tests/test_circuit_breaker.py -v

def test_get_data_cache_hit(mock_auth, mock_state_machine):

    manager = ExampleManager(mock_auth, mock_state_machine)pytest tests/test_timer_manager.py -v

    cached_data = {"cached": True}

    # Annuler tous les timers

    with patch.object(manager._cache, 'get', return_value=cached_data):

        result = manager.get_data()./alexa timer cancel-all# Avec coverage



    assert result == cached_datapytest tests/ --cov=core --cov-report=html

    mock_auth.get.assert_not_called()  # Pas d'appel API si cache hit

```# Vérifier que tout est OK# Ouvrir htmlcov/index.html dans navigateur



---./alexa device list --json | jq '.[] | select(.online==true) | .accountName'



## 🧪 Tests & Qualité# Tests parallèles (plus rapide)



### Lancer les Testsecho "✅ Maison sécurisée !"pytest tests/ -n auto



```bash````

# Tous les tests (207 tests)

pytest tests/ -v### 🐍 Intégration Python### Écrire des Tests



# Tests avec coverage```pythonVoir `tests/conftest.py` pour fixtures communes (mocks API, state machine, etc.)

pytest tests/ --cov=core --cov=cli --cov-report=html

# Ouvrir htmlcov/index.html dans navigateurimport subprocess



# Tests spécifiquesimport json```python

pytest tests/test_state_machine.py -v

pytest tests/test_device_service.py -vimport pytest



# Tests parallèles (plus rapide)def play_music(device, query):from unittest.mock import Mock, patch

pytest tests/ -n auto

    """Jouer de la musique sur un appareil"""

# Tests avec logs détaillés

pytest tests/ -v --log-cli-level=DEBUG    result = subprocess.run(def test_timer_creation(mock_auth, mock_state_machine):

```````

        ["./alexa", "music", "play", "-d", device, "-s", query, "--json"],    from core.timers import TimerManager

### Statistiques Qualité Actuelles

        capture_output=True,

```bash

# Rapport complet        text=True    timer_mgr = TimerManager(mock_auth, mock_state_machine)

./tests/config/check_quality.sh

    )

# Résultats :

# ✅ 207 tests - 100% succès    return json.loads(result.stdout)    with patch.object(mock_auth, 'post') as mock_post:

# ✅ Santé globale - 75% (4 OK, 2 warnings)

# ✅ Type hints - 100% (mypy validé)        mock_post.return_value = {"id": "timer-123", "status": "ON"}

# ✅ Endpoints API - 50+ validés, 0 invalides

# ✅ Cache - 3/3 caches critiques présentsdef get_all_devices():

# ✅ 149 fichiers Python

# ✅ 39 commits (10 derniers jours)    """Récupérer la liste des appareils"""        result = timer_mgr.create_timer("ABC123", "ECHO_DEVICE", 15, "Test")

```

    result = subprocess.run(

### Benchmarks Performance

        ["./alexa", "device", "list", "--json"],        assert result is not None

`````bash

# Synchronisation complète (devices + smart_home + routines)        capture_output=True,        assert result["id"] == "timer-123"

time ./alexa sync all

# ~1.7s avec cache chaud        text=True        mock_post.assert_called_once()

# ~4.2s avec cache froid (appels API)

    )```

# Récupération routines (avec cache)

time ./alexa routine list    return json.loads(result.stdout)

# ~0.15s (cache hit mémoire)

# ~0.35s (cache hit disque)---

# ~1.2s (cache miss, API call)

```# Utilisation



---devices = get_all_devices()## 🗺️ Roadmap



## 🤝 Contributionfor device in devices:



### Workflow Contribution    if device['online']:### État Actuel (7 octobre 2025)



1. **Fork** le projet        print(f"✅ {device['accountName']} is online")

2. **Créer** une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)

3. **Développer** en respectant les standards````- ✅ **API Managers:** 17 modules complets (100%)

4. **Tester** (`pytest tests/ -v`)

5. **Vérifier** qualité (`./tests/config/check_quality.sh`)- ✅ **Tests:** 55 tests pytest (100%)

6. **Commit** (`git commit -m '✨ Ajout fonctionnalité X'`)

7. **Push** (`git push origin feature/nouvelle-fonctionnalite`)### 🔗 Home Assistant Integration- ⏳ **CLI Refonte:** Architecture modulaire (0%)

8. **Pull Request** vers branche principale



### Checklist Pull Request

```yaml### Sprints Prévus (3-4 semaines)

- [ ] Tests ajoutés/mis à jour (>80% coverage)

- [ ] Type hints complets (mypy strict mode passe)# configuration.yaml

- [ ] Docstrings format Google/NumPy

- [ ] Black formatting appliqué (`black .`)shell_command:1. **Sprint 1 (Semaine 1):** Foundation

- [ ] isort appliqué (`isort .`)

- [ ] `./tests/config/check_quality.sh` passe sans erreur  alexa_play_music: "/path/to/alexa music play -d '{{ device }}' -s '{{ query }}'"

- [ ] Documentation mise à jour si nécessaire

- [ ] Thread-safety vérifié (`RLock` si ressources partagées)  alexa_announce: "/path/to/alexa announcement send -m '{{ message }}'"   - `cli/command_parser.py`, `base_command.py`, `context.py`

- [ ] Multiplateforme testé (Windows + Linux si possible)

  alexa_light_on: "/path/to/alexa light on --entity {{ entity }}"   - Commandes `auth` et `device`

### Convention Commits



```bash

# Format : <type>(<scope>): <description>automation:2. **Sprint 2 (Semaine 1-2):** Fonctionnalités Principales



✨ feat(routines): Ajout RoutineManager avec cache  - alias: "Annonce porte d'entrée"

🐛 fix(auth): Correction refresh token

📝 docs(readme): Mise à jour installation    trigger:   - Commandes `music`, `timer`, `alarm`

✅ test(timers): Tests TimerManager complets

♻️ refactor(cache): Simplification CacheService      - platform: state

🔥 perf(api): Optimisation appels API

🔒 security(auth): Permissions fichiers 600        entity_id: binary_sensor.porte_entree3. **Sprint 3 (Semaine 2):** Smart Home

`````

        to: 'on'

---

    action:   - Commandes `light`, `thermostat`, `smarthome`

## 📄 License

      - service: shell_command.alexa_announce

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour détails.

        data:4. **Sprint 4 (Semaine 2-3):** Communication

---

          message: "La porte d'entrée vient d'être ouverte"

## 🙏 Remerciements

```  - Commandes`notification`, `dnd`, `announcement`

- **[Apollon77/alexa-remote](https://github.com/Apollon77/alexa-remote)** - Bibliothèque Node.js pour authentification

- **Amazon Alexa API** - API non-officielle documentée par la communauté

- **Communauté Python** - Outils de développement exceptionnels (pytest, mypy, black, loguru)

---5. **Sprint 5 (Semaine 3):** Compléments

---

## 📞 Support

## 🔧 Options Globales - Commandes `reminder`, `list`, `activity`

- 🐛 **Issues** : [GitHub Issues](https://github.com/weedmanu/alexa_advanced_control/issues)

- 💬 **Discussions** : [GitHub Discussions](https://github.com/weedmanu/alexa_advanced_control/discussions)

- 📖 **Documentation** : Voir fichiers `docs/` (à venir)

| Option | Description | Exemple |6. **Sprint 6 (Semaine 3-4):** Finalisation

---

|--------|-------------|---------| - Commandes `audio`, `settings`, `routine`, `multiroom`

## 🗺️ Roadmap

| `--help`, `-h` | Afficher l'aide | `./alexa --help` | - Documentation, tests E2E, CI/CD

### ✅ Complété (v1.0)

| `--version` | Version du programme | `./alexa --version` |

- [x] 17+ Managers opérationnels

- [x] RoutineManager avec cache multi-niveaux| `--verbose`, `-v` | Mode verbeux | `./alexa -v device list` |Voir [ROADMAP.md](ROADMAP.md) pour plan détaillé complet.

- [x] Vérification 50+ endpoints API

- [x] Health check complet| `--debug` | Mode debug complet | `./alexa --debug music play ...` |

- [x] 207 tests (100% succès)

- [x] State machine thread-safe| `--json` | Sortie JSON | `./alexa --json device list` |### Reprise du Projet

- [x] Circuit breaker pattern

- [x] Sync automatique au login

| `-d`, `--device` | Appareil cible | `./alexa -d "Salon" music play` |Pour reprendre le développement, voir [REPRISE_PROJET.md](REPRISE_PROJET.md) - guide complet pour humains et IA.

### 🔄 En Cours (v1.1)

| `--config` | Config personnalisé | `./alexa --config custom.conf` |

- [ ] Documentation complète API endpoints

- [ ] Tests end-to-end CLI---

- [ ] Optimisations performance (parallélisation API)

- [ ] Compression cache JSON---

### ⏳ Prévu (v2.0)## 📚 Documentation

- [ ] Interface GUI (Qt/PyQt)## 🧪 Tests & Qualité

- [ ] API REST pour intégrations externes

- [ ] Support multi-comptes Amazon### Guides Utilisateur

- [ ] Dashboard web monitoring

- [ ] Plugin system extensible### Exécuter les tests

- [ ] Support Docker/Podman

- **[USER_GUIDE.md](USER_GUIDE.md)** - Guide complet d'utilisation (1000+ lignes)

---

````bash - Installation et configuration

<div align="center">

# Tous les tests  - Toutes les commandes avec exemples

**Développé avec ❤️ pour la communauté Alexa**

pytest tests/ -v  - Scénarios d'utilisation réels

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org)

[![Amazon Alexa](https://img.shields.io/badge/Amazon_Alexa-00CAFF?logo=amazon-alexa&logoColor=white)](https://alexa.amazon.com)  - Dépannage et FAQ



**Version 1.0.0** • Janvier 2025# Tests avec coverage



</div>pytest --cov=core --cov=cli --cov-report=html### Documentation Technique


open htmlcov/index.html

- **[API_ANALYSIS.md](API_ANALYSIS.md)** - Analyse des API Amazon Alexa

# Tests d'une catégorie

pytest tests/cli/test_music_commands.py -v  - 33 endpoints documentés

```  - Architecture d'authentification

  - Gestion sécurité et rate limiting

### Vérifier la qualité  - Compatibilité multi-régions



```bash- **[QUALITY_REPORT.md](QUALITY_REPORT.md)** - Rapport de qualité du code

# Script de qualité complet  - 171 tests (100% réussite) ✅

./tests/config/check_quality.sh  - PYLINT 9.62/10 ✅

  - Coverage 41.51%

# Formatage manuel  - Analyse complète qualité

black core/ cli/ tests/

isort core/ cli/ tests/### Démarrage Rapide



# Linting```bash

pylint core/ cli/# Voir toutes les commandes disponibles

mypy core/ cli/./alexa --help

````

# Guide d'une commande spécifique

### Statistiques Qualité./alexa music --help

- ✅ **171 tests** - 100% de réussite# Exemples pratiques

- ✅ **PYLINT 9.62/10** - Excellent./alexa music play -d "Salon" -s "Queen"

- ✅ **Coverage 41.51%** - En amélioration./alexa timer create -d "Cuisine" --duration 10

- ✅ **Type hints** - 100% du code./alexa light brightness --entity light.salon --value 80

- ✅ **PEP8** - Conforme (Black/Isort)```

- ✅ **Sécurité** - Validé Bandit

Pour plus de détails, consultez le [USER_GUIDE.md](USER_GUIDE.md).

---

---

## 🐛 Dépannage

## 🤝 Contribution

### Problème: "Not authenticated"

````bash### Contribuer

./alexa auth status    # Vérifier

./alexa auth login     # Se reconnecter1. Fork le projet

```2. Créer une branche feature (`git checkout -b feature/nouvelle-commande`)

3. Respecter les standards de qualité (tests, type hints, docstrings)

### Problème: "Device not found"4. Commit (`git commit -m '✨ Ajout commande X'`)

```bash5. Push (`git push origin feature/nouvelle-commande`)

./alexa device list    # Voir noms exacts6. Créer Pull Request vers `cli-dev`

# Utiliser le nom exact (sensible à la casse)

```### Checklist PR



### Problème: Commande lente- [ ] Tests ajoutés/mis à jour (>80% coverage)

```bash- [ ] Type hints complets (mypy passe)

./alexa auth refresh   # Rafraîchir token- [ ] Docstrings format Google/NumPy

# ou- [ ] Black formatting appliqué

./alexa --debug ...    # Mode debug pour logs- [ ] `./tests/config/check_quality.sh` passe sans erreur

```- [ ] Documentation mise à jour si nécessaire

- [ ] Multiplateforme testé (Windows + Linux si possible)

### Logs détaillés

```bash---

# Activer le mode debug

export ALEXA_DEBUG=1## 📄 License

./alexa --debug device list

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour détails.

# Voir les logs

tail -f ~/.alexa/logs/alexa.log---

````

## 🙏 Remerciements

---

- [Apollon77/alexa-remote](https://github.com/Apollon77/alexa-remote) - Bibliothèque Node.js pour authentification

## 🤝 Contribution- Communauté Python pour outils de développement exceptionnels

Les contributions sont les bienvenues ! Voici comment participer :---

1. **Fork** le projet## 📞 Support

2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)

3. **Commiter** vos changements (`git commit -m 'Add AmazingFeature'`)- **Issues:** [GitHub Issues](https://github.com/weedmanu/alexa_advanced_control/issues)

4. **Pousser** vers la branche (`git push origin feature/AmazingFeature`)- **Documentation:** Voir [COMMANDES.md](COMMANDES.md) et [ROADMAP.md](ROADMAP.md)

5. **Ouvrir** une Pull Request- **Guide Reprise:** [REPRISE_PROJET.md](REPRISE_PROJET.md)

### Guidelines---

- ✅ Suivre le style PEP8 (Black/Isort)**Développé avec ❤️ pour la communauté Alexa**

- ✅ Ajouter des tests pour les nouvelles features
- ✅ Maintenir coverage > 40%
- ✅ Documenter avec docstrings
- ✅ Passer `./tests/config/check_quality.sh` avant commit

---

## 📜 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **Amazon Alexa API** - Pour l'API (non officielle)
- **alexa-remote-control** - Pour l'inspiration initiale
- **alexa-cookie** - Pour le module d'authentification Node.js
- **Community** - Pour les retours et contributions

---

## 📞 Support & Contact

- 🐛 **Issues**: [GitHub Issues](https://github.com/weedmanu/alexa_advanced_control/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/weedmanu/alexa_advanced_control/discussions)
- 📧 **Email**: Voir profil GitHub
- 📖 **Wiki**: [GitHub Wiki](https://github.com/weedmanu/alexa_advanced_control/wiki)

---

## 🗺️ Roadmap

### Version 2.1 (Planifiée)

- [ ] Interface GUI (Qt/PyQt)
- [ ] API REST pour intégrations
- [ ] Support multi-comptes
- [ ] Cache intelligent
- [ ] Tests d'intégration end-to-end

### Version 3.0 (Future)

- [ ] Support Alexa Skills
- [ ] Gestion avancée routines
- [ ] Dashboard web
- [ ] Plugin system
- [ ] Support Docker

---

<div align="center">

**Fait avec ❤️ par M@nu**

[![GitHub](https://img.shields.io/badge/GitHub-weedmanu-181717?logo=github)](https://github.com/weedmanu)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Amazon Alexa](https://img.shields.io/badge/Amazon_Alexa-00CAFF?logo=amazon-alexa&logoColor=white)](https://alexa.amazon.com)

**Version 2.0.0** • 7 janvier 2025

</div>
