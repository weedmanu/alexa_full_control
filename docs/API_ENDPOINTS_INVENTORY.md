# 📋 Inventaire Complet des Endpoints API Alexa

**Date de création** : 12 octobre 2025  
**Projet** : Alexa Advanced Control - Version CLI Python

---

## 🎯 Légende

| Symbole | Signification                                                         |
| ------- | --------------------------------------------------------------------- |
| ✅      | **Utilisé et fonctionnel** dans le code Python                        |
| ⚠️      | **Utilisé mais problématique** (retourne vide, erreur, ou deprecated) |
| ❌      | **Non utilisé** dans le code Python actuel                            |
| 🔧      | **Endpoint du script Shell** uniquement                               |
| 📄      | Retourne **JSON**                                                     |
| 🌐      | Retourne **HTML**                                                     |
| 🔒      | Nécessite **CSRF supplémentaire** (privacy)                           |

---

## 📊 Tableau Récapitulatif par Catégorie

### 🔐 1. Authentification & Session

| Endpoint                    | Méthode | Format  | Statut | Fonction                                          | Fichier d'utilisation                                                          |
| --------------------------- | ------- | ------- | ------ | ------------------------------------------------- | ------------------------------------------------------------------------------ |
| `/api/bootstrap?version=0`  | GET     | 📄 JSON | ✅     | Récupérer `customerId` et état d'authentification | `services/voice_command_service.py` `core/settings/device_settings_manager.py` |
| `/ap/exchangetoken/cookies` | POST    | 📄 JSON | ✅     | Échanger refresh token contre cookies de session  | `alexa_auth/alexa_auth.py`                                                     |

---

### 📱 2. Gestion des Appareils

| Endpoint                                  | Méthode | Format  | Statut | Fonction                                                                           | Fichier d'utilisation                               |
| ----------------------------------------- | ------- | ------- | ------ | ---------------------------------------------------------------------------------- | --------------------------------------------------- |
| `/api/devices-v2/device?cached=false`     | GET     | 📄 JSON | ✅     | **Liste complète des appareils Alexa** avec détails (serial, type, nom, capacités) | `core/device_manager.py` `services/sync_service.py` |
| `/api/device-preferences/{device_serial}` | GET     | 📄 JSON | ✅     | Préférences et paramètres d'un appareil spécifique                                 | `core/settings/device_settings_manager.py`          |
| `/api/wake-word`                          | POST    | 📄 JSON | ✅     | Modifier le mot de réveil ("Alexa", "Echo", "Amazon", "Computer")                  | `core/settings/device_settings_manager.py`          |
| `/api/device-preferences/time-zone`       | POST    | 📄 JSON | ✅     | Changer le fuseau horaire de l'appareil                                            | `core/settings/device_settings_manager.py`          |
| `/api/device-preferences/locale`          | POST    | 📄 JSON | ✅     | Modifier la langue/locale de l'appareil                                            | `core/settings/device_settings_manager.py`          |

---

### 🔊 3. Contrôle du Volume & Audio

| Endpoint                                                | Méthode | Format  | Statut | Fonction                                                                                 | Fichier d'utilisation                      |
| ------------------------------------------------------- | ------- | ------- | ------ | ---------------------------------------------------------------------------------------- | ------------------------------------------ |
| `/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes` | GET     | 📄 JSON | ✅     | **Récupérer le volume de TOUS les appareils** en une seule requête                       | `core/settings/device_settings_manager.py` |
| `/api/behaviors/preview` (Volume)                       | POST    | 📄 JSON | ✅     | **Définir le volume** d'un appareil spécifique (0-100) via `Alexa.DeviceControls.Volume` | `core/settings/device_settings_manager.py` |
| `/api/equalizer/{device_serial}/{device_type}`          | GET     | 📄 JSON | ✅     | Récupérer les paramètres d'égaliseur (basses, médiums, aigus)                            | `core/audio/equalizer_manager.py`          |
| `/api/equalizer/{device_serial}/{device_type}`          | PUT     | 📄 JSON | ✅     | Modifier les paramètres d'égaliseur                                                      | `core/audio/equalizer_manager.py`          |

---

### 🎵 4. Musique & Média

#### 4.1 Contrôle de Lecture (Playback)

