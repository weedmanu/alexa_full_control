# 🔌 Référence Complète des API Alexa

**Date** : 16 octobre 2025  
**Statut** : ✅ Endpoints validés et fonctionnels  
**Dernière mise à jour** : Déploiement CLI Python 2.0.0

---

## 🎯 Introduction

Ce document liste **tous les endpoints API Alexa validés** actuellement utilisés dans le projet pour contrôler vos appareils Alexa. Chaque endpoint inclut domaine, headers, paramètres et exemple de réponse.

### ✅ Endpoints Fonctionnels

| Endpoint                   | Méthode | Domaine           | Statut | Usage                   |
| -------------------------- | ------- | ----------------- | ------ | ----------------------- |
| `/api/devices-v2/device`   | GET     | `alexa.amazon.fr` | ✅     | Lister appareils        |
| `/api/bootstrap?version=0` | GET     | `alexa.amazon.fr` | ✅     | Info session            |
| `/api/behaviors/preview`   | POST    | `alexa.amazon.fr` | ✅     | Commandes (volume, TTS) |
| `/api/np/player`           | GET     | `alexa.amazon.fr` | ✅     | État du player          |
| `/api/notifications`       | GET     | `alexa.amazon.fr` | ✅     | Notifications           |

---

## 🔐 Authentification & Session

### Bootstrap (État de Connexion)

```
GET /api/bootstrap?version=0
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

**Réponse**:

```json
{
  "authentication": {
    "authenticated": true,
    "customerId": "A2EPGYVJYILASM"
  }
}
```

**Usage**: Vérifier l'authentification et récupérer le `customerId` pour les commandes.

---

## 📱 Gestion des Appareils

### Liste Complète des Appareils

```
GET /api/devices-v2/device?cached=false
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

**Réponse**: Liste JSON avec tous les appareils (serial, type, nom, état).

**Utilisation**: Découverte des appareils au démarrage.

### Informations Détaillées d'un Appareil

```
GET /api/device-preferences/{device_serial}
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

**Paramètres**:

- `device_serial`: Numéro de série de l'appareil

---

## 🔊 Contrôle du Volume

### Récupération du Volume (Tous les Appareils)

```
GET /api/devices/deviceType/dsn/audio/v1/allDeviceVolumes
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

**Réponse**:

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

### Définition du Volume

```
POST /api/behaviors/preview
Domaine: alexa.amazon.fr
Headers: csrf: <token>
Content-Type: application/json
```

**Payload**:

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{...Alexa.DeviceControls.Volume...}",
  "status": "ENABLED"
}
```

**Paramètres requis**:

- `deviceType`: Type appareil (ex: "A2UONLFQW0PADH")
- `deviceSerialNumber`: Numéro de série (ex: "G6G2MM125193038X")
- `customerId`: ID client (via `/api/bootstrap`)
- `value`: Volume (0-100)

---

## 🎵 Musique et Médias

### État du Player Actuel

```
GET /api/np/player
Domaine: alexa.amazon.fr
Headers: csrf: <token>
Paramètres: deviceSerialNumber={serial}&deviceType={type}&lemurId={parent_id}
```

**Réponse**: État du player (morceau, position, qualité audio).

### Queue de Lecture

```
GET /api/np/queue
Domaine: alexa.amazon.fr
Headers: csrf: <token>
Paramètres: deviceSerialNumber={serial}&deviceType={type}
```

**Réponse**: Liste complète de la queue.

### Recherche et Lecture de Musique

```
POST /api/behaviors/preview
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

**Payload**:

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"@type\":\"...\",\"type\":\"Alexa.Music.PlaySearchPhrase\",\"operationPayload\":{\"searchPhrase\":\"nom de la musique\"}}",
  "status": "ENABLED"
}
```

---

## 🔔 Notifications et Rappels

### Lister les Notifications

```
GET /api/notifications
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

### Envoyer une Notification

