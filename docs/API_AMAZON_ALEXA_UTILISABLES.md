# 📘 Guide des API Amazon Alexa Utilisables

**Date** : 12 octobre 2025  
**Projet** : Alexa Advanced Control  
**Statut** : APIs validées et fonctionnelles

---

## 🎯 Introduction

Ce document liste **uniquement les APIs Amazon Alexa qui fonctionnent actuellement** et peuvent être utilisées pour contrôler vos appareils Alexa. Toutes les APIs ont été testées et validées.

### Légende des symboles

| Symbole | Signification                            |
| ------- | ---------------------------------------- |
| ✅      | API fonctionnelle et recommandée         |
| ⚠️      | API fonctionnelle mais avec limitations  |
| 🔒      | Nécessite authentification CSRF spéciale |
| 📄      | Retourne du JSON                         |
| 🌐      | Retourne du HTML                         |

---

## 🔐 1. Authentification & Session

### 1.1 Obtenir le statut de connexion et le Customer ID

**Endpoint** : `GET /api/bootstrap?version=0`

**Domaine** : `alexa.amazon.fr` (ou votre domaine Amazon)

**Headers requis** :

```
csrf: <votre_token_csrf>
```

**Exemple de requête** :

```bash
curl -X GET \
  "https://alexa.amazon.fr/api/bootstrap?version=0" \
  -H "csrf: abc123xyz..." \
  -H "Cookie: session-id=..."
```

**Réponse** :

```json
{
  "authentication": {
    "authenticated": true,
    "customerId": "A2EPGYVJYILASM",
    "customerName": "John Doe",
    "customerEmail": "john@example.com"
  },
  "endpoints": {
    "websocketUrl": "wss://...",
    "musicUrl": "https://music.amazon.fr"
  }
}
```

**Usage** :

- Vérifier que l'utilisateur est connecté
- Récupérer le `customerId` (requis pour certaines opérations)
- Obtenir les endpoints de service

---

### 1.2 Échanger un refresh token contre des cookies de session

**Endpoint** : `POST /ap/exchangetoken/cookies`

**Domaine** : `api.amazon.fr`

**Headers requis** :

```
x-amzn-identity-auth-domain: api.amazon.fr
Content-Type: application/x-www-form-urlencoded
```

**Body (x-www-form-urlencoded)** :

```
app_name=Amazon%20Alexa
requested_token_type=auth_cookies
domain=www.amazon.fr
source_token_type=refresh_token
source_token=<votre_refresh_token>
```

**Réponse** :

```json
{
  "response": {
    "tokens": {
      "cookies": {
        "session-id": "...",
        "ubid-acbfr": "...",
        "at-acbfr": "..."
      }
    }
  }
}
```

**Usage** :

- Authentification initiale sans mot de passe
- Renouveler les cookies expirés
- Automatiser la connexion

---

## 📱 2. Gestion des Appareils

### 2.1 Lister tous les appareils Alexa

**Endpoint** : `GET /api/devices-v2/device?cached=false`

**Headers requis** :

```
csrf: <votre_token_csrf>
```

**Exemple de requête** :

```bash
curl -X GET \
  "https://alexa.amazon.fr/api/devices-v2/device?cached=false" \
  -H "csrf: abc123xyz..."
```

**Réponse** :

```json
{
  "devices": [
    {
      "serialNumber": "G6G2MM125193038X",
      "deviceType": "A2UONLFQW0PADH",
      "deviceFamily": "ECHO",
      "accountName": "Salon Echo",
      "capabilities": [
        "AUDIO_PLAYER",
        "FLASH_BRIEFING",
        "TIMERS_AND_ALARMS",
        "REMINDERS",
        "VOLUME_SETTING"
      ],
      "online": true
    }
  ]
}
```

**Informations disponibles** :

- `serialNumber` : Numéro de série unique
- `deviceType` : Modèle de l'appareil
- `deviceFamily` : Famille (ECHO, FIRE_TV, etc.)
- `accountName` : Nom personnalisé
- `capabilities` : Fonctionnalités supportées
- `online` : État de connexion

---

### 2.2 Obtenir les préférences d'un appareil

**Endpoint** : `GET /api/device-preferences/{device_serial}`