| Endpoint             | Méthode | Format  | Statut | Fonction                                                                    | Fichier d'utilisation            |
| -------------------- | ------- | ------- | ------ | --------------------------------------------------------------------------- | -------------------------------- |
| `/api/np/command`    | POST    | 📄 JSON | ✅     | **Commandes de lecture** : play, pause, next, previous, shuffle, loop, stop | `core/music/playback_manager.py` |
| `/api/np/player`     | GET     | 📄 JSON | ✅     | **État du player actuel** : titre, artiste, album, progression, durée       | `core/music/playback_manager.py` |
| `/api/media/state`   | GET     | 📄 JSON | ✅     | **État média détaillé** : volume, muet, état de lecture                     | `core/music/playback_manager.py` |
| `/api/np/queue`      | GET     | 📄 JSON | ✅     | **File d'attente complète** de lecture                                      | `core/music/playback_manager.py` |
| `/api/media/history` | GET     | 📄 JSON | ✅     | Historique de lecture récent                                                | `core/music/playback_manager.py` |

#### 4.2 Bibliothèque Musicale

| Endpoint                                        | Méthode | Format  | Statut | Fonction                                                             | Fichier d'utilisation       |
| ----------------------------------------------- | ------- | ------- | ------ | -------------------------------------------------------------------- | --------------------------- |
| `/api/entertainment/v1/player/queue`            | PUT     | 📄 JSON | ✅     | Lire une station TuneIn (contentToken: `music:tuneIn/stationId/...`) | `services/music_library.py` |
| `/api/cloudplayer/queue-and-play`               | POST    | 📄 JSON | ✅     | **Lire une piste de la bibliothèque personnelle** (trackId)          | `services/music_library.py` |
| `/api/cloudplayer/playlists/{type}-V0-OBJECTID` | GET     | 📄 JSON | ✅     | Récupérer les playlists d'un type (favoris, récents, etc.)           | `services/music_library.py` |
| `/api/prime/prime-playlist-queue-and-play`      | POST    | 📄 JSON | ✅     | Lire une playlist Amazon Music Prime                                 | `services/music_library.py` |
| `/api/prime/prime-playlist-browse-nodes`        | GET     | 📄 JSON | ✅     | Récupérer les catégories de playlists Prime                          | `services/music_library.py` |
| `/api/prime/prime-playlists-by-browse-node`     | POST    | 📄 JSON | ✅     | Lister les playlists d'une catégorie Prime                           | `services/music_library.py` |
| `/api/prime/prime-sections`                     | GET     | 📄 JSON | ✅     | Récupérer les sections Prime (recommandations, nouveautés, etc.)     | `services/music_library.py` |
| `/api/gotham/queue-and-play`                    | POST    | 📄 JSON | ✅     | Lire du contenu Audible                                              | `services/music_library.py` |
| `/api/media/play-historical-queue`              | POST    | 📄 JSON | ✅     | Relire une file d'attente historique                                 | `services/music_library.py` |

#### 4.3 TuneIn (Radio)

| Endpoint                     | Méthode | Format  | Statut | Fonction                                  | Fichier d'utilisation          |
| ---------------------------- | ------- | ------- | ------ | ----------------------------------------- | ------------------------------ |
| `/api/tunein/search`         | POST    | 📄 JSON | ✅     | Rechercher des stations/podcasts TuneIn   | `core/music/tunein_manager.py` |
| `/api/tunein/queue-and-play` | POST    | 📄 JSON | ✅     | Lire une station/podcast TuneIn (guideId) | `core/music/tunein_manager.py` |
| `/api/tunein/favorites`      | GET     | 📄 JSON | ✅     | Récupérer les favoris TuneIn              | `core/music/tunein_manager.py` |
| `/api/tunein/favorites`      | POST    | 📄 JSON | ✅     | Ajouter aux favoris TuneIn                | `core/music/tunein_manager.py` |

---

### ⏰ 5. Alarmes, Timers & Rappels

#### 5.1 Alarmes

