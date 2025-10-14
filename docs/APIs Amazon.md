# 📘 Guide Complet des API Amazon Alexa (Publiques et Privées)

**Date** : 12 octobre 2025  
**Projet** : Alexa Advanced Control  
**Statut** : Document de synthèse  
**Dernière mise à jour** : Implémentation flag `--real` pour listes, clarification APIs dépréciées

---

## 🎯 Introduction : Deux Mondes d'API

Pour interagir avec l'écosystème Amazon Alexa, il existe deux types d'API fondamentalement différents :

1.  **Les API Publiques (officielles)** : Fournies et documentées par Amazon via l'**Alexa Skills Kit (ASK)**. Elles permettent aux développeurs de **créer de nouvelles fonctionnalités (des _skills_)** pour Alexa.

    - **Principe** : Votre service externe répond aux requêtes d'Alexa.
    - **Exemple** : Vous créez une skill "Météo Personnalisée". Quand un utilisateur dit "Alexa, demande à Météo Personnalisée le temps qu'il fera demain", Alexa interroge _votre_ API.

2.  **Les API Privées (non-officielles)** : Utilisées par l'application mobile et le site web d'Alexa. Elles ne sont **pas documentées** et permettent de **contrôler directement vos propres appareils Echo**.
    - **Principe** : Votre code se fait passer pour l'application officielle et envoie des commandes aux serveurs d'Amazon pour piloter vos appareils.
    - **Exemple** : Votre script envoie une requête à une API privée pour dire à votre Echo de salon de jouer une chanson ou de régler son volume.

Ce document présente ces deux types d'API en détail.

---

## PARTIE 1 : 🔧 API Publiques - Pour les Créateurs de Skills (Alexa Skills Kit)

Cette section liste les API officielles pour développer des skills Alexa.

### 1. Alexa Skills Kit (ASK) REST API

- **Fonction** : Gérer le cycle de vie des skills Alexa (création, mise à jour, suppression, publication).
- **Méthodes** : RESTful (GET, POST, PUT, DELETE)
- **Authentification** : OAuth 2.0
- **Cas d’usage** : Automatiser la publication d'une skill, mettre à jour ses métadonnées, gérer les différentes versions.

### 2. Smart Home API

- **Fonction** : Permettre à une skill de contrôler des appareils domotiques (lumières, thermostats, etc.). C'est le standard pour intégrer des objets connectés à Alexa.
- **Méthodes** : Directives JSON envoyées à votre skill.
- **Cas d’usage** : Créer une skill pour une nouvelle marque de lampes connectées, permettant aux utilisateurs de dire "Alexa, allume la lumière du salon".

### 3. Alexa Presentation Language (APL)

- **Fonction** : Créer des expériences visuelles riches pour les appareils avec écran (Echo Show).
- **Cas d’usage** : Afficher des listes, des images, des vidéos, et créer des interfaces interactives en réponse à une commande vocale.

### 4. API de Confidentialité et Consentement

- **Alexa Customer Profile API** : Accéder aux données de l'utilisateur (nom, email, numéro de téléphone) après avoir obtenu son consentement explicite.
- **Alexa Settings API** : Lire les paramètres de l'utilisateur (langue, fuseau horaire, unité de mesure) pour adapter les réponses.
- **Device Address API** : Obtenir l'adresse physique de l'appareil (avec consentement) pour des services géolocalisés (livraison, météo locale précise).

### 5. API de Communication et Notifications

- **Alexa Notifications API** : Envoyer des notifications (discrètes ou avec un son) vers les appareils Echo d'un utilisateur.
- **Alexa Messaging API** : Permettre à une skill d'envoyer des messages vocaux entre utilisateurs.

### 6. Amazon API Gateway

- **Fonction** : Bien que ce soit un service AWS, il est essentiel. Il sert de point d'entrée (endpoint) sécurisé pour votre skill, recevant les requêtes d'Alexa et les transmettant à votre logique (par exemple, une fonction AWS Lambda).

---

## PARTIE 2 : 🚀 API Privées - Pour le Contrôle Direct des Appareils

Cette section détaille les API non-documentées, utilisées pour piloter directement vos appareils. **Attention : ces API peuvent changer sans préavis.**

### Légende des symboles

| Symbole | Signification                                  |
| :------ | :--------------------------------------------- |
| ✅      | API fonctionnelle et recommandée               |
| ⚠️      | API fonctionnelle mais avec limitations        |
| 🔒      | Nécessite une authentification spéciale (CSRF) |
| 📄      | Retourne du JSON                               |
| 🌐      | Retourne du HTML                               |

### 1. Authentification & Session

- **Obtenir le statut de connexion et le Customer ID** (`GET /api/bootstrap`) ✅📄 : Vérifie si la session est active et récupère des informations cruciales comme le `customerId`.
- **Échanger un refresh token** (`POST /ap/exchangetoken/cookies`) ✅📄 : Permet de renouveler les cookies de session sans avoir à saisir de nouveau le mot de passe.

### 2. Gestion des Appareils

- **Lister tous les appareils Alexa** (`GET /api/devices-v2/device`) ✅📄 : Récupère une liste complète de vos appareils avec leurs détails (numéro de série, type, nom, capacités, état en ligne).
- **Obtenir les préférences d'un appareil** (`GET /api/device-preferences/{device_serial}`) ✅📄 : Lit les paramètres spécifiques d'un appareil (langue, fuseau horaire, mot de réveil).

### 3. Contrôle du Volume

- **Récupérer le volume de tous les appareils** (`GET /api/devices/deviceType/dsn/audio/v1/allDeviceVolumes`) ✅📄 : Une seule requête pour connaître le volume de tous vos Echos.
- **Définir le volume d'un appareil** (`POST /api/behaviors/preview` avec payload `Alexa.DeviceControls.Volume`) ✅📄 : Modifie le volume (0-100) d'un appareil spécifique.

### 4. Contrôle de la Musique

- **Commandes de lecture** (`POST /api/np/command`) ✅📄 : Envoyer des commandes simples comme `Play`, `Pause`, `Next`, `Previous`, `Shuffle`.
- **Obtenir l'état de lecture actuel** (`GET /api/np/player`) ✅📄 : Récupère ce qui est en cours de lecture (titre, artiste, album, progression, service de musique).
- **Lire une station TuneIn (Radio)** (`PUT /api/entertainment/v1/player/queue`) ✅📄 : Lance la lecture d'une radio par son ID.

### 5. Alarmes, Timers & Rappels

- **Récupérer toutes les notifications** (`GET /api/notifications`) ✅📄 : Liste toutes les alarmes, minuteurs et rappels actifs ou programmés sur tous vos appareils.
- **Créer une alarme** (`POST /api/alarms`) ✅📄 : Programme une nouvelle alarme (ponctuelle ou récurrente).
- **Créer un timer** (`POST /api/timers`) ✅📄 : Lance un nouveau minuteur.
- **Créer un rappel** (`POST /api/notifications/createReminder`) ✅📄 : Crée un nouveau rappel.
- **Supprimer une notification** (`DELETE /api/notifications/{id}`) ✅📄 : Supprime une alarme, un minuteur ou un rappel par son ID.