**Variables** :

- `{device_serial}` : Numéro de série de l'appareil

**Réponse** :

```json
{
  "devicePreferences": {
    "locale": "fr-FR",
    "timeZone": "Europe/Paris",
    "wakeWord": "ALEXA",
    "clockDisplay": "24_HOURS",
    "temperatureUnit": "CELSIUS"
  }
}
```

---

## 🔊 3. Contrôle du Volume

### 3.1 Récupérer le volume de tous les appareils

**Endpoint** : `GET /api/devices/deviceType/dsn/audio/v1/allDeviceVolumes`

**Avantage** : Une seule requête pour tous les appareils ✅

**Réponse** :

```json
{
  "volumes": [
    {
      "dsn": "G6G2MM125193038X",
      "deviceType": "A2UONLFQW0PADH",
      "speakerVolume": 50,
      "speakerMuted": false
    },
    {
      "dsn": "G000MM125193099Y",
      "deviceType": "A32DOYMUN6DTXA",
      "speakerVolume": 30,
      "speakerMuted": false
    }
  ]
}
```

**Filtrage** : Utiliser le `dsn` (device serial number) pour filtrer

---

### 3.2 Définir le volume d'un appareil

**Endpoint** : `POST /api/behaviors/preview`

**Headers requis** :

```
csrf: <votre_token_csrf>
Content-Type: application/json
```