```
POST /api/notifications
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

**Payload**:

```json
{
  "notificationLevel": "VERBOSE",
  "labelOverride": "Titre",
  "bodyOverride": "Message",
  "deviceSerialNumber": "{serial}"
}
```

---

## 📋 Commandes Vocales (Fallback)

### Texte Command (Simulation de Commande Vocale)

```
POST /api/behaviors/preview
Domaine: alexa.amazon.fr
Headers: csrf: <token>
```

**Payload**:

```json
{
  "behaviorId": "PREVIEW",
  "sequenceJson": "{\"type\":\"Alexa.TextCommand\",\"operationPayload\":{\"command\":\"<commande vocale>\"}}",
  "status": "ENABLED"
}
```

**Exemple**: `"command": "Alexa, allume la lumière du salon"`

---

## ⚠️ Endpoints Dépréciés/Bloqués

### ❌ API Listes (Désactivées depuis juillet 2024)

```
GET /api/namedLists        → 503/404 (Service désactivé)
GET /api/todos             → 404 (Endpoint vide)
GET /api/household/lists   → 404 (Alternative non-fonctionnelle)
```

**Solution**: Utiliser les commandes vocales pour les listes.

### ❌ Calendrier (Bloqué par Amazon)

```
GET /alexa-privacy/apd/calendar           → 403 (Accès bloqué)
POST /alexa-privacy/apd/calendar/events   → 403 (Accès bloqué)
```

**Raison**: Changements de politique de confidentialité Amazon.

---

## 🛠️ Headers Communs

Tous les appels API Alexa doivent inclure:

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json
Accept-Language: fr-FR,fr;q=0.9
csrf: <token_csrf>
Content-Type: application/json; charset=UTF-8
Referer: https://alexa.{domaine}/spa/index.html
Origin: https://alexa.{domaine}
```

---

## 🔄 Gestion des Erreurs

| Code        | Signification        | Action                         |
| ----------- | -------------------- | ------------------------------ |
| **200**     | Succès               | Continuer                      |
| **401/403** | Token expiré         | Régénérer via `/api/bootstrap` |
| **429**     | Rate limiting        | Attendre + Circuit Breaker     |
| **500**     | Erreur serveur       | Retry avec backoff exponentiel |
| **503**     | Service indisponible | Endpoint probablement dépublié |

---

## 🔌 Circuit Breaker (Protection)

Configuration recommandée pour éviter les surcharges:

- **Seuil d'erreurs** : 3 appels consécutifs en erreur
- **Timeout** : 30 secondes
- **Max appels en half-open** : 1

---

## 💾 Stratégie de Fallback

**Ordre de priorité pour les fonctionnalités**:

1. **API directe** (priorité haute) - endpoints validés ci-dessus
2. **Commande vocale** (fallback) - `Alexa.TextCommand` si API échoue
3. **TTS** (dernier recours) - `Alexa.Speak` pour synthèse vocale

---

## 📚 Ressources

- Documentation archivée: `Dev/docs/archived/`
- Logs détaillés: Activer avec `DEBUG=true`
- Tests API: `pytest Dev/pytests/test_integration.py -v`

---

**Mise à jour** : 16 octobre 2025  
**Validé avec**: Python CLI 2.0.0, Windows/Linux/macOS

---

## 🧪 Échantillons JSON (générés)

Un test Pytest `Dev/pytests/test_api_endpoints_all.py` peut interroger une série d'endpoints
et sauvegarder les réponses JSON pour inspection manuelle dans `Dev/api_samples/`.

Pour exécuter (nécessite la variable d'environnement `ALEXA_TEST_COOKIES` pointant vers le dossier
contenant vos cookies `cookie-resultat.json` ou `cookie.txt`):

```powershell
$env:ALEXA_TEST_COOKIES = 'C:\chemin\vers\cookies'
; .venv\Scripts\python.exe -m pytest Dev/pytests/test_api_endpoints_all.py -q
```

Les fichiers seront écrits dans `Dev/api_samples/` avec des noms dérivés du chemin de l'endpoint.