### 6. Contrôle Smart Home

- **Lister tous les appareils smart home** (`GET /api/behaviors/entities?skillId=amzn1.ask.1p.smarthome`) ✅📄 : Récupère tous vos appareils domotiques (lumières, prises, thermostats...).
- **Contrôler un appareil** (`POST /api/phoenix`) ✅📄 : Permet d'allumer/éteindre, de changer la luminosité ou la couleur d'un appareil domotique.

### 7. Commandes Vocales & Synthèse Vocale (TTS)

- **Envoyer une commande textuelle** (`POST /api/behaviors/preview` avec payload `Alexa.TextCommand`) ✅📄 : Simule une commande vocale. Le texte envoyé est interprété par Alexa comme si vous l'aviez prononcé.
  - **Exemples** : "Alexa, quel temps fait-il ?", "Alexa, ajoute du lait à ma liste de courses".
- **Synthèse vocale (TTS)** (`POST /api/behaviors/preview` avec payload `Alexa.Speak`) ✅📄 : Fait parler un appareil Echo avec un texte personnalisé.
  - **Exemple** : "Bonjour, le café est prêt !".

### 8. Routines

- **Lister toutes les routines** (`GET /api/behaviors/v2/automations`) ✅📄 : Récupère la liste de toutes les routines configurées dans votre compte.
- **Exécuter une routine** (`POST /api/behaviors/preview` avec `behaviorId`) ✅📄 : Déclenche l'exécution d'une routine existante.

### 9. Mode Ne Pas Déranger (DND)

- **Obtenir/modifier le statut DND** (`GET /api/dnd/status`, `PUT /api/dnd/status`) ✅📄 : Active ou désactive le mode "Ne pas déranger" pour un appareil.
- **Statut DND de tous les appareils** (`GET /api/dnd/device-status-list`) ✅📄 : Récupère l'état DND de tous les appareils en une seule fois.

### 10. Bluetooth

- **Lister et contrôler les appareils Bluetooth** (`GET /api/bluetooth`, `POST /api/bluetooth/...`) ✅📄 : Affiche les appareils jumelés, et permet de connecter ou déconnecter une enceinte ou un casque.

### 11. Historique Vocal (API Privacy) 🔒

- **Récupérer le CSRF token Privacy** (`GET /alexa-privacy/apd/activity`) ✅🌐 : Étape préliminaire nécessaire pour obtenir un token CSRF spécifique à l'API de confidentialité.
- **Récupérer l'historique vocal** (`POST /alexa-privacy/apd/rvh/customer-history-records-v2/`) ✅📄 : Accède à l'historique complet des interactions vocales (ce que vous avez dit et ce qu'Alexa a répondu). Nécessite le token CSRF spécial.

### 12. Gestion des Listes (Courses, Tâches) ⚠️

**⚠️ ATTENTION : APIs REST désactivées depuis juillet 2024**

- **APIs REST dépréciées** :

  - `/api/namedLists` ❌ (retourne 503/404)
  - `/api/todos` ❌ (retourne 503/404)
  - `/api/household/lists` ❌ (retourne 503/404)
  - `/api/namedLists/items` ❌ (retourne 503/404)

- **API Privacy pour listes** : ❌ **NON DISPONIBLE** (contrairement aux activités vocales)

- **Alternatives fonctionnelles** :

  - **Commandes textuelles** (`POST /api/behaviors/preview` avec `Alexa.TextCommand`) ✅📄 : Simule des commandes vocales pour gérer les listes
    - "ajoute [item] à ma liste de courses"
    - "retire [item] de ma liste de courses"
    - "marque [item] comme fait dans ma liste de tâches"
    - "vide ma liste de courses"
  - **Cache local simulé** : Système de persistance local pour les données mockées

- **Implémentation recommandée** (ce projet) :
  ```python
  # Système hybride : Mock + Voice Commands
  class ListsManager:
      def add_item(self, list_type, text):
          if real_mode:
              # Commande vocale réelle
              return voice_service.speak(f"ajoute {text} à ma liste de {list_type}")
          else:
              # Données simulées locales
              return mock_cache.add_item(list_type, text)
  ```

### 13. API Dépréciées (À ne plus utiliser) ❌

- **Activités système** (`/api/activities`) : Cette API est maintenant vide et a été remplacée par l'API Privacy (voir section 11).

---

## PARTIE 3 : 📝 Bonnes Pratiques et Outils

Ces pratiques s'appliquent surtout à l'utilisation des API privées.

### 1. Gestion des Erreurs

| Code | Signification    | Action recommandée                               |
| :--- | :--------------- | :----------------------------------------------- |
| 200  | Succès           | ✅ Traiter la réponse                            |
| 401  | Non autorisé     | 🔄 Rafraîchir les cookies de session             |
| 403  | Interdit         | 🔄 Régénérer le token CSRF                       |
| 429  | Trop de requêtes | ⏸️ Attendre (implémenter un backoff exponentiel) |
| 5xx  | Erreur serveur   | 🔄 Réessayer plus tard                           |

### 2. Rate Limiting (Limitation de débit)

Amazon n'officialise pas les limites, mais les observations communautaires suggèrent :

- ~100 requêtes/minute par endpoint.
- ~1000 requêtes/heure au total.
- **Recommandation** : Espacer les requêtes d'au moins 500ms et utiliser un **Circuit Breaker** pour éviter de surcharger les serveurs en cas d'erreurs répétées.

### 3. Caching

Pour minimiser les appels API et améliorer les performances, il est crucial de mettre en cache les données qui changent peu :

- **Liste des appareils** : Mettre en cache pendant 24h.
- **Liste des routines et appareils smart home** : Mettre en cache pendant 1h.
- **État des appareils (volume, DND)** : Mettre en cache pendant 5 minutes.
- **Notifications (alarmes, timers)** : Mettre en cache pendant 1 minute.

### 4. Outils de Développement

- **`curl`** : Idéal pour tester rapidement un endpoint avec les bons headers et cookies.
- **Bibliothèques Python/Node.js** : Des projets comme `alexa-remote-control` (shell), `alexa-remote` (Node.js) ou ce projet `alexa_advanced_control` (Python) encapsulent la complexité de l'authentification et des appels.

---

## PARTIE 4 : 🔍 Détails Techniques - Implémentation dans ce Projet

Cette section détaille précisément comment les APIs Amazon sont utilisées dans ce projet `alexa_advanced_control`, avec les payloads JSON exacts, headers, et exemples d'implémentation.

### 1. Architecture Générale

Le projet utilise une approche hybride :

- **Authentification** : Cookies persistants + CSRF tokens
- **Circuit Breaker** : Protection contre les pannes API
- **Cache multi-niveau** : Mémoire → Fichier JSON → API → Données simulées
- **State Machine** : Gestion thread-safe des états de connexion

### 2. Authentification Détaillée

#### Cookies de Session

```json
{
  "session-id": "XXX-XXXX-XXXX-XXXX-XXXXXXXX",
  "session-id-time": "1234567890123",
  "ubid-main": "XXX-XXXX-XXXX-XXXX-XXXXXXXX",
  "at-main": "Atza|XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "sess-at-main": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

#### Headers Standards pour Toutes les Requêtes

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}
```

### 3. API Bootstrap - Informations de Base

**Endpoint** : `GET https://www.amazon.{domain}/api/bootstrap`
**Headers supplémentaires** : Cookies de session
**Réponse attendue** :

```json
{
  "authentication": {
    "customerId": "AXXXXXXXXXXXXX",
    "customerName": "John Doe"
  },
  "network": {
    "online": true
  }
}
```

### 4. Gestion des Appareils - Device Manager

#### Lister Tous les Appareils

**Endpoint** : `GET https://www.amazon.{domain}/api/devices-v2/device`
**Headers** : Cookies + CSRF standard
**Réponse** :

```json
{
  "devices": [
    {
      "deviceType": "A2UONLFQW0PADH",
      "serialNumber": "GXXXXXXXXXXXXX",
      "deviceName": "Salon Echo",
      "deviceOwnerCustomerId": "AXXXXXXXXXXXXX",
      "capabilities": ["AUDIO_PLAYER", "VOLUME_SETTING", "MICROPHONE"],
      "online": true
    }
  ]
}
```

#### Obtenir les Préférences d'un Appareil

**Endpoint** : `GET https://www.amazon.{domain}/api/device-preferences/{serialNumber}`
**Réponse** :

```json
{
  "devicePreferences": {
    "wakeWord": "ALEXA",
    "locale": "fr-FR",
    "timeZoneId": "Europe/Paris",
    "distanceUnits": "METRIC",
    "temperatureScale": "CELSIUS"
  }
}
```

### 5. Contrôle du Volume - Volume Control

#### Récupérer le Volume de Tous les Appareils

**Endpoint** : `GET https://www.amazon.{domain}/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes`
**Réponse** :

```json
{
  "volumes": [
    {
      "dsn": "GXXXXXXXXXXXXX",
      "volume": 65
    }
  ]
}
```

#### Modifier le Volume d'un Appareil

**Endpoint** : `POST https://www.amazon.{domain}/api/behaviors/preview`
**Payload** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.SerialNode\",\"nodesToExecute\":[{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"GXXXXXXXXXXXXX\",\"locale\":\"fr-FR\",\"customerId\":\"AXXXXXXXXXXXXX\"},\"type\":\"Alexa.DeviceControls.Volume\",\"volume\":75}]}}",
  "status": "ENABLED"
}
```

### 6. Contrôle Musical - Music Control

#### État de Lecture Actuel

**Endpoint** : `GET https://www.amazon.{domain}/api/np/player`
**Paramètres** : `deviceSerialNumber=GXXXXXXXXXXXXX&deviceType=A2UONLFQW0PADH`
**Réponse** :