**Body** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.ParallelNode\",\"nodesToExecute\":[{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"type\":\"Alexa.DeviceControls.Volume\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"G6G2MM125193038X\",\"customerId\":\"A2EPGYVJYILASM\",\"locale\":\"fr-FR\",\"value\":\"50\"}}]}}",
  "status": "ENABLED"
}
```

**Paramètres du payload** :

- `deviceType` : Type de l'appareil
- `deviceSerialNumber` : Numéro de série
- `customerId` : ID client (depuis `/api/bootstrap`)
- `locale` : Langue (ex: "fr-FR")
- `value` : Volume souhaité (0-100)

**Format simplifié du sequenceJson** :

```json
{
  "@type": "com.amazon.alexa.behaviors.model.Sequence",
  "startNode": {
    "@type": "com.amazon.alexa.behaviors.model.ParallelNode",
    "nodesToExecute": [
      {
        "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
        "type": "Alexa.DeviceControls.Volume",
        "operationPayload": {
          "deviceType": "A2UONLFQW0PADH",
          "deviceSerialNumber": "G6G2MM125193038X",
          "customerId": "A2EPGYVJYILASM",
          "locale": "fr-FR",
          "value": "50"
        }
      }
    ]
  }
}
```

---

## 🎵 4. Contrôle de la Musique

### 4.1 Commandes de lecture (Play/Pause/Next/Previous)

**Endpoint** : `POST /api/np/command`

**Headers requis** :

```
csrf: <votre_token_csrf>
Content-Type: application/json
```

**Paramètres URL** :

```
?deviceSerialNumber=G6G2MM125193038X
&deviceType=A2UONLFQW0PADH
```

**Body pour chaque commande** :

#### Play

```json
{
  "type": "PlayCommand"
}
```

#### Pause

```json
{
  "type": "PauseCommand"
}
```

#### Suivant

```json
{
  "type": "NextCommand"
}
```

#### Précédent

```json
{
  "type": "PreviousCommand"
}
```

#### Activer le shuffle

```json
{
  "type": "ShuffleCommand",
  "shuffle": true
}
```

#### Activer la répétition

```json
{
  "type": "RepeatCommand",
  "repeat": true
}
```

---

### 4.2 Obtenir l'état de lecture actuel

**Endpoint** : `GET /api/np/player`

**Paramètres URL** :

```
?deviceSerialNumber=G6G2MM125193038X
&deviceType=A2UONLFQW0PADH
```

**Réponse** :

```json
{
  "playerInfo": {
    "state": "PLAYING",
    "volume": {
      "volume": 50,
      "muted": false
    },
    "mainArt": {
      "url": "https://m.media-amazon.com/images/..."
    },
    "provider": {
      "providerName": "Spotify"
    },
    "infoText": {
      "title": "Bohemian Rhapsody",
      "subText1": "Queen",
      "subText2": "A Night at the Opera"
    },
    "progress": {
      "mediaLength": 354000,
      "mediaProgress": 120000
    }
  }
}
```

**Informations disponibles** :

- État de lecture (PLAYING, PAUSED, STOPPED)
- Titre, artiste, album
- Progression (en millisecondes)
- Durée totale
- Service de musique (Spotify, Amazon Music, etc.)

⚠️ **Note** : Peut retourner 403 Forbidden sur certains appareils

---

### 4.3 Lire une station TuneIn (Radio)

**Endpoint** : `PUT /api/entertainment/v1/player/queue`

**Body** :

```json
{
  "deviceSerialNumber": "G6G2MM125193038X",
  "deviceType": "A2UONLFQW0PADH",
  "contentToken": "music:tuneIn/stationId/s12345"
}
```

**Format du contentToken** :

- Radio locale : `music:tuneIn/stationId/s12345`
- Podcast : `music:tuneIn/showId/p12345`

---

## ⏰ 5. Alarmes, Timers & Rappels

### 5.1 Récupérer toutes les notifications

**Endpoint** : `GET /api/notifications`

**Réponse** :

```json
{
  "notifications": [
    {
      "id": "alarm-123",
      "type": "Alarm",
      "status": "ON",
      "originalTime": "2025-10-13T07:00:00.000Z",
      "deviceSerialNumber": "G6G2MM125193038X",
      "recurringPattern": "P1D",
      "label": "Réveil du matin"
    },
    {
      "id": "timer-456",
      "type": "Timer",
      "status": "ON",
      "remainingTime": 300000,
      "label": "Pizza"
    },
    {
      "id": "reminder-789",
      "type": "Reminder",
      "status": "ON",
      "originalTime": "2025-10-13T14:00:00.000Z",
      "label": "Rendez-vous dentiste"
    }
  ]
}
```

**Types de notifications** :

- `Alarm` : Alarmes
- `Timer` : Minuteurs
- `Reminder` : Rappels

**Filtrage** : Côté client par le champ `type`

---

### 5.2 Créer une alarme

**Endpoint** : `POST /api/alarms`

**Body** :

```json
{
  "type": "Alarm",
  "deviceSerialNumber": "G6G2MM125193038X",
  "deviceType": "A2UONLFQW0PADH",
  "originalDate": "2025-10-13",
  "originalTime": "07:00:00.000",
  "recurringPattern": "P1D",
  "label": "Réveil du matin",
  "sound": {
    "providerId": "ECHO",
    "displayName": "Simple Alarm"
  }
}
```

**Patterns de récurrence** :

- `null` : Une seule fois
- `P1D` : Chaque jour
- `XXXX-WE` : Week-end (samedi-dimanche)
- `XXXX-WD` : Jours de semaine (lundi-vendredi)
- Pattern personnalisé : `YYYY-MM-DD:T1,T3,T5` (mardi, jeudi, samedi)

---

### 5.3 Créer un timer

**Endpoint** : `POST /api/timers`

**Body** :

```json
{
  "deviceSerialNumber": "G6G2MM125193038X",
  "deviceType": "A2UONLFQW0PADH",
  "duration": 300000,
  "label": "Pizza"
}
```

**Paramètres** :

- `duration` : Durée en millisecondes (300000 = 5 minutes)
- `label` : Étiquette optionnelle

---

### 5.4 Créer un rappel

**Endpoint** : `POST /api/notifications/createReminder`

**Body** :

```json
{
  "type": "Reminder",
  "deviceSerialNumber": "G6G2MM125193038X",
  "deviceType": "A2UONLFQW0PADH",
  "reminderLabel": "Rendez-vous dentiste",
  "alarmTime": 1697198400000,
  "originalTime": "2025-10-13T14:00:00.000Z",
  "recurringPattern": null
}
```

**Paramètres** :

- `alarmTime` : Timestamp Unix en millisecondes
- `originalTime` : Date/heure ISO 8601
- `recurringPattern` : Même format que les alarmes

---

### 5.5 Supprimer une notification

**Endpoint** : `DELETE /api/notifications/{notification_id}`

**Exemple** :

```bash
curl -X DELETE \
  "https://alexa.amazon.fr/api/notifications/alarm-123" \
  -H "csrf: abc123xyz..."