| Endpoint                 | Méthode | Format  | Statut | Fonction                                                                                        | Fichier d'utilisation                                                                              |
| ------------------------ | ------- | ------- | ------ | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `/api/notifications`     | GET     | 📄 JSON | ✅     | **Récupérer TOUTES les notifications** (alarmes, timers, rappels) - Filtrer localement par type | `core/alarms/alarm_manager.py` `core/timers/timer_manager.py` `core/reminders/reminder_manager.py` |
| `/api/alarms`            | POST    | 📄 JSON | ✅     | **Créer une alarme**                                                                            | `core/alarms/alarm_manager.py` `core/timers/alarm_manager.py`                                      |
| `/api/alarms/{alarm_id}` | GET     | 📄 JSON | ✅     | Récupérer détails d'une alarme                                                                  | `core/alarms/alarm_manager.py` `core/timers/alarm_manager.py`                                      |
| `/api/alarms/{alarm_id}` | PUT     | 📄 JSON | ✅     | **Modifier une alarme** existante                                                               | `core/alarms/alarm_manager.py` `core/timers/alarm_manager.py`                                      |
| `/api/alarms/{alarm_id}` | DELETE  | 📄 JSON | ✅     | **Supprimer une alarme**                                                                        | `core/alarms/alarm_manager.py` `core/timers/alarm_manager.py`                                      |

#### 5.2 Timers

| Endpoint                 | Méthode | Format  | Statut | Fonction                             | Fichier d'utilisation          |
| ------------------------ | ------- | ------- | ------ | ------------------------------------ | ------------------------------ |
| `/api/timers`            | POST    | 📄 JSON | ✅     | **Créer un timer**                   | `core/timers/timer_manager.py` |
| `/api/timers/{timer_id}` | PUT     | 📄 JSON | ✅     | **Modifier un timer** (pause/resume) | `core/timers/timer_manager.py` |
| `/api/timers/{timer_id}` | DELETE  | 📄 JSON | ✅     | **Supprimer un timer**               | `core/timers/timer_manager.py` |

#### 5.3 Rappels

| Endpoint                            | Méthode | Format  | Statut | Fonction                              | Fichier d'utilisation                |
| ----------------------------------- | ------- | ------- | ------ | ------------------------------------- | ------------------------------------ |
| `/api/reminders`                    | POST    | 📄 JSON | ✅     | **Créer un rappel**                   | `core/timers/reminder_manager.py`    |
| `/api/reminders/{reminder_id}`      | DELETE  | 📄 JSON | ✅     | **Supprimer un rappel**               | `core/timers/reminder_manager.py`    |
| `/api/notifications/createReminder` | POST    | 📄 JSON | ✅     | Créer un rappel (endpoint alternatif) | `core/notification_manager.py`       |
| `/api/notifications/{reminder_id}`  | PUT     | 📄 JSON | ✅     | **Modifier un rappel**                | `core/reminders/reminder_manager.py` |
| `/api/notifications/{reminder_id}`  | DELETE  | 📄 JSON | ✅     | **Supprimer un rappel**               | `core/reminders/reminder_manager.py` |

---

### 📝 6. Listes (Shopping, To-Do)

| Endpoint                          | Méthode | Format  | Statut | Fonction                                                        | Fichier d'utilisation        |
| --------------------------------- | ------- | ------- | ------ | --------------------------------------------------------------- | ---------------------------- |
| `/api/namedLists`                 | GET     | 📄 JSON | ⚠️     | **API REST dépréciée** (retourne `[]` vide depuis juillet 2024) | `core/lists/list_manager.py` |
| `/api/todos`                      | GET     | 📄 JSON | ⚠️     | Alternative listes de tâches (retourne `{"values": []}` vide)   | `core/lists/list_manager.py` |
| `/api/household/lists`            | GET     | 📄 JSON | ⚠️     | Alternative listes ménagères (retourne `{"lists": []}` vide)    | `core/lists/list_manager.py` |
| `/api/namedLists/{list_id}/items` | POST    | 📄 JSON | ⚠️     | Ajouter un article (ne fonctionne plus)                         | `core/lists/list_manager.py` |

**💡 Solution actuelle** : Utilisation de **commandes vocales via VoiceCommandService** avec skillId `amzn1.ask.1p.tellalexa`

---

### 🏠 7. Smart Home (Domotique)