```json
{
  "playerInfo": {
    "state": "PLAYING",
    "infoText": {
      "title": "Bohemian Rhapsody",
      "subText1": "Queen",
      "subText2": "A Night at the Opera"
    },
    "progress": {
      "mediaLength": 355000,
      "mediaProgress": 45000
    },
    "provider": {
      "providerName": "Amazon Music"
    }
  }
}
```

#### Commandes de Lecture

**Endpoint** : `POST https://www.amazon.{domain}/api/np/command`
**Payload pour Play/Pause** :

```json
{
  "type": "PlayCommand"
}
```

**Payload pour Next/Previous** :

```json
{
  "type": "NextCommand"
}
```

### 7. Notifications - Alarmes, Timers, Rappels

#### Lister Toutes les Notifications

**Endpoint** : `GET https://www.amazon.{domain}/api/notifications`
**Paramètres** : `cached=true`
**Réponse** :

```json
{
  "notifications": [
    {
      "id": "ALARM_1234567890",
      "type": "Alarm",
      "status": "ON",
      "alarmTime": "07:00",
      "recurringPattern": "weekdays",
      "deviceSerialNumber": "GXXXXXXXXXXXXX"
    },
    {
      "id": "TIMER_1234567891",
      "type": "Timer",
      "status": "ON",
      "remainingTime": 300,
      "deviceSerialNumber": "GXXXXXXXXXXXXX"
    }
  ]
}
```

#### Créer une Alarme

**Endpoint** : `POST https://www.amazon.{domain}/api/alarms`
**Payload** :

```json
{
  "type": "Alarm",
  "label": "Réveil matin",
  "scheduledTime": "07:00",
  "recurringPattern": "weekdays",
  "device": {
    "deviceType": "A2UONLFQW0PADH",
    "deviceSerialNumber": "GXXXXXXXXXXXXX"
  }
}
```

#### Créer un Timer

**Endpoint** : `POST https://www.amazon.{domain}/api/timers`
**Payload** :

```json
{
  "label": "Cuisine",
  "creationTime": 1638360000000,
  "originalDuration": 600,
  "remainingDuration": 600,
  "device": {
    "deviceType": "A2UONLFQW0PADH",
    "deviceSerialNumber": "GXXXXXXXXXXXXX"
  }
}
```

### 8. Commandes Textuelles - Text Commands

#### Commande Vocale Simulée

**Endpoint** : `POST https://www.amazon.{domain}/api/behaviors/preview`
**Payload** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.SerialNode\",\"nodesToExecute\":[{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"GXXXXXXXXXXXXX\",\"locale\":\"fr-FR\",\"customerId\":\"AXXXXXXXXXXXXX\",\"text\":\"allume la lumière du salon\"},\"type\":\"Alexa.TextCommand\"}]}}",
  "status": "ENABLED"
}
```

#### Synthèse Vocale (TTS)

**Endpoint** : `POST https://www.amazon.{domain}/api/behaviors/preview`
**Payload** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.SerialNode\",\"nodesToExecute\":[{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"GXXXXXXXXXXXXX\",\"locale\":\"fr-FR\",\"customerId\":\"AXXXXXXXXXXXXX\",\"text\":\"Bonjour, le café est prêt !\"},\"type\":\"Alexa.Speak\"}]}}",
  "status": "ENABLED"
}
```

### 9. Smart Home Control

#### Lister les Appareils Domotiques

**Endpoint** : `GET https://www.amazon.{domain}/api/behaviors/entities`
**Paramètres** : `skillId=amzn1.ask.1p.smarthome`
**Réponse** :

```json
{
  "entities": [
    {
      "id": "amzn1.alexa.endpoint.XXXXXXXX",
      "displayName": "Lampe Salon",
      "capabilities": [
        {
          "type": "AlexaInterface",
          "interface": "Alexa.PowerController",
          "version": "3"
        },
        {
          "type": "AlexaInterface",
          "interface": "Alexa.BrightnessController",
          "version": "3"
        }
      ]
    }
  ]
}
```