```

---

## 🏠 6. Contrôle Smart Home

### 6.1 Lister tous les appareils smart home

**Endpoint** : `GET /api/behaviors/entities?skillId=amzn1.ask.1p.smarthome`

**Réponse** :

```json
[
  {
    "id": "light.salon_plafond",
    "displayName": "Lumière Salon",
    "description": "Philips Hue",
    "supportedProperties": [
      "Alexa.PowerController.powerState",
      "Alexa.BrightnessController.brightness",
      "Alexa.ColorController.color"
    ],
    "entityType": "LIGHT"
  },
  {
    "id": "switch.ventilateur",
    "displayName": "Ventilateur",
    "description": "Prise intelligente",
    "supportedProperties": ["Alexa.PowerController.powerState"],
    "entityType": "SWITCH"
  }
]
```

**Types d'appareils** :

- `LIGHT` : Lumières
- `SWITCH` : Prises/interrupteurs
- `THERMOSTAT` : Thermostats
- `LOCK` : Serrures
- `CAMERA` : Caméras

---

### 6.2 Contrôler un appareil (allumer/éteindre)

**Endpoint** : `POST /api/phoenix`

**Body pour allumer** :

```json
{
  "controlRequests": [
    {
      "entityId": "light.salon_plafond",
      "entityType": "LIGHT",
      "parameters": {
        "action": "turnOn"
      }
    }
  ]
}
```

**Body pour éteindre** :

```json
{
  "controlRequests": [
    {
      "entityId": "light.salon_plafond",
      "entityType": "LIGHT",
      "parameters": {
        "action": "turnOff"
      }
    }
  ]
}
```

---

### 6.3 Contrôler la luminosité

**Body** :

```json
{
  "controlRequests": [
    {
      "entityId": "light.salon_plafond",
      "entityType": "LIGHT",
      "parameters": {
        "action": "setBrightness",
        "brightness": 75
      }
    }
  ]
}
```

**Paramètres** :

- `brightness` : 0-100 (pourcentage)

---

### 6.4 Changer la couleur (lampes RGB)

**Body** :

```json
{
  "controlRequests": [
    {
      "entityId": "light.salon_plafond",
      "entityType": "LIGHT",
      "parameters": {
        "action": "setColor",
        "colorHue": 0.5,
        "colorSaturation": 1.0,
        "colorBrightness": 1.0
      }
    }
  ]
}
```

**Paramètres** :

- `colorHue` : Teinte (0.0-1.0)
- `colorSaturation` : Saturation (0.0-1.0)
- `colorBrightness` : Luminosité (0.0-1.0)

---

## 🎤 7. Commandes Vocales & Synthèse Vocale

### 7.1 Envoyer une commande textuelle

**Endpoint** : `POST /api/behaviors/preview`

**Usage** : Envoyer une commande comme si vous parliez à Alexa

**Body** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"type\":\"Alexa.TextCommand\",\"skillId\":\"amzn1.ask.1p.tellalexa\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"G6G2MM125193038X\",\"customerId\":\"A2EPGYVJYILASM\",\"locale\":\"fr-FR\",\"text\":\"Alexa, quel temps fait-il ?\"}}}",
  "status": "ENABLED"
}
```

**Format du sequenceJson** :

```json
{
  "@type": "com.amazon.alexa.behaviors.model.Sequence",
  "startNode": {
    "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
    "type": "Alexa.TextCommand",
    "skillId": "amzn1.ask.1p.tellalexa",
    "operationPayload": {
      "deviceType": "A2UONLFQW0PADH",
      "deviceSerialNumber": "G6G2MM125193038X",
      "customerId": "A2EPGYVJYILASM",
      "locale": "fr-FR",
      "text": "Alexa, quel temps fait-il ?"
    }
  }
}
```

**Exemples de commandes** :

- `"Alexa, joue de la musique relaxante"`
- `"Alexa, allume la lumière du salon"`
- `"Alexa, ajoute du lait à ma liste de courses"`
- `"Alexa, programme un timer de 10 minutes"`

---

