# Analyse des Endpoints API Alexa

## Vue d'ensemble

Ce document référence les endpoints API Alexa validés et fonctionnels pour le contrôle des appareils. Les endpoints sont organisés par fonctionnalité et incluent les méthodes HTTP, paramètres requis et exemples d'utilisation.

## Endpoints Validés ✅

### 1. Gestion des Appareils

#### Liste des appareils

- **Endpoint**: `GET /api/devices-v2/device?cached=false`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Réponse**: Liste complète des appareils avec détails (serial, type, nom, etc.)
- **Utilisation**: Récupération initiale des appareils connectés

#### Informations détaillées d'un appareil

- **Endpoint**: `GET /api/device-preferences/{device_serial}`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Paramètres**: `device_serial` (numéro de série de l'appareil)
- **Réponse**: Préférences et paramètres de l'appareil

### 2. Contrôle du Volume

#### Récupération du volume (tous appareils)

- **Endpoint**: `GET /api/devices/deviceType/dsn/audio/v1/allDeviceVolumes`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Réponse**: Array de volumes pour tous les appareils
  ```json
  {
    "volumes": [
      {
        "dsn": "G6G2MM125193038X",
        "deviceType": "A2UONLFQW0PADH",
        "speakerVolume": 50,
        "speakerMuted": false
      }
    ]
  }
  ```
- **Filtrage**: Utiliser `dsn` (device serial number) pour filtrer par appareil

#### Définition du volume

- **Endpoint**: `POST /api/behaviors/preview`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Payload**:
  ```json
  {
    "behaviorId": "PREVIEW",
    "sequenceJson": "{\"@type\":\"com.amazon.alexa.behaviors.model.Sequence\",\"startNode\":{\"@type\":\"com.amazon.alexa.behaviors.model.ParallelNode\",\"nodesToExecute\":[{\"@type\":\"com.amazon.alexa.behaviors.model.OpaquePayloadOperationNode\",\"type\":\"Alexa.DeviceControls.Volume\",\"operationPayload\":{\"deviceType\":\"A2UONLFQW0PADH\",\"deviceSerialNumber\":\"G6G2MM125193038X\",\"customerId\":\"A2EPGYVJYILASM\",\"locale\":\"fr-FR\",\"value\":\"50\"}}]}}",
    "status": "ENABLED"
  }
  ```
- **Paramètres requis**:
  - `deviceType`: Type de l'appareil (ex: "A2UONLFQW0PADH")
  - `deviceSerialNumber`: Numéro de série (ex: "G6G2MM125193038X")
  - `customerId`: ID client (récupéré via `/api/bootstrap`)
  - `locale`: Langue (ex: "fr-FR")
  - `value`: Volume souhaité (0-100)

### 3. Authentification et Session

#### Bootstrap (état de connexion)

- **Endpoint**: `GET /api/bootstrap?version=0`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Réponse**: État d'authentification et customerId
  ```json
  {
    "authentication": {
      "authenticated": true,
      "customerId": "A2EPGYVJYILASM"
    }
  }
  ```

#### Échange de token refresh

- **Endpoint**: `POST /ap/exchangetoken/cookies`
- **Domaine**: `api.amazon.fr`
- **Headers**: `x-amzn-identity-auth-domain: api.amazon.fr`
- **Payload**: `app_name=Amazon%20Alexa&requested_token_type=auth_cookies&domain=www.amazon.fr&source_token_type=refresh_token&source_token=<refresh_token>`

### 4. Commandes de Contrôle

#### État du player (queue actuelle)

- **Endpoint**: `GET /api/np/player`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Paramètres URL**: `deviceSerialNumber={serial}&deviceType={type}&lemurId={parent_id}&lemurDeviceType={parent_type}`
- **Réponse**: État actuel du player (morceau en cours, position, etc.)
- **Note**: Peut retourner 403 Forbidden pour certains appareils

#### État média détaillé

- **Endpoint**: `GET /api/media/state`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Paramètres URL**: `deviceSerialNumber={serial}&deviceType={type}`
- **Réponse**: État détaillé du média en cours

#### Queue complète

- **Endpoint**: `GET /api/np/queue`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Paramètres URL**: `deviceSerialNumber={serial}&deviceType={type}`
- **Réponse**: Liste complète de la queue de lecture

## Endpoints à Tester 🔄

### Commandes avancées

- **Text Command**: `POST /api/behaviors/preview` avec `Alexa.TextCommand`
- **TTS (Text-to-Speech)**: `POST /api/behaviors/preview` avec `Alexa.Speak`
- **Automation/Routines**: `GET /api/behaviors/v2/automations` puis `POST /api/behaviors/preview`

### 5. Musique et Media

#### Lecture de station radio TuneIn

- **Endpoint**: `PUT /api/entertainment/v1/player/queue`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Payload**:
  ```json
  {
    "contentToken": "music:tuneIn/stationId/s12345"
  }
  ```

#### Lecture de piste bibliothèque

- **Endpoint**: `POST /api/cloudplayer/queue-and-play`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Paramètres URL**: `deviceSerialNumber={serial}&deviceType={type}&mediaOwnerCustomerId={customer_id}&shuffle=false`
- **Payload**:
  ```json
  {
    "trackId": "track_id",
    "playQueuePrime": true
  }
  ```

#### Recherche et lecture de musique

- **Endpoint**: `POST /api/behaviors/operation/validate`
- **Domaine**: `alexa.amazon.fr`
- **Headers**: `csrf: <token>`
- **Payload**:
  ```json
  {
    "type": "Alexa.Music.PlaySearchPhrase",
    "operationPayload": {
      "locale": "fr-FR",
      "musicProviderId": "TUNEIN",
      "searchPhrase": "nom de la musique"
    }
  }
  ```

## Notes Techniques

### Headers Communs

Tous les appels API nécessitent :

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json
Accept-Language: fr-FR,fr;q=0.9
csrf: <token_csrf>
```

### Gestion d'Erreurs

- **401/403**: Token CSRF expiré → régénérer via `/api/bootstrap`
- **429**: Rate limiting → utiliser Circuit Breaker
- **500**: Erreur serveur → retry avec backoff

### Circuit Breaker

Configuration recommandée :

- `failure_threshold`: 3
- `timeout`: 30 secondes
- `half_open_max_calls`: 1

### State Machine

Les appels API ne doivent être faits que si `state_machine.can_execute_commands == True`

## Fallback Strategy

Pour les fonctionnalités non implémentées ou défaillantes :

1. **API directe** (priorité haute) - endpoints validés ci-dessus
2. **Text Command** (fallback) - `Alexa.TextCommand` pour commandes vocales
3. **TTS** (dernier recours) - `Alexa.Speak` pour synthèse vocale

## Mise à Jour

Dernière mise à jour : 8 octobre 2025
Validé avec : Python CLI, refresh token authentication
