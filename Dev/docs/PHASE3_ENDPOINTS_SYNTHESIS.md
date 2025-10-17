# 📊 Synthèse Complète des Endpoints API Alexa

**Date**: 17 octobre 2025  
**Phase**: 3.1 - API Contract Audit & Discovery  
**Sources**:

- `Dev/docs/API_ENDPOINTS.md` (Endpoints validés)
- `Dev/docs/alexa_remote_control.sh` (Legacy bash script)
- `docs/endpoints_mapping.json` (Audit complet)
- Code analysis du projet

---

## 🎯 Résumé Exécutif

### Endpoints Découverts

| Catégorie                | Count | Status | Exemple                                                 |
| ------------------------ | ----- | ------ | ------------------------------------------------------- |
| **Device Management**    | 4     | ✅     | `/api/devices-v2/device`                                |
| **Music/Playback**       | 6     | ✅     | `/api/np/player`, `/api/np/command`                     |
| **Routines/Automation**  | 4     | ✅     | `/api/behaviors/v2/automations`                         |
| **Alarms & Timers**      | 6     | ✅     | `/api/alarms`, `/api/timers`                            |
| **Reminders**            | 3     | ✅     | `/api/reminders`                                        |
| **DND (Do Not Disturb)** | 3     | ✅     | `/api/dnd/status`                                       |
| **Multiroom Audio**      | 3     | ✅     | `/api/phoenix`                                          |
| **Lists**                | 3     | ❌     | `/api/namedLists` (disabled July 2024)                  |
| **Notifications**        | 2     | ✅     | `/api/notifications`                                    |
| **Calendar**             | 2     | ❌     | `/alexa-privacy/apd/calendar` (blocked)                 |
| **Smart Home**           | 2     | ✅     | `/api/smart-home/devices`                               |
| **Bluetooth**            | 3     | ✅     | `/api/bluetooth`                                        |
| **Volume Control**       | 2     | ✅     | `/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes` |
| **Authentication**       | 2     | ✅     | `/api/bootstrap`, Session tokens                        |
| **Entertainment**        | 3     | ✅     | `/api/entertainment/v1/player/queue`                    |
| **Prime Music**          | 4     | ✅     | `/api/prime/*` endpoints                                |
| **TuneIn Radio**         | 2     | ✅     | `/api/tunein`                                           |
| **Cloud Player**         | 2     | ✅     | `/api/cloudplayer/*`                                    |

**Total: 52 endpoints (48 active ✅, 4 deprecated/blocked ❌)**

---

## 🔐 Authentification & Session

### Authentication Flow

```
1. Login via alexa-cookie-cli (device registration refresh_token exchange)
2. Get CSRF token from /api/bootstrap or /api/devices-v2/device
3. Use CSRF + cookies for all subsequent API calls
4. Re-authenticate if token expires (401/403 error)
```