#### Contrôler un Appareil Domotique

**Endpoint** : `POST https://www.amazon.{domain}/api/phoenix`
**Payload pour allumer/éteindre** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.SerialNode\",\"nodesToExecute\":[{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"GXXXXXXXXXXXXX\",\"locale\":\"fr-FR\",\"customerId\":\"AXXXXXXXXXXXXX\",\"target\":\"amzn1.alexa.endpoint.XXXXXXXX\",\"namespace\":\"Alexa.PowerController\",\"name\":\"TurnOn\"},\"type\":\"Alexa.ApiGateway.EndpointControl\"}]}}",
  "status": "ENABLED"
}
```

### 10. Mode Ne Pas Déranger (DND)

#### Statut DND d'un Appareil

**Endpoint** : `GET https://www.amazon.{domain}/api/dnd/status`
**Paramètres** : `deviceSerialNumber=GXXXXXXXXXXXXX`
**Réponse** :

```json
{
  "enabled": false
}
```

#### Modifier le Statut DND

**Endpoint** : `PUT https://www.amazon.{domain}/api/dnd/status`
**Payload** :

```json
{
  "enabled": true,
  "deviceSerialNumber": "GXXXXXXXXXXXXX"
}
```

### 11. Historique Vocal - Privacy API

#### Récupération du Token CSRF Privacy

**Endpoint** : `GET https://www.amazon.{domain}/alexa-privacy/apd/activity`
**Headers supplémentaires** : Cookies de session
**Méthode d'extraction** : Parser le HTML pour trouver le token CSRF dans les balises meta ou inputs hidden

#### Récupération de l'Historique Vocal

**Endpoint** : `POST https://www.amazon.{domain}/alexa-privacy/apd/rvh/customer-history-records-v2/`
**Headers** :

```json
{
  "csrf": "standard_csrf_token",
  "anti-csrftoken-a2z": "privacy_specific_csrf_token",
  "Content-Type": "application/json"
}
```

**Payload** :

```json
{
  "previousRequestToken": null,
  "pageSize": 50,
  "startTime": 0,
  "endTime": 1638360000000
}
```

**Réponse** :

```json
{
  "customerHistoryRecords": [
    {
      "recordKey": "VOICE_1234567890",
      "timestamp": 1638360000000,
      "device": {
        "deviceName": "Salon Echo",
        "serialNumber": "GXXXXXXXXXXXXX",
        "deviceType": "A2UONLFQW0PADH"
      },
      "voiceHistoryRecordItems": [
        {
          "recordItemType": "CUSTOMER_TRANSCRIPT",
          "transcriptText": "Alexa, quelle heure est-il ?"
        },
        {
          "recordItemType": "ALEXA_RESPONSE",
          "transcriptText": "Il est 15 heures 30"
        }
      ],
      "activityStatus": "SUCCESS"
    }
  ]
}
```

#### Gestion des Listes - Implémentation Hybride

**Contexte** : APIs REST désactivées depuis juillet 2024, pas d'API Privacy disponible.

**Endpoint de secours** : `POST /api/behaviors/preview` avec `Alexa.TextCommand`

**Payload pour ajouter un élément** :

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.SerialNode\",\"nodesToExecute\":[{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"GXXXXXXXXXXXXX\",\"locale\":\"fr-FR\",\"customerId\":\"AXXXXXXXXXXXXX\",\"text\":\"ajoute du pain à ma liste de courses\"},\"type\":\"Alexa.TextCommand\"}]}}",
  "status": "ENABLED"
}
```

**Commandes vocales supportées** :

- Ajouter : `"ajoute {item} à ma liste de courses"`
- Supprimer : `"retire {item} de ma liste de courses"`
- Marquer fait : `"marque {item} comme fait dans ma liste de tâches"`
- Vider : `"vide ma liste de courses"`

**Système de cache local** :

```json
{
  "shopping": {
    "data": [
      {
        "id": "mock-1234567890",
        "text": "Pain",
        "completed": false,
        "created_at": "2025-10-12T10:00:00.000Z"
      }
    ],
    "last_updated": "2025-10-12T10:00:00.000Z",
    "source": "mock"
  },
  "todo": {
    "data": [...],
    "last_updated": "2025-10-12T10:00:00.000Z",
    "source": "mock"
  }
}
```

**Flag CLI --real** : Bascule entre mode simulé (cache local) et réel (commandes vocales)

```bash
# Mode simulé (défaut)
alexa lists add "Pain"                    # Cache local uniquement
alexa lists list                         # Affiche données mockées

# Mode réel
alexa lists --real add "Pain"            # Commande vocale réelle
alexa lists --real list                  # Erreur : pas d'API pour lister
```

### 12. Gestion des Erreurs et Rate Limiting

#### Codes d'Erreur Courants

```json
{
  "401": {
    "message": "Unauthorized - Session expired",
    "action": "Refresh cookies"
  },
  "403": {
    "message": "Forbidden - Invalid CSRF token",
    "action": "Regenerate CSRF token"
  },
  "429": {
    "message": "Too Many Requests",
    "action": "Implement exponential backoff"
  },
  "500": {
    "message": "Internal Server Error",
    "action": "Retry with circuit breaker"
  }
}
```

#### Implémentation du Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
```

### 13. Système de Cache Implémenté

#### Structure du Cache Local

```json
{
  "devices": {
    "data": [...],
    "last_updated": "2025-10-12T12:00:00.000Z",
    "ttl": 86400
  },
  "activities": {
    "records": [...],
    "last_updated": "2025-10-12T12:00:00.000Z",
    "source": "privacy_api"
  },
  "smart_home": {
    "entities": [...],
    "last_updated": "2025-10-12T12:00:00.000Z",
    "ttl": 3600
  }
}
```

#### Stratégie de Cache Multi-Niveau

1. **Cache Mémoire** : Données fréquemment utilisées (TTL: 5 minutes)
2. **Cache Fichier** : Persistance entre sessions (TTL: 24h pour appareils)
3. **Cache API** : Données fraîches depuis Amazon
4. **Cache Fallback** : Données simulées si tout échoue

### 14. State Machine - Gestion des États

#### États de Connexion

```python
class ConnectionState(Enum):
    DISCONNECTED = auto()
    AUTHENTICATING = auto()
    AUTHENTICATED = auto()
    REFRESHING_TOKEN = auto()
    ERROR = auto()
    RATE_LIMITED = auto()
    CIRCUIT_OPEN = auto()
```

#### Transitions Valides

- `DISCONNECTED` → `AUTHENTICATING`
- `AUTHENTICATING` → `AUTHENTICATED`, `ERROR`
- `AUTHENTICATED` → `REFRESHING_TOKEN`, `ERROR`, `RATE_LIMITED`, `CIRCUIT_OPEN`
- etc.

### 15. Exemples d'Implémentation Python