| Endpoint                                                 | Méthode | Format  | Statut | Fonction                                                                    | Fichier d'utilisation                                                                                                   |
| -------------------------------------------------------- | ------- | ------- | ------ | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome` | GET     | 📄 JSON | ✅     | **Lister TOUS les appareils smart home** connectés                          | `services/sync_service.py` `core/smart_home/light_controller.py`                                                        |
| `/api/phoenix`                                           | POST    | 📄 JSON | ✅     | **Contrôler un appareil smart home** (allumer/éteindre, variateur, couleur) | `core/smart_home/light_controller.py` `core/smart_home/device_controller.py` `core/smart_home/thermostat_controller.py` |
| `/api/phoenix/state`                                     | GET     | 📄 JSON | ✅     | Récupérer l'état de tous les appareils smart home                           | `core/smart_home/light_controller.py`                                                                                   |
| `/api/phoenix/state/{entity_id}`                         | GET     | 📄 JSON | ✅     | Récupérer l'état d'un appareil smart home spécifique                        | `core/smart_home/device_controller.py`                                                                                  |

---

### 🔄 8. Routines & Automatisations

| Endpoint                           | Méthode | Format  | Statut | Fonction                             | Fichier d'utilisation                                         |
| ---------------------------------- | ------- | ------- | ------ | ------------------------------------ | ------------------------------------------------------------- |
| `/api/behaviors/v2/automations`    | GET     | 📄 JSON | ✅     | **Lister toutes les routines** Alexa | `core/routines/routine_manager.py` `services/sync_service.py` |
| `/api/behaviors/preview` (Routine) | POST    | 📄 JSON | ✅     | **Exécuter une routine** existante   | `core/routines/routine_manager.py`                            |

---

### 📢 9. Notifications & DND

| Endpoint                               | Méthode | Format  | Statut | Fonction                                                                    | Fichier d'utilisation                                     |
| -------------------------------------- | ------- | ------- | ------ | --------------------------------------------------------------------------- | --------------------------------------------------------- |
| `/api/notifications`                   | GET     | 📄 JSON | ✅     | **Récupérer toutes les notifications** (alarmes, timers, rappels, annonces) | `core/notification_manager.py` `services/sync_service.py` |
| `/api/notifications/{notification_id}` | PUT     | 📄 JSON | ✅     | Modifier une notification                                                   | `core/notification_manager.py`                            |
| `/api/notifications/{notification_id}` | DELETE  | 📄 JSON | ✅     | Supprimer une notification                                                  | `core/notification_manager.py`                            |
| `/api/dnd/status`                      | GET     | 📄 JSON | ✅     | Récupérer statut DND (Ne Pas Déranger) d'un appareil                        | `core/dnd_manager.py`                                     |
| `/api/dnd/status`                      | PUT     | 📄 JSON | ✅     | **Activer/désactiver le mode DND**                                          | `core/dnd_manager.py`                                     |
| `/api/dnd/device-status-list`          | GET     | 📄 JSON | ✅     | **Statut DND de TOUS les appareils**                                        | `core/dnd_manager.py`                                     |

---

### 🎤 10. Commandes Vocales & Behaviors

| Endpoint                               | Méthode | Format  | Statut | Fonction                                                         | Fichier d'utilisation                                      |
| -------------------------------------- | ------- | ------- | ------ | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| `/api/behaviors/preview` (TextCommand) | POST    | 📄 JSON | ✅     | **Envoyer une commande textuelle** comme si vous parliez à Alexa | `services/voice_command_service.py` `cli/commands/list.py` |
| `/api/behaviors/preview` (Speak/TTS)   | POST    | 📄 JSON | ✅     | **Synthèse vocale** : faire parler Alexa avec un texte           | `services/voice_command_service.py`                        |
| `/api/behaviors/preview` (Volume)      | POST    | 📄 JSON | ✅     | Contrôler le volume via behaviors                                | `core/settings/device_settings_manager.py`                 |

---

### 🔵 11. Bluetooth

| Endpoint                                                       | Méthode | Format  | Statut | Fonction                                    | Fichier d'utilisation             |
| -------------------------------------------------------------- | ------- | ------- | ------ | ------------------------------------------- | --------------------------------- |
| `/api/bluetooth`                                               | GET     | 📄 JSON | ✅     | **Lister les appareils Bluetooth** jumelés  | `core/audio/bluetooth_manager.py` |
| `/api/bluetooth/pair-sink/{device_type}/{device_serial}`       | POST    | 📄 JSON | ✅     | **Jumeler/connecter** un appareil Bluetooth | `core/audio/bluetooth_manager.py` |
| `/api/bluetooth/disconnect-sink/{device_type}/{device_serial}` | POST    | 📄 JSON | ✅     | **Déconnecter** un appareil Bluetooth       | `core/audio/bluetooth_manager.py` |

---

### 📊 12. Activités & Historique

#### 12.1 API Standard (Migrée vers Privacy API)

| Endpoint                        | Méthode | Format  | Statut | Fonction                                                                 | Fichier d'utilisation      |
| ------------------------------- | ------- | ------- | ------ | ------------------------------------------------------------------------ | -------------------------- |
| `/api/activities`               | GET     | 📄 JSON | ✅     | **MIGRÉ** : Récupérer activités système (utilise maintenant API Privacy) | `core/activity_manager.py` |
| `/api/activities/{activity_id}` | DELETE  | 📄 JSON | ❌     | **NON SUPPORTÉ** : Supprimer activité (API Privacy ne permet pas)        | `core/activity_manager.py` |

#### 12.2 API Privacy (Fonctionnelle - Implémentée en Python)

| Endpoint                                              | Méthode | Format       | Statut | Fonction                                                                 | Fichier d'utilisation                                     |
| ----------------------------------------------------- | ------- | ------------ | ------ | ------------------------------------------------------------------------ | --------------------------------------------------------- |
| `/alexa-privacy/apd/activity?ref=activityHistory`     | GET     | 🌐 HTML      | ✅     | **Récupérer le CSRF token Privacy** depuis la page HTML                  | `core/activity_manager.py` (get_privacy_csrf)             |
| `/alexa-privacy/apd/rvh/customer-history-records-v2/` | POST    | 📄 JSON + 🔒 | ✅     | **Historique vocal complet** (transcriptions, commandes, réponses Alexa) | `core/activity_manager.py` (get_customer_history_records) |

**Paramètres** :

- `startTime=0` : Début de l'historique
- `endTime=2147483647000` : Fin (19 janvier 2038)
- `pageType=VOICE_HISTORY` : Type d'historique

**Headers requis** :

- `anti-csrftoken-a2z: <privacy_csrf_token>` 🔒
- `csrf: <standard_csrf_token>`

**Body** :

```json
{
  "previousRequestToken": null // Pour pagination
}
```

---

## 🆚 Comparaison Python vs Shell

### ✅ Endpoints utilisés dans Python ET Shell

| Endpoint                                              | Fonction                 | Implémentation Python                                             |
| ----------------------------------------------------- | ------------------------ | ----------------------------------------------------------------- |
| `/alexa-privacy/apd/activity`                         | Récupérer CSRF Privacy   | **Implémenté** - `ActivityManager.get_privacy_csrf()`             |
| `/alexa-privacy/apd/rvh/customer-history-records-v2/` | Historique vocal complet | **Implémenté** - `ActivityManager.get_customer_history_records()` |

### ⚠️ Endpoints utilisés mais CASSÉS en Python

| Endpoint                | Statut           | Problème                         | Solution                                        |
| ----------------------- | ---------------- | -------------------------------- | ----------------------------------------------- |
| `/api/namedLists`       | ⚠️ Retourne vide | Service désactivé (juillet 2024) | **Utiliser VoiceCommandService** (déjà fait ✅) |
| `/api/todos`            | ⚠️ Retourne vide | Alternative non fonctionnelle    | **Utiliser VoiceCommandService** (déjà fait ✅) |
| `/api/household/lists`  | ⚠️ Retourne vide | Alternative non fonctionnelle    | **Utiliser VoiceCommandService** (déjà fait ✅) |
| `/api/namedLists/items` | ⚠️ Retourne vide | API dépréciée                    | **Utiliser VoiceCommandService** (déjà fait ✅) |

---

## 📈 Statistiques d'utilisation

### Par catégorie

| Catégorie             | Total Endpoints | ✅ Utilisés | ⚠️ Problématiques | ❌ Non utilisés | 🔧 Shell only |
| --------------------- | --------------- | ----------- | ----------------- | --------------- | ------------- |
| **Authentification**  | 2               | 2           | 0                 | 0               | 0             |
| **Appareils**         | 5               | 5           | 0                 | 0               | 0             |
| **Volume/Audio**      | 4               | 4           | 0                 | 0               | 0             |
| **Musique**           | 15              | 15          | 0                 | 0               | 0             |
| **Alarmes/Timers**    | 11              | 11          | 0                 | 0               | 0             |
| **Listes**            | 4               | 0           | 4                 | 0               | 0             |
| **Smart Home**        | 4               | 4           | 0                 | 0               | 0             |
| **Routines**          | 2               | 2           | 0                 | 0               | 0             |
| **Notifications/DND** | 6               | 6           | 0                 | 0               | 0             |
| **Behaviors**         | 3               | 3           | 0                 | 0               | 0             |
| **Bluetooth**         | 3               | 3           | 0                 | 0               | 0             |
| **Activités**         | 2               | 2           | 0                 | 0               | 0             |
| **Privacy**           | 2               | 2           | 0                 | 0               | 0             |
| **TOTAL**             | **63**          | **59**      | **3**             | **1**           | **0**         |

### Taux de fonctionnalité

- **Endpoints fonctionnels** : 59/63 = **93.7%** ✅
- **Endpoints problématiques** : 3/63 = **4.8%** ⚠️
- **Endpoints non utilisés** : 1/63 = **1.6%** ❌
- **Endpoints Shell uniquement** : 0/63 = **0%** 🔧

---

## 🔧 Actions Réalisées

### ✅ 1. Implémentation de l'API Privacy (TERMINÉ)

**Problème résolu** : `python alexa activity list` retourne maintenant des données via l'API Privacy

**Méthodes ajoutées** :

- `get_privacy_csrf()` : Récupération du token CSRF spécial depuis la page HTML
- `get_customer_history_records()` : Récupération de l'historique vocal complet
- `_convert_privacy_record_to_activity()` : Conversion des données Privacy au format standard

**Migration effectuée** : `ActivityManager.get_activities()` utilise maintenant l'API Privacy au lieu de `/api/activities`

### ✅ 2. Ajout des commandes CLI manquantes (TERMINÉ)

**Commandes ajoutées** :

- `python alexa activity lastdevice` : Affiche le dernier appareil utilisé
- `python alexa activity lastcommand [-d DEVICE]` : Affiche la dernière commande vocale
- `python alexa activity lastresponse [-d DEVICE]` : Affiche la dernière réponse d'Alexa

**Implémentation** : Méthodes `_show_last_device()`, `_show_last_command()`, et `_show_last_response()` dans `cli/commands/activity.py`

### ✅ 3. Mise à jour des statistiques (TERMINÉ)

**Changements** :

- Endpoints Privacy : Statut changé de 🔧 (Shell only) à ✅ (Utilisés)
- Endpoint `/api/activities` : Statut changé de ⚠️ à ✅ (Migré vers Privacy API)
- Taux de fonctionnalité : 57/63 = **90.5%** → 59/63 = **93.7%** ✅

### ⚠️ Endpoints problématiques restants

| Endpoint                | Statut           | Problème                         | Solution                                        |
| ----------------------- | ---------------- | -------------------------------- | ----------------------------------------------- |
| `/api/namedLists`       | ⚠️ Retourne vide | Service désactivé (juillet 2024) | **Utiliser VoiceCommandService** (déjà fait ✅) |
| `/api/todos`            | ⚠️ Retourne vide | Alternative non fonctionnelle    | **Utiliser VoiceCommandService** (déjà fait ✅) |
| `/api/household/lists`  | ⚠️ Retourne vide | Alternative non fonctionnelle    | **Utiliser VoiceCommandService** (déjà fait ✅) |
| `/api/namedLists/items` | ⚠️ Retourne vide | API dépréciée                    | **Utiliser VoiceCommandService** (déjà fait ✅) |

---

## 📚 Références

- **Documentation officielle** : Aucune (API non documentée)
- **Script Shell source** : `scripts/alexa_remote_control.sh`
- **Endpoint Analysis** : `docs/ANALYSE_ENDPOINTS_API.md`
- **Code Python** : `core/`, `services/`, `cli/commands/`

---

**Dernière mise à jour** : 14 octobre 2025  
**Auteur** : Analyse automatique du code