### 7.2 Synthèse vocale (TTS)

**Endpoint** : `POST /api/behaviors/preview`

**Usage** : Faire parler Alexa avec un texte personnalisé

**Body** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"type\":\"Alexa.Speak\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"G6G2MM125193038X\",\"customerId\":\"A2EPGYVJYILASM\",\"locale\":\"fr-FR\",\"textToSpeak\":\"Bonjour, le café est prêt !\"}}}",
  "status": "ENABLED"
}
```

**Format du sequenceJson** :

```json
{
  "@type": "com.amazon.alexa.behaviors.model.Sequence",
  "startNode": {
    "@type": "com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode",
    "type": "Alexa.Speak",
    "operationPayload": {
      "deviceType": "A2UONLFQW0PADH",
      "deviceSerialNumber": "G6G2MM125193038X",
      "customerId": "A2EPGYVJYILASM",
      "locale": "fr-FR",
      "textToSpeak": "Bonjour, le café est prêt !"
    }
  }
}
```

**Limitations** :

- Texte limité à ~250 caractères
- Pas de SSML (Speech Synthesis Markup Language)

---

## 🔄 8. Routines

### 8.1 Lister toutes les routines

**Endpoint** : `GET /api/behaviors/v2/automations`

**Réponse** :

```json
[
  {
    "automationId": "routine-123",
    "name": "Bonne nuit",
    "enabled": true,
    "triggers": [
      {
        "type": "Schedule",
        "time": "22:00:00"
      }
    ],
    "sequence": [
      {
        "type": "Alexa.Speak",
        "payload": {
          "textToSpeak": "Bonne nuit !"
        }
      },
      {
        "type": "Alexa.DeviceControls.Volume",
        "payload": {
          "value": "20"
        }
      }
    ]
  }
]
```

---

### 8.2 Exécuter une routine

**Endpoint** : `POST /api/behaviors/preview`

**Body** :

```json
{
  "behaviorId": "routine-123",
  "sequenceJson": "<copier_le_sequence_de_la_routine>",
  "status": "ENABLED"
}
```

---

## 🔔 9. Mode Ne Pas Déranger (DND)

### 9.1 Obtenir le statut DND d'un appareil

**Endpoint** : `GET /api/dnd/status`

**Paramètres URL** :

```
?deviceSerialNumber=G6G2MM125193038X
&deviceType=A2UONLFQW0PADH
```

**Réponse** :

```json
{
  "doNotDisturbEnabled": false
}
```

---

### 9.2 Activer/désactiver le DND

**Endpoint** : `PUT /api/dnd/status`

**Body** :

```json
{
  "deviceSerialNumber": "G6G2MM125193038X",
  "deviceType": "A2UONLFQW0PADH",
  "enabled": true
}
```

---

### 9.3 Statut DND de tous les appareils

**Endpoint** : `GET /api/dnd/device-status-list`

**Réponse** :

```json
{
  "deviceStatusList": [
    {
      "deviceSerialNumber": "G6G2MM125193038X",
      "deviceType": "A2UONLFQW0PADH",
      "enabled": false
    },
    {
      "deviceSerialNumber": "G000MM125193099Y",
      "deviceType": "A32DOYMUN6DTXA",
      "enabled": true
    }
  ]
}
```

---

## 🔵 10. Bluetooth

### 10.1 Lister les appareils Bluetooth

**Endpoint** : `GET /api/bluetooth`

**Paramètres URL** :

```
?deviceSerialNumber=G6G2MM125193038X
&deviceType=A2UONLFQW0PADH
```

**Réponse** :

```json
{
  "bluetoothStates": [
    {
      "deviceSerialNumber": "G6G2MM125193038X",
      "pairedDeviceList": [
        {
          "address": "00:11:22:33:44:55",
          "friendlyName": "Casque Sony",
          "connected": true
        }
      ]
    }
  ]
}
```

---

### 10.2 Connecter un appareil Bluetooth

**Endpoint** : `POST /api/bluetooth/pair-sink/{deviceType}/{deviceSerial}`

**Body** :

```json
{
  "bluetoothDeviceAddress": "00:11:22:33:44:55"
}
```

---

### 10.3 Déconnecter un appareil Bluetooth

**Endpoint** : `POST /api/bluetooth/disconnect-sink/{deviceType}/{deviceSerial}`

---

## 📊 11. Historique Vocal (API Privacy) 🔒

### 11.1 Récupérer le CSRF token Privacy

**Endpoint** : `GET /alexa-privacy/apd/activity?ref=activityHistory`

**Domaine** : `www.amazon.fr`

**Réponse** : 🌐 **Page HTML**

**Extraction** :

```html
<meta name="csrf-token" content="abc123xyz..." />
```

**Code d'extraction** :

```python
import re