#### Appel API avec Gestion d'Erreurs

```python
def call_api_with_retry(self, method, url, **kwargs):
    """Appel API avec retry automatique et circuit breaker."""
    if not self.state_machine.can_execute_commands:
        raise Exception("Connexion non établie")

    try:
        response = self.breaker.call(self.auth.session.request, method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API {method} {url}: {e}")
        if response.status_code == 401:
            self.auth.refresh_session()
        raise
```

#### Parsing des Données d'Appareils

```python
def parse_device_data(self, device_data):
    """Convertit les données brutes d'Amazon en objets Device."""
    devices = []
    for raw_device in device_data.get('devices', []):
        device = Device(
            serial_number=raw_device['serialNumber'],
            device_type=raw_device['deviceType'],
            name=raw_device.get('accountName', raw_device.get('deviceName', 'Unknown')),
            capabilities=raw_device.get('capabilities', []),
            online=raw_device.get('online', False)
        )
        devices.append(device)
    return devices
```

---

## PARTIE 5 : 🎯 Guide Pratique d'Utilisation - Cas d'Usage par Catégorie

Cette section explique **comment utiliser chaque API** avec des exemples concrets, des cas d'usage courants, et des combinaisons pour éviter de réinventer la roue.

### 📋 **Méthodologie Générale**

#### Pattern d'Utilisation Standard

```python
# 1. Vérifier l'état de connexion
bootstrap = api_call('GET', '/api/bootstrap')
if not bootstrap.get('authentication'):
    refresh_cookies()

# 2. Récupérer les données de base (avec cache)
devices = get_cached_data('devices', '/api/devices-v2/device', ttl=86400)

# 3. Effectuer l'action souhaitée
result = api_call('POST', endpoint, payload)

# 4. Gérer les erreurs et mettre à jour le cache si nécessaire
```

#### Gestion des Erreurs par Catégorie

- **401/403** : Régénérer CSRF → Retry
- **429** : Backoff exponentiel (1s, 2s, 4s...)
- **5xx** : Retry avec circuit breaker
- **Timeout** : Augmenter timeout ou utiliser cache

---

### 🔐 **1. Authentification & Session - La Base de Tout**

#### **Pourquoi l'utiliser ?**

- **Vérifier la validité** de votre session avant toute opération
- **Récupérer le customerId** nécessaire pour de nombreuses APIs
- **Détecter les déconnexions** pour rafraîchir automatiquement

#### **Cas d'usage courants :**

```python
# Vérification périodique de session
def check_session_health():
    try:
        bootstrap = api_call('GET', '/api/bootstrap')
        return bootstrap.get('authentication', {}).get('customerId') is not None
    except:
        return False

# Rafraîchissement automatique
def ensure_authenticated():
    if not check_session_health():
        refresh_cookies()
        if not check_session_health():
            raise AuthenticationError("Impossible de se connecter")
```

#### **À combiner avec :**

- Toutes les autres APIs (toujours vérifier avant)

#### **Fréquence d'appel :**

- Au démarrage de l'application
- Toutes les 30 minutes pour vérifier la session
- Avant chaque opération critique

---

### 📱 **2. Gestion des Appareils - Le Point de Départ**

#### **Pourquoi l'utiliser ?**

- **Découvrir vos appareils** automatiquement (pas de config manuelle)
- **Filtrer par capacités** (volume, musique, etc.)
- **Détecter les nouveaux appareils** ajoutés

#### **Cas d'usage courants :**

```python
# Lister les appareils musicaux uniquement
def get_music_devices():
    devices = api_call('GET', '/api/devices-v2/device')['devices']
    return [d for d in devices if 'AUDIO_PLAYER' in d.get('capabilities', [])]

# Trouver l'appareil le plus proche (par nom)
def find_device_by_name(name_pattern):
    devices = api_call('GET', '/api/devices-v2/device')['devices']
    return next((d for d in devices if name_pattern.lower() in d['deviceName'].lower()), None)

# Vérifier si un appareil est en ligne
def is_device_online(serial_number):
    devices = api_call('GET', '/api/devices-v2/device')['devices']
    device = next((d for d in devices if d['serialNumber'] == serial_number), None)
    return device.get('online', False) if device else False
```

#### **À combiner avec :**

- Volume API (pour contrôler le volume de tous les appareils)
- Music API (pour jouer sur un appareil spécifique)
- DND API (pour gérer le mode silencieux)

#### **Fréquence d'appel :**

- Au démarrage (cache 24h)
- Lors de l'ajout d'un nouvel appareil
- Toutes les 6h pour détecter les changements

---

### 🔊 **3. Contrôle du Volume - Interactions Simples**

#### **Pourquoi l'utiliser ?**

- **Synchroniser le volume** sur tous les appareils
- **Restaurer le volume** après une session
- **Ajustements programmés** (volume nocturne, etc.)

#### **Cas d'usage courants :**

```python
# Synchroniser le volume sur tous les appareils
def sync_volume_all_devices(target_volume):
    volumes = api_call('GET', '/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes')

    for vol_info in volumes['volumes']:
        if vol_info['volume'] != target_volume:
            set_device_volume(vol_info['dsn'], target_volume)

# Mode cinéma (volume réduit)
def cinema_mode(enable=True):
    devices = get_music_devices()
    target_volume = 20 if enable else 50

    for device in devices:
        set_device_volume(device['serialNumber'], target_volume)

# Volume adaptatif selon l'heure
def adaptive_volume():
    hour = datetime.now().hour
    if 22 <= hour or hour <= 6:  # Nuit
        sync_volume_all_devices(25)
    elif 7 <= hour <= 9:  # Matinée
        sync_volume_all_devices(60)
    else:  # Jour
        sync_volume_all_devices(45)
```

#### **À combiner avec :**

- Device API (pour connaître tous les appareils)
- Timer API (pour programmer des changements)

#### **Fréquence d'appel :**

- Sur demande utilisateur
- Programmé (toutes les heures pour mode adaptatif)

---

### 🎵 **4. Contrôle Musical - Le Cœur de l'Expérience**

#### **Pourquoi l'utiliser ?**

- **Contrôler la lecture** depuis n'importe où
- **Obtenir l'état actuel** pour l'affichage
- **Créer des playlists** dynamiques

#### **Cas d'usage courants :**

```python
# Système de réveil musical
def morning_routine():
    # 1. Désactiver DND
    set_dnd_status(False)

    # 2. Régler le volume
    set_device_volume("SALON_ECHO_SERIAL", 40)

    # 3. Jouer une playlist douce
    play_music("spotify:playlist:morning_vibes")

    # 4. Annoncer l'heure
    text_to_speech("Il est temps de se lever !")

# Pause automatique quand personne n'écoute
def smart_pause():
    last_interaction = get_last_activity_timestamp()
    if datetime.now() - last_interaction > timedelta(minutes=30):
        pause_music()

# Synchronisation multi-pièces
def sync_playback():
    master_device = get_master_device()
    master_state = get_player_state(master_device)

    if master_state['state'] == 'PLAYING':
        # Synchroniser tous les autres appareils
        for device in get_slave_devices():
            if get_player_state(device)['state'] != 'PLAYING':
                play_music_on_device(device, master_state['current_track'])
```