### Common Headers (All Endpoints)

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json
Accept-Language: fr-FR,fr;q=0.9
csrf: <token_csrf>
Content-Type: application/json; charset=UTF-8
Referer: https://alexa.{domaine}/spa/index.html
Origin: https://alexa.{domaine}
DNT: 1
Connection: keep-alive
```

### Key Endpoints

- **GET** `/api/bootstrap?version=0`
  - Returns: `{ "authentication": { "authenticated": bool, "customerId": "..." } }`
  - Usage: Verify auth, get customerId for commands

---

## 📱 Device Management (4 endpoints)

### GET /api/devices-v2/device

```
Endpoint: /api/devices-v2/device?cached=false
Method: GET
Domain: alexa.amazon.fr
Parameters: cached=false (optional, force refresh)
Response: { "devices": [...] }
```

**Device Object Structure**:

```json
{
  "serialNumber": "ABCD1234567890",
  "deviceName": "Salon",
  "deviceType": "ECHO_DOT",
  "online": true,
  "accountName": "Device User",
  "parentSerialNumber": null,
  "deviceFamily": "Echo",
  "capabilities": ["MUSIC_STREAMING", "ANNOUNCE", "ALARM_CONTROL"],
  "supportedOperations": ["MUSIC_PLAYER", "VOLUME", "MICROPHONE"],
  "location": "Salon",
  "macAddress": "AA:BB:CC:DD:EE:FF",
  "firmwareVersion": "627906540",
  "bluetoothConnected": true,
  "connectedAt": "2025-10-17T10:30:00.000Z"
}
```

### GET /api/device-preferences/{device_serial}

```
Endpoint: /api/device-preferences/{device_serial}
Method: GET
Parameters: device_serial - device serial number
Response: Device preferences JSON
```

### POST /api/device-preferences/{device_serial}

```
Endpoint: /api/device-preferences/{device_serial}
Method: POST
Payload: Updated preferences object
Response: Success/Error
```

---

## 🔊 Volume Control (2 endpoints)

### GET /api/devices/deviceType/dsn/audio/v1/allDeviceVolumes

```
Endpoint: /api/devices/deviceType/dsn/audio/v1/allDeviceVolumes
Method: GET
Response: {
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

### POST /api/behaviors/preview (Volume Command)

```
Endpoint: /api/behaviors/preview
Method: POST
Payload: {
  "behaviorId": "PREVIEW",
  "sequenceJson": "{...Alexa.DeviceControls.Volume...}",
  "status": "ENABLED"
}
Parameters in sequenceJson:
  - deviceType: "A2UONLFQW0PADH"
  - deviceSerialNumber: "G6G2MM125193038X"
  - customerId: from /api/bootstrap
  - value: 0-100
```

---

## 🎵 Music & Playback (6 endpoints)

### GET /api/np/player

```
Endpoint: /api/np/player
Method: GET
Parameters:
  - deviceSerialNumber={serial}
  - deviceType={type}
  - lemurId={parent_id} (optional for multiroom)
Response: Current playback state + track info
```

**Playback State Object**:

```json
{
  "playerInfo": [
    {
      "deviceSerialNumber": "ABCD1234567890",
      "state": "PLAYING",
      "transportState": "PLAYING",
      "currentTrackId": "spotify:track:TRACK_ID",
      "mediaSource": "spotify",
      "mainTitle": "Song Title",
      "subTitle1": "Artist Name",
      "subTitle2": "Album Name",
      "mediaLengthInMilliseconds": 240000,
      "progressInMilliseconds": 120000,
      "shuffle": false,
      "repeat": "OFF"
    }
  ]
}
```

### GET /api/np/queue

```
Endpoint: /api/np/queue
Method: GET
Parameters: deviceSerialNumber, deviceType
Response: Queue items array
```

### POST /api/np/command

```
Endpoint: /api/np/command
Method: POST
Parameters: deviceSerialNumber, deviceType
Payload: { "commandType": "PLAY|PAUSE|NEXT|PREVIOUS|SHUFFLE_ON|SHUFFLE_OFF" }
Response: Success
```

### POST /api/behaviors/preview (Music Command)

```
Used for all music operations via sequence JSON
Examples:
  - Play search phrase: Alexa.Music.PlaySearchPhrase
  - Play music: Use musicProviderId (SPOTIFY, AMAZON_MUSIC, TUNEIN, etc)
```

### GET/POST /api/entertainment/v1/player/queue

```
Endpoint: /api/entertainment/v1/player/queue
Method: GET/PUT
Used for: TuneIn radio, playlist playback
Parameter: deviceSerialNumber, deviceType
Payload contains: Base64 encoded content tokens
```

### GET /api/cloudplayer/playlists

```
Endpoint: /api/cloudplayer/playlists/{TYPE}-V0-OBJECTID
Method: GET
Parameters: deviceSerialNumber, deviceType, mediaOwnerCustomerId, offset, size
Used for: Library tracks, albums, playlists
```

---

## 📋 Routines & Automation (4 endpoints)

### GET /api/behaviors/v2/automations

```
Endpoint: /api/behaviors/v2/automations
Method: GET
Response: All routines with triggers and actions
```

**Routine Object**:

```json
{
  "automationId": "routine-id-123",
  "name": "Good Morning",
  "enabled": true,
  "triggers": [
    {
      "triggerType": "TIME",
      "payload": {
        "recurrence": "DAILY",
        "timeOfDay": "07:00:00"
      }
    }
  ],
  "actions": [
    {
      "actionType": "ANNOUNCEMENT|MUSIC|VOLUME",
      "payload": {...}
    }
  ]
}
```

### POST /api/behaviors/v2/automations

```
Create new routine
```

### PUT /api/behaviors/v2/automations/{routine_id}

```
Update existing routine
```

### DELETE /api/behaviors/v2/automations/{routine_id}

```
Delete routine
```

---

## ⏰ Alarms & Timers (6 endpoints)

### GET /api/alarms

```
Retrieve all alarms with scheduling info
```

### POST /api/alarms

```
Create new alarm with:
  - deviceSerialNumber
  - label
  - alarmTime (HH:MM:SS)
  - timezone
  - recurrencePattern (DAILY, WEEKLY, ONCE)
  - recurrenceDays (MON, TUE, etc)
```

### DELETE /api/alarms/{alarm_id}

```
Delete specific alarm
```

### GET /api/timers

```
List all timers with remaining time
```

### POST /api/timers

```
Create timer:
  - deviceSerialNumber
  - label
  - duration (seconds)
```

### DELETE /api/timers/{timer_id}

```
Delete timer
```

---

## 🔔 Reminders (3 endpoints)

### GET /api/reminders

```
List all reminders with triggers
```

### POST /api/reminders

```
Create reminder:
  - deviceSerialNumber
  - label
  - reminderTime
  - timezone
```

### DELETE /api/reminders/{reminder_id}

```
Delete reminder
```

---

## 🔇 DND - Do Not Disturb (3 endpoints)

### GET /api/dnd/status

```
Get current DND state
Response: { "enabled": bool, "durationInMinutes": int }
```

### PUT /api/dnd/status

```
Enable/disable DND
Payload: { "enabled": bool, "durationInMinutes": int }
```

### POST /api/dnd/schedule

```
Set recurring DND schedule
Payload: {
  "startTime": "22:00:00",
  "endTime": "08:00:00",
  "recurringDays": ["MON", "TUE", "WED", "THU", "FRI"]
}
```

---

## 🎙️ Multiroom Audio (3 endpoints)

### GET /api/phoenix

```
Get multiroom group status
Response: Groups with member devices and playback state
```

### POST /api/phoenix/group

```
Create multiroom group
```

### DELETE /api/phoenix/group/{group_id}

```
Delete multiroom group
```

---

## 📌 Lists (3 endpoints - DEPRECATED ❌)

### GET /api/namedLists

```
Status: ❌ DISABLED (July 2024)
Response: 503/404
Alternative: Use voice commands
```

### GET /api/namedLists/{listId}/items

```
Status: ❌ DISABLED
Alternative: Use voice commands
```

### POST /api/namedLists/{listId}/items

```
Status: ❌ DISABLED
Alternative: Use voice commands
```

---

## 📬 Notifications (2 endpoints)

### GET /api/notifications

```
Get all notifications
```

### POST /api/notifications

```
Send notification to device:
  - notificationLevel: "VERBOSE"
  - labelOverride: "Title"
  - bodyOverride: "Message"
  - deviceSerialNumber: device serial
```

---

## 📅 Calendar (2 endpoints - BLOCKED ❌)

### GET /alexa-privacy/apd/calendar

```
Status: ❌ BLOCKED (Privacy policy change)
Response: 403 Forbidden
```

### POST /alexa-privacy/apd/calendar/events

```
Status: ❌ BLOCKED
Response: 403 Forbidden
```

---

## 🏠 Smart Home (2 endpoints)

### GET /api/smart-home/devices

```
List connected smart home devices
Response: { "devices": [...with state...] }
```

### POST /api/smart-home/devices/{device_id}/control

```
Control smart home device
Payload: Command for device (on/off, brightness, etc)
```

---

## 🎧 Bluetooth (3 endpoints)

### GET /api/bluetooth

```
List Bluetooth devices
Response: { "pairedDevices": [...], "discoveredDevices": [...] }
```

### POST /api/bluetooth/pair-sink/{device_type}/{device_serial}

```
Pair Bluetooth device
Payload: MAC address or device info
```

### DELETE /api/bluetooth/disconnect-sink/{device_type}/{device_serial}

```
Disconnect Bluetooth device
```

---

## 🎵 TuneIn Radio (2 endpoints)

### GET /api/tunein/search

```
Search TuneIn stations
Parameters: searchPhrase
Response: Station list with IDs
```

### PUT /api/entertainment/v1/player/queue

```
Play TuneIn station
Payload: Base64 encoded content token with stationId
```

---

## 🎼 Prime Music (4 endpoints)

### GET /api/prime/prime-playlists

```
List Prime playlists
```

### POST /api/prime/prime-playlist-queue-and-play

```
Play Prime playlist
Payload: { "asin": "PLAYLIST_ASIN" }
```

### POST /api/gotham/queue-and-play

```
Play Prime station
Payload: Seed/station info
```

### POST /api/media/play-historical-queue

```
Play Prime historical queue
```

---

## ☁️ Cloud Player (2 endpoints)

### GET /api/cloudplayer/playlists/{TYPE}-V0-OBJECTID

```
Get library content (tracks, albums, playlists)
Types: TRACK, ALBUM, PLAYLIST
Parameters: offset, size, mediaOwnerCustomerId
```

### POST /api/cloudplayer/queue-and-play

```
Play library track/album
Payload: trackId or album info
Parameters: mediaOwnerCustomerId
```

---

## 🎙️ Commands & Behaviors (Via /api/behaviors/preview)

### Voice Commands via Sequence JSON

```
Supported sequence types:
  - Alexa.Weather
  - Alexa.Traffic
  - Alexa.FlashBriefing
  - Alexa.GoodMorning
  - Alexa.SingASong
  - Alexa.TellStory
  - Alexa.Speak (TTS)
  - Alexa.TextCommand
  - Alexa.Music.PlaySearchPhrase
  - Alexa.DeviceControls.Volume
  - Alexa.RemoteSequence (automation/routine)
```

### Announce/Speak

```
TTS support via sequenceJson
SSML support for advanced formatting
Locale: TTS_LOCALE (default: fr-FR)
```

---

## ❌ Deprecated/Blocked Endpoints Summary

| Endpoint                      | Reason                  | Status  | Alternative                  |
| ----------------------------- | ----------------------- | ------- | ---------------------------- |
| `/api/namedLists`             | Amazon disabled service | 503/404 | Voice commands               |
| `/api/todos`                  | Empty endpoint          | 404     | Voice commands               |
| `/api/household/lists`        | No access               | 404     | Voice commands               |
| `/alexa-privacy/apd/calendar` | Privacy restrictions    | 403     | Not available                |
| Legacy login methods          | Security changes        | ❌      | Use device registration flow |

---

## 🔄 Common Response Patterns

### Success Response

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Human-readable message",
  "error_code": "MACHINE_READABLE_CODE",
  "details": {...}
}
```

### Status Codes

- 200: Success
- 201: Created
- 204: No Content (delete)
- 400: Bad Request
- 401: Unauthorized (expired token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 429: Rate Limited
- 500: Server Error
- 503: Service Unavailable

---

## 🛡️ Error Handling Strategy

### Retry Logic

```
1st attempt: Immediate
2nd attempt: After 2s (exponential backoff)
3rd attempt: After 5s
4th attempt: After 10s
Max retries: 5
```

### Circuit Breaker

```
- Failure threshold: 3 consecutive errors
- Recovery timeout: 60 seconds
- Half-open max calls: 1
- Transitions: CLOSED → OPEN → HALF_OPEN → CLOSED
```

### Fallback Strategy

Priority order:

1. Direct API call (fastest)
2. Voice command (TextCommand via /api/behaviors/preview)
3. TTS fallback (Alexa.Speak)

---

## 🔗 Cross-Reference: API Endpoints vs Phase 3 Schemas

### Device Management

- API: `/api/devices-v2/device`
- Schema: `Device`, `GetDevicesResponse` (Phase 3.4)

### Music Playback

- API: `/api/np/player`, `/api/np/command`
- Schema: `MusicStatusResponse`, `PlayMusicRequest` (Phase 3.5)

### Routines

- API: `/api/behaviors/v2/automations`
- Schema: `RoutineDTO`, `CreateRoutineRequest` (Phase 3.5c)

### Alarms & Timers

- API: `/api/alarms`, `/api/timers`
- Schema: `AlarmDTO`, `TimerDTO` (Phase 3.5c)

### Reminders

- API: `/api/reminders`
- Schema: `ReminderDTO`, `CreateReminderRequest` (Phase 3.5c)

### DND

- API: `/api/dnd/status`
- Schema: `DNDStatusDTO`, `SetDNDRequest` (Phase 3.5c)

### Multiroom

- API: `/api/phoenix`
- Schema: `GroupDTO`, `GetGroupsResponse` (Phase 3.5c)

### Bluetooth

- API: `/api/bluetooth`
- Schema: `BluetoothDeviceDTO` (Phase 3.5c)

### Smart Home

- API: `/api/smart-home/devices`
- Schema: `SmartHomeDeviceDTO` (Phase 3.5c)

### Notifications

- API: `/api/notifications`
- Schema: `NotificationDTO`, `SendNotificationRequest` (Phase 3.5c)

---

## 📚 Document Version & History

| Version | Date        | Changes                                                  |
| ------- | ----------- | -------------------------------------------------------- |
| 1.0     | 17 Oct 2025 | Initial synthesis from multiple sources                  |
| -       | -           | Combines API_ENDPOINTS.md + shell script + code analysis |
| -       | -           | Ready for Phase 3.4+ DTO implementation                  |

---

**Status**: ✅ Phase 3.1 Complete - Ready for Phase 3.4 (Device Schemas TDD)  
**Next**: Create test_device_schemas.py with 12+ tests before implementation