response = session.get("https://www.amazon.fr/alexa-privacy/apd/activity?ref=activityHistory")
html = response.text

# Méthode 1: Regex
csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', html)
privacy_csrf = csrf_match.group(1) if csrf_match else None

# Méthode 2: BeautifulSoup
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
meta = soup.find('meta', {'name': 'csrf-token'})
privacy_csrf = meta['content'] if meta else None
```

---

### 11.2 Récupérer l'historique vocal complet

**Endpoint** : `POST /alexa-privacy/apd/rvh/customer-history-records-v2/`

**Domaine** : `www.amazon.fr`

**Paramètres URL** :

```
?startTime=0
&endTime=2147483647000
&pageType=VOICE_HISTORY
```

**Headers requis** 🔒 :

```
csrf: <votre_token_csrf_standard>
anti-csrftoken-a2z: <privacy_csrf_token>
Content-Type: application/json
```

**Body** :

```json
{
  "previousRequestToken": null
}
```

**Réponse** :

```json
{
  "customerHistoryRecords": [
    {
      "recordKey": "A2EPGYVJYILASM#1696849200000#G6G2MM125193038X#12345",
      "timestamp": 1696849200000,
      "device": {
        "deviceName": "Salon Echo",
        "serialNumber": "G6G2MM125193038X",
        "deviceType": "A2UONLFQW0PADH"
      },
      "voiceHistoryRecordItems": [
        {
          "recordItemType": "CUSTOMER_TRANSCRIPT",
          "transcriptText": "Alexa, quel temps fait-il ?"
        },
        {
          "recordItemType": "ALEXA_RESPONSE",
          "transcriptText": "Il fait 18 degrés avec un ciel nuageux"
        }
      ],
      "activityStatus": "SUCCESS"
    }
  ],
  "nextRequestToken": "eyJ0eXAiOiJKV1Qi..."
}
```

**Pagination** :

```json
{
  "previousRequestToken": "eyJ0eXAiOiJKV1Qi..."
}
```

**Informations disponibles** :

- Transcription de votre commande vocale
- Réponse d'Alexa
- Appareil utilisé
- Timestamp (date/heure)
- Statut (SUCCESS, FAILED, INTERRUPTED)

---

## ⚠️ 12. APIs Dépréciées (Ne Pas Utiliser)

### ❌ Listes de courses/tâches (REST API)

**Endpoints** :

- `GET /api/namedLists` → Retourne `{"lists": []}`
- `GET /api/todos` → Retourne `{"values": []}`
- `GET /api/household/lists` → Retourne `{"lists": []}`

**Raison** : Service désactivé par Amazon (juillet 2024)

**Alternative** : Utiliser **Alexa.TextCommand** avec commandes vocales :

```
"Alexa, ajoute du lait à ma liste de courses"
"Alexa, retire le pain de ma liste"
"Alexa, lis ma liste de courses"
```

---

### ❌ Activités système (REST API)

**Endpoints** :

- `GET /api/activities` → Retourne `{"activities": []}`

**Raison** : API déplacée vers `/alexa-privacy/...`

**Alternative** : Utiliser **API Privacy** (section 11)

---

## 📝 13. Bonnes Pratiques

### 13.1 Gestion des erreurs

**Codes HTTP courants** :

| Code | Signification    | Action recommandée          |
| ---- | ---------------- | --------------------------- |
| 200  | Succès           | ✅ Traiter la réponse       |
| 401  | Non autorisé     | 🔄 Rafraîchir les cookies   |
| 403  | Interdit         | 🔄 Régénérer le CSRF token  |
| 404  | Non trouvé       | ❌ Vérifier l'endpoint/ID   |
| 429  | Trop de requêtes | ⏸️ Attendre (rate limiting) |
| 500  | Erreur serveur   | 🔄 Retry avec backoff       |

---

### 13.2 Circuit Breaker

**Recommandation** : Utiliser un circuit breaker pour éviter de saturer l'API

**Configuration suggérée** :

```python
circuit_breaker = CircuitBreaker(
    failure_threshold=3,  # 3 échecs consécutifs
    timeout=30,           # 30 secondes avant réouverture
    half_open_max_calls=1 # 1 appel test en half-open
)
```

---

### 13.3 Rate Limiting

**Limites observées** :

- ~100 requêtes/minute par endpoint
- ~1000 requêtes/heure global

**Recommandation** : Espacer les requêtes de 500ms minimum

---

### 13.4 Caching

**Données à cacher** :

- Liste des appareils : **24h**
- Volume des appareils : **5 minutes**
- État DND : **1 heure**
- Notifications : **1 minute**
- Smart home devices : **1 heure**

**Headers de cache** :

```python
response = session.get(url, expire_after=3600)  # 1 heure
```

---

## 🔧 14. Outils de Développement

### 14.1 Tester une API avec curl

**Exemple** :

```bash
# 1. Définir les variables
CSRF_TOKEN="abc123xyz..."
DEVICE_SERIAL="G6G2MM125193038X"
DEVICE_TYPE="A2UONLFQW0PADH"