#### **À combiner avec :**

- Volume API (ajuster le volume selon la musique)
- Activity API (détecter la présence)
- Timer API (arrêter automatiquement)

#### **Fréquence d'appel :**

- Sur interaction utilisateur
- Toutes les 30s pour monitoring d'état
- Programmé pour les routines

---

### ⏰ **5. Alarmes, Timers & Rappels - Gestion du Temps**

#### **Pourquoi l'utiliser ?**

- **Rappels intelligents** (médicaments, courses)
- **Timers de cuisine** multiples
- **Alarmes contextuelles** (selon la météo, trafic)

#### **Cas d'usage courants :**

```python
# Timer de cuisine intelligent
def cooking_timer(dish_name, duration_minutes):
    # Créer le timer
    timer = create_timer(f"Cuisson {dish_name}", duration_minutes * 60)

    # Programmer un rappel 5 min avant
    reminder_time = datetime.now() + timedelta(minutes=duration_minutes - 5)
    create_reminder(f"Préparer la fin de cuisson de {dish_name}", reminder_time)

    # Programmer l'annonce finale
    schedule_announcement(f"{dish_name} est prêt !",
                         datetime.now() + timedelta(minutes=duration_minutes))

# Système de rappels médicamenteux
def medication_reminder(medication, times_per_day, start_date):
    for i in range(times_per_day):
        reminder_time = start_date + timedelta(hours=(24/times_per_day) * i)
        create_recurring_reminder(f"Prendre {medication}", reminder_time, "daily")

# Alarme météo-adaptive
def weather_adaptive_alarm():
    weather = get_weather_forecast()

    if weather['rain_probability'] > 70:
        # Alarme plus tôt pour laisser du temps
        create_alarm("Réveil pluie",
                    (datetime.now() + timedelta(days=1)).replace(hour=6, minute=30))
        text_to_speech("Alarme avancée à cause de la pluie demain")
    else:
        create_alarm("Réveil normal",
                    (datetime.now() + timedelta(days=1)).replace(hour=7, minute=0))
```

#### **À combiner avec :**

- Text-to-Speech (annoncer les rappels)
- Weather API externe (alarmes adaptatives)
- Routine API (enchaîner les actions)

#### **Fréquence d'appel :**

- Sur demande
- Programmé pour les rappels récurrents

---

### 🏠 **6. Contrôle Smart Home - Domotique**

#### **Pourquoi l'utiliser ?**

- **Centraliser le contrôle** de tous vos appareils
- **Créer des scènes** (cinéma, départ, arrivée)
- **Automatisations conditionnelles**

#### **Cas d'usage courants :**

```python
# Scène "Cinéma"
def cinema_scene():
    # 1. Fermer les volets
    control_blind("salon", "close")

    # 2. Allumer la TV et le projecteur
    turn_on_device("tv_salon")
    turn_on_device("projecteur")

    # 3. Régler l'ambiance lumineuse
    set_light_brightness("lampe_salon", 20)
    set_light_color("bandes_led", "blue")

    # 4. Préparer le son
    set_volume_all(30)

    # 5. Annoncer le mode cinéma
    text_to_speech("Mode cinéma activé")

# Système de sécurité
def security_system(arm=True):
    if arm:
        # Activer détecteurs de mouvement
        turn_on_device("detecteur_entree")
        turn_on_device("camera_exterieur")

        # Allumer lumières extérieures
        turn_on_device("spots_jardin")

        # Fermer volets
        control_blind("all", "close")

        text_to_speech("Système de sécurité activé")
    else:
        # Désactiver tout
        turn_off_device("detecteur_entree")
        turn_off_device("camera_exterieur")
        turn_off_device("spots_jardin")

        text_to_speech("Système de sécurité désactivé")

# Mode "Départ de maison"
def leaving_home():
    # Éteindre tous les appareils non-essentiels
    turn_off_lights_except("entree")

    # Régler chauffage sur éco
    set_thermostat_mode("eco")

    # Activer alarme
    security_system(arm=True)

    # Annoncer
    text_to_speech("Mode départ activé. Bonne journée !")
```

#### **À combiner avec :**

- Routine API (enchaîner automatiquement)
- Timer API (délais entre actions)
- TTS (feedback vocal)

#### **Fréquence d'appel :**

- Sur demande utilisateur
- Programmé (lever/coucher du soleil)

---

### 🗣️ **7. Commandes Vocales & TTS - L'Interface Naturelle**

#### **Pourquoi l'utiliser ?**

- **Contrôler Alexa** sans parler (notifications, automatisations)
- **Feedback vocal** pour les actions
- **Intégration** avec d'autres systèmes

#### **Cas d'usage courants :**

```python
# Annonce d'arrivée de colis
def package_delivery_alert(tracking_info):
    message = f"Votre colis {tracking_info['description']} est arrivé !"
    text_to_speech(message, device="entree")

    # Allumer la lumière d'entrée
    turn_on_device("lampe_entree")

# Rappel de réunion
def meeting_reminder(meeting_info):
    message = f"Rappel : réunion {meeting_info['title']} dans 15 minutes en salle {meeting_info['room']}"
    text_to_speech(message)

    # Si urgent, répéter
    if meeting_info.get('urgent'):
        time.sleep(30)
        text_to_speech("Rappel urgent : réunion dans 10 minutes")

# Système d'annonces familiales
def family_announcements():
    announcements = get_pending_announcements()

    for announcement in announcements:
        # Annoncer sur tous les appareils
        text_to_speech_all_devices(announcement['message'])

        # Marquer comme lu
        mark_announcement_read(announcement['id'])

# Commande conditionnelle
def conditional_command(condition, command_text):
    if evaluate_condition(condition):
        send_text_command(command_text)
        return True
    return False

# Exemple : "Si il pleut, ferme les volets"
conditional_command("weather.rain > 50", "ferme les volets du salon")
```

#### **À combiner avec :**

- Timer API (annonces programmées)
- Smart Home (actions physiques)
- Activity API (contexte utilisateur)

#### **Fréquence d'appel :**

- Sur événements externes (arrivée colis, rappels)
- Programmé (annonces régulières)

---

### 🔕 **8. Mode DND - Gestion de la Tranquillité**

#### **Pourquoi l'utiliser ?**

- **Respecter les heures** de sommeil
- **Éviter les interruptions** pendant les appels
- **Mode focus** pour le travail

#### **Cas d'usage courants :**