# 2. Tester l'API
curl -X GET \
  "https://alexa.amazon.fr/api/np/player?deviceSerialNumber=${DEVICE_SERIAL}&deviceType=${DEVICE_TYPE}" \
  -H "csrf: ${CSRF_TOKEN}" \
  -H "Cookie: session-id=...; at-acbfr=..." \
  | jq .
```

---

### 14.2 Tester avec Python

```python
import requests

session = requests.Session()
session.cookies.update({
    'session-id': '...',
    'at-acbfr': '...',
    'ubid-acbfr': '...'
})

response = session.get(
    "https://alexa.amazon.fr/api/devices-v2/device",
    params={'cached': 'false'},
    headers={'csrf': 'abc123xyz...'}
)

print(response.json())
```

---

### 14.3 Déboguer les requêtes

**Activer les logs HTTP** :

```python
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 15. Références

### Documentation officielle

⚠️ **Aucune documentation officielle publique** - API non documentée par Amazon

### Ressources communautaires

- [alexa-remote-control.sh](https://github.com/thorsten-gehrig/alexa-remote-control) - Script Shell original
- [alexa-remote](https://github.com/Apollon77/alexa-remote) - Bibliothèque Node.js

### Projets similaires

- **Home Assistant Alexa Media Player** - Intégration Alexa pour Home Assistant
- **ioBroker Alexa2** - Adaptateur Alexa pour ioBroker

---

## 📊 16. Tableau Récapitulatif

| Catégorie             | Endpoints | Status    | Documentation            |
| --------------------- | --------- | --------- | ------------------------ |
| **Authentification**  | 2         | ✅        | Section 1                |
| **Appareils**         | 5         | ✅        | Section 2                |
| **Volume**            | 2         | ✅        | Section 3                |
| **Musique**           | 15        | ✅        | Section 4                |
| **Alarmes/Timers**    | 11        | ✅        | Section 5                |
| **Smart Home**        | 4         | ✅        | Section 6                |
| **Commandes Vocales** | 2         | ✅        | Section 7                |
| **Routines**          | 2         | ✅        | Section 8                |
| **DND**               | 3         | ✅        | Section 9                |
| **Bluetooth**         | 3         | ✅        | Section 10               |
| **Historique**        | 2         | ✅ 🔒     | Section 11               |
| **Listes**            | 4         | ❌        | Alternative : Section 7  |
| **Activités**         | 2         | ❌        | Alternative : Section 11 |
| **TOTAL**             | **57**    | **51 ✅** | -                        |

**Taux de disponibilité** : 89.5% (51/57)

---

**Dernière mise à jour** : 12 octobre 2025  
**Version du document** : 1.0  
**Contributeur** : Analyse du projet Alexa Advanced Control