```python
# Programmation automatique DND
def schedule_dnd():
    # DND automatique la nuit
    enable_dnd_at_time("22:00")
    disable_dnd_at_time("07:00")

    # DND pendant les réunions
    enable_dnd_during_calendar_events()

    # DND sur détection de sommeil
    enable_dnd_on_motion_sensor("chambre", timeout_minutes=30)

# Mode "Ne pas déranger intelligent"
def smart_dnd():
    # Activer si réunion en cours
    if is_in_meeting():
        set_dnd_all_devices(True)

    # Activer si musique forte
    if get_average_volume() > 70:
        set_dnd_all_devices(True, except_device="salon")

    # Désactiver si quelqu'un sonne
    if doorbell_rang():
        set_dnd_all_devices(False)

# DND par pièce
def room_based_dnd():
    # Cuisine : jamais DND (urgences cuisine)
    # Salon : DND après 22h
    # Chambre : DND toujours activé automatiquement
    # Bureau : DND pendant les heures de travail

    for room, devices in get_devices_by_room().items():
        if should_room_be_dnd(room):
            set_dnd_devices(devices, True)
```

#### **À combiner avec :**

- Calendar API (réunions)
- Motion sensors (détection présence)
- Timer API (programmation)

#### **Fréquence d'appel :**

- Programmé (toutes les heures)
- Sur événements (début réunion)

---

### 📚 **9. Routines - Automatisations Complexes**

#### **Pourquoi l'utiliser ?**

- **Enchaîner des actions** complexes
- **Réutiliser** des séquences courantes
- **Déclenchement conditionnel**

#### **Cas d'usage courants :**

```python
# Routine "Soirée Film"
def movie_night_routine():
    # 1. Préparer le salon
    cinema_scene()

    # 2. Préparer les snacks (commande vocale)
    send_text_command("Alexa, rappelle-moi de préparer les popcorns")

    # 3. Lancer Netflix
    send_text_command("Alexa, ouvre Netflix")

    # 4. Annoncer
    text_to_speech("Bon film ! Pensez aux popcorns dans 5 minutes")

# Routine "Arrivée à la maison"
def home_arrival_routine():
    # 1. Désactiver alarme
    security_system(arm=False)

    # 2. Allumer les lumières
    turn_on_device("lumieres_entree")
    turn_on_device("lumieres_salon")

    # 3. Régler température confortable
    set_thermostat_temperature(21)

    # 4. Jouer musique d'accueil
    play_music("spotify:playlist:welcome_home")

    # 5. Annoncer
    text_to_speech("Bienvenue à la maison !")

# Routine conditionnelle "Mauvais temps"
def bad_weather_routine():
    weather = get_weather()

    if weather['wind_speed'] > 50:  # Vent fort
        # Fermer volets automatiquement
        control_blind("all", "close")
        text_to_speech("Volets fermés à cause du vent")

    if weather['temperature'] < 5:  # Froid
        # Augmenter chauffage
        set_thermostat_temperature(23)
        text_to_speech("Chauffage augmenté, il fait froid dehors")

# Routine "Nuit"
def night_routine():
    # 1. Vérifier que tout est fermé
    if not all_doors_locked():
        text_to_speech("Attention : portes non verrouillées")
        return

    # 2. Activer sécurité
    security_system(arm=True)

    # 3. Éteindre lumières progressivement
    fade_out_lights(duration_minutes=10)

    # 4. Activer DND
    set_dnd_all_devices(True)

    # 5. Régler alarme réveil
    create_alarm("Réveil matin", "07:00", recurring="weekdays")

    # 6. Bonne nuit
    text_to_speech("Bonne nuit ! Dormez bien.")
```

#### **À combiner avec :**

- Toutes les autres APIs pour créer des workflows complets

#### **Fréquence d'appel :**

- Sur déclencheurs (arrivée, heure fixe)
- Manuellement

---

### 📊 **10. Historique Vocal - Analyse et Apprentissage**

#### **Pourquoi l'utiliser ?**

- **Analyser les habitudes** vocales
- **Améliorer les automatisations**
- **Détecter les problèmes** de reconnaissance

#### **Cas d'usage courants :**

```python
# Analyse des commandes fréquentes
def analyze_voice_patterns():
    activities = get_voice_history(days=30)

    # Compter les commandes par heure
    hourly_usage = {}
    for activity in activities:
        hour = datetime.fromtimestamp(activity['timestamp']/1000).hour
        hourly_usage[hour] = hourly_usage.get(hour, 0) + 1

    # Identifier les heures de pointe
    peak_hours = sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        'peak_hours': peak_hours,
        'total_commands': len(activities),
        'most_used_device': find_most_used_device(activities)
    }

# Détection d'erreurs de reconnaissance
def detect_recognition_errors():
    activities = get_voice_history(days=7)

    errors = []
    for activity in activities:
        user_text = activity.get('utterance', '')
        alexa_response = activity.get('alexaResponse', '')

        # Détecter réponses d'erreur
        if any(error_phrase in alexa_response.lower() for error_phrase in
               ['je ne comprends pas', 'désolé', 'répétez']):
            errors.append({
                'timestamp': activity['timestamp'],
                'user_said': user_text,
                'alexa_said': alexa_response,
                'device': activity.get('deviceName')
            })

    return errors

# Apprentissage des préférences
def learn_user_preferences():
    activities = get_voice_history(days=90)

    preferences = {
        'favorite_music': extract_music_preferences(activities),
        'preferred_devices': find_preferred_devices(activities),
        'common_times': analyze_usage_times(activities),
        'routine_patterns': detect_routines(activities)
    }

    return preferences

# Amélioration automatique des routines
def optimize_routines_based_on_history():
    preferences = learn_user_preferences()

    # Adapter les routines selon les préférences apprises
    if preferences['preferred_devices']['music'] == 'salon':
        # Modifier la routine pour jouer sur l'appareil préféré
        update_routine_device('morning_music', preferences['preferred_devices']['music'])

    if preferences['common_times']['wake_up'] == '06:30':
        # Ajuster l'alarme selon l'heure d'habitude
        update_alarm_time('morning', preferences['common_times']['wake_up'])
```

#### **À combiner avec :**

- Toutes les APIs pour optimiser les automatisations

#### **Fréquence d'appel :**

- Analyse hebdomadaire/mensuelle
- Sur demande pour debugging

---

### � **11. Gestion des Listes - Système Hybride (Courses, Tâches)**

#### **Pourquoi c'est complexe ?**

- **APIs REST désactivées** depuis juillet 2024 (Amazon privacy)
- **Pas d'API Privacy** disponible (contrairement aux activités)
- **Solution hybride** : Cache simulé + commandes vocales

#### **Cas d'usage courants :**

```python
# Système hybride : Mock + Voice Commands
def smart_list_management():
    # Mode simulé pour développement/test
    list_mgr.add_mock_item("Pain", list_type="shopping")
    items = list_mgr.get_mock_items("shopping")  # Cache local

    # Mode réel pour production
    if real_mode:
        success = list_mgr.add_real_item("Pain", list_type="shopping")  # Commande vocale
        # Note : pas de récupération possible en mode réel
```

#### **Gestion des deux modes :**

```python
def add_to_list(item, list_type="shopping", real_mode=False):
    if real_mode:
        # Commande vocale réelle (pas de feedback de succès garanti)
        command = f"ajoute {item} à ma liste de {list_type}"
        return voice_service.speak(command)
    else:
        # Cache local simulé (feedback immédiat)
        return mock_cache.add_item(item, list_type)

def get_list_items(list_type="shopping", real_mode=False):
    if real_mode:
        # Impossible de récupérer via API
        raise NotImplementedError("Listing réel non disponible - utilisez l'app Alexa")
    else:
        # Cache local
        return mock_cache.get_items(list_type)
```

#### **Limitations du mode réel :**

- ✅ **Ajouter/Supprimer/Marquer fait** : Fonctionne via commandes vocales
- ❌ **Lister les éléments** : Impossible (pas d'API)
- ❌ **Synchronisation** : Pas de sync entre appareils
- ⚠️ **Feedback** : Pas de confirmation de succès

#### **Stratégies recommandées :**

```python
# 1. Mode simulé pour l'interface utilisateur
def ui_add_item(item):
    # Ajout simulé immédiat pour UX fluide
    mock_cache.add_item(item)
    ui_refresh_list()

    # Sync réel en arrière-plan (si activé)
    if background_sync_enabled:
        thread = Thread(target=lambda: real_add_item(item))
        thread.start()

# 2. Mode réel pour les automatisations
def automation_add_item(item):
    # Commande vocale directe
    voice_service.speak(f"ajoute {item} à ma liste de courses")
    # Pas de vérification - assume succès

# 3. Hybride : Mock primary, Real secondary
def hybrid_add_item(item):
    # Toujours ajouter au cache local d'abord
    mock_cache.add_item(item)

    # Puis tenter la commande réelle (ne bloque pas)
    try:
        voice_service.speak(f"ajoute {item} à ma liste de courses")
    except:
        pass  # Ignore les erreurs de commande réelle
```

#### **À combiner avec :**

- Voice Commands (pour les vraies opérations)
- Cache local (pour la persistance simulée)
- Timer API (rappels automatiques)

#### **Fréquence d'appel :**

- Mode simulé : Sur demande utilisateur
- Mode réel : Sur demande + automatisations

---

### �🔄 **12. Combinaisons Puissantes - Éviter de Réinventer**

#### **Dashboard Domotique Complet**

```python
def smart_home_dashboard():
    return {
        'devices': get_all_devices_status(),
        'music': get_current_playback_status(),
        'alarms': get_active_notifications(),
        'weather': get_weather_info(),
        'energy': get_energy_consumption(),
        'security': get_security_status()
    }

# Mise à jour temps réel
def real_time_updates():
    while True:
        dashboard = smart_home_dashboard()

        # Détecter changements
        if dashboard_changed(dashboard):
            notify_user(dashboard)

        time.sleep(30)  # Mise à jour toutes les 30s
```

#### **Système de Notification Intelligent**

```python
def intelligent_notifications():
    # 1. Vérifier le contexte
    context = get_current_context()

    # 2. Adapter selon le contexte
    if context['user_present'] and not context['dnd_active']:
        # Notification normale
        send_notification(message)
    elif context['user_present'] and context['dnd_active']:
        # Notification discrète (lumière seulement)
        flash_light_notification()
    else:
        # Notification différée
        schedule_delayed_notification(message)
```

#### **Gestion Énergétique**

```python
def energy_management():
    # Analyser la consommation
    consumption = analyze_energy_usage()

    # Optimisations automatiques
    if consumption['too_high']:
        # Réduire chauffage
        set_thermostat_temperature(current_temp - 2)
        text_to_speech("Température réduite pour économiser l'énergie")

    # Rappels éco
    if consumption['standby_devices']:
        text_to_speech("Éteignez ces appareils en veille : " + ', '.join(consumption['standby_devices']))
```

---

### 📈 **12. Métriques et Monitoring**

#### **Pourquoi mesurer ?**

- **Optimiser les performances**
- **Détecter les problèmes** tôt
- **Améliorer l'expérience** utilisateur

#### **Métriques Essentielles**

```python
def collect_api_metrics():
    return {
        'response_times': measure_api_response_times(),
        'error_rates': calculate_error_rates(),
        'cache_hit_ratio': get_cache_performance(),
        'device_uptime': check_device_availability(),
        'user_satisfaction': measure_user_interactions()
    }

def generate_performance_report():
    metrics = collect_api_metrics()

    report = f"""
    📊 Rapport de Performance - {datetime.now().strftime('%Y-%m-%d')}

    ⏱️ Temps de réponse moyen : {metrics['response_times']['average']}ms
    ❌ Taux d'erreur : {metrics['error_rates']['total']}%
    💾 Taux de hit cache : {metrics['cache_hit_ratio']}%
    🔋 Disponibilité appareils : {metrics['device_uptime']}%

    🔍 Problèmes détectés :
    {identify_performance_issues(metrics)}

    💡 Recommandations :
    {generate_optimization_suggestions(metrics)}
    """

    return report
```

---

## 🎯 **Résumé : Quand Utiliser Chaque API**

| Catégorie            | Quand l'utiliser     | Fréquence                 | Combinaisons Clés     |
| -------------------- | -------------------- | ------------------------- | --------------------- |
| **Authentification** | Toujours en premier  | Au démarrage + périodique | Toutes                |
| **Appareils**        | Découverte initiale  | Cache 24h                 | Volume, Musique, DND  |
| **Volume**           | Contrôle audio       | Sur demande               | Musique, Routines     |
| **Musique**          | Lecture/contrôle     | Temps réel                | Volume, Activity      |
| **Notifications**    | Rappels, alarmes     | Programmé                 | TTS, Routines         |
| **Smart Home**       | Domotique            | Sur demande               | Routines, TTS         |
| **Text/TTS**         | Communication        | Événementiel              | Toutes                |
| **DND**              | Gestion tranquillité | Programmé                 | Timer, Calendar       |
| **Routines**         | Automatisations      | Sur déclencheur           | Toutes                |
| **Listes**           | Gestion tâches       | Sur demande               | Voice Commands, Cache |
| **Historique**       | Analyse/optimisation | Hebdomadaire              | Toutes                |

**Règle d'or** : Commencez simple, ajoutez de la complexité progressivement, et utilisez toujours le cache pour éviter de surcharger les APIs.

---

## 🚀 **Prochaines Étapes**

Maintenant que vous connaissez les APIs et leurs cas d'usage, vous pouvez :

1. **Commencer petit** : Implémentez un contrôleur de volume simple
2. **Ajouter des fonctionnalités** : Intégrez la musique et les notifications
3. **Créer des routines** : Automatisez vos tâches quotidiennes
4. **Monitorer et optimiser** : Utilisez les métriques pour améliorer

Ce guide vous évite de réinventer la roue en vous donnant des patterns éprouvés pour chaque cas d'usage ! 🎯
