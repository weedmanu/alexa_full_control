# API Contracts Documentation - Phase 3

**Objective**: Comprehensive documentation of all API request/response structures for Pydantic DTO implementation.

**Date**: 17 octobre 2025  
**Status**: Phase 3.1 - API Contract Audit & Discovery

---

## 📋 Table of Contents

1. [Device Management APIs](#device-management-apis)
2. [Music/Playback APIs](#musicplayback-apis)
3. [Routine/Automation APIs](#routineautomation-apis)
4. [Timer & Alarm APIs](#timer--alarm-apis)
5. [Reminder APIs](#reminder-apis)
6. [DND (Do Not Disturb) APIs](#dnd-do-not-disturb-apis)
7. [Multiroom Audio APIs](#multiroom-audio-apis)
8. [Lists APIs](#lists-apis)
9. [Notification APIs](#notification-apis)
10. [Calendar APIs](#calendar-apis)
11. [Smart Home APIs](#smart-home-apis)
12. [Bluetooth APIs](#bluetooth-apis)
13. [Authentication APIs](#authentication-apis)
14. [General Error Responses](#general-error-responses)

---

## Device Management APIs

### GET /api/devices-v2/device

**Description**: Retrieve all registered Alexa devices.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/devices-v2/device",
  "query_params": {
    "cached": "false" // Optional: force refresh from API
  }
}
```

**Response - Success (200)**:

```json
{
  "devices": [
    {
      "serialNumber": "ABCD1234567890",
      "deviceName": "Salon",
      "deviceType": "ECHO_DOT",
      "online": true,
      "accountName": "Device User",
      "parentSerialNumber": null,
      "parentBrand": null,
      "deviceFamily": "Echo",
      "deviceAccountId": "amzn1.ask.device.DEVICE_ID",
      "accountId": "ACCOUNT_ID",
      "capabilities": [
        "MUSIC_STREAMING",
        "ANNOUNCE",
        "ALARM_CONTROL",
        "TIMER_CONTROL"
      ],
      "supportedOperations": ["MUSIC_PLAYER", "VOLUME", "MICROPHONE", "ALERTS"],
      "location": "Salon",
      "macAddress": "AA:BB:CC:DD:EE:FF",
      "permissionId": "amzn1.ask.device.permission.PERMISSION_ID",
      "firmwareVersion": "627906540",
      "amazonSoftwareVersion": null,
      "software": "627906540",
      "bluetoothMac": "AA:BB:CC:DD:EE:FF",
      "connected": true,
      "connectedAt": "2025-10-17T10:30:00.000Z",
      "bluetoothConnected": true
    }
  ]
}
```

**Response - Error (401)**:

```json
{
  "errors": [
    {
      "code": "AUTH_ERROR",
      "message": "Authentication failed or token expired"
    }
  ]
}
```

**Error Codes**:

- 401: Unauthorized - authentication failed
- 403: Forbidden - insufficient permissions
- 404: Not Found - device not found
- 429: Too Many Requests - rate limited
- 500: Internal Server Error

---

## Music/Playback APIs

### GET /api/np/player

**Description**: Get current music player status for a device.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/np/player",
  "headers": {
    "deviceSerialNumber": "ABCD1234567890"
  }
}
```

**Response - Success (200)**:

```json
{
  "playerInfo": [
    {
      "deviceSerialNumber": "ABCD1234567890",
      "deviceName": "Salon",
      "deviceFamily": "Echo",
      "playbackSessionId": "session-123456",
      "inSkillProducts": [],
      "supportedOperations": ["PLAY", "PAUSE", "NEXT", "PREVIOUS"],
      "mediaSource": "spotify",
      "state": "PLAYING",
      "transportState": "PLAYING",
      "currentTrackId": "spotify:track:TRACK_ID",
      "queueVersion": "2",
      "radioStationToken": null,
      "playbackOrder": "LINEAR",
      "shuffle": false,
      "repeat": "OFF",
      "trackOrderToken": null,
      "mediaLengthInMilliseconds": 240000,
      "progressInMilliseconds": 120000,
      "cachedMediaSource": null,
      "cacheExpirationTime": 0,
      "mainArtUrl": "https://i.scdn.co/image/ARTIST_IMAGE",
      "mainArtUrlLastUpdate": "2025-10-17T12:00:00Z",
      "mainTitle": "Song Title",
      "subTitle1": "Artist Name",
      "subTitle2": "Album Name",
      "subTitle3": null,
      "mediaReferenceId": "spotify:album:ALBUM_ID"
    }
  ]
}
```

**Error Codes**:

- 401: Unauthorized
- 404: Device not found or no media playing
- 429: Rate limited
- 500: Server error

---

### POST /api/np/command

**Description**: Send a playback command (play, pause, next, previous).

**Request**:

```json
{
  "method": "POST",
  "endpoint": "/api/np/command",
  "headers": {
    "deviceSerialNumber": "ABCD1234567890"
  },
  "body": {
    "commandType": "PLAY",
    "options": {
      "mediaSource": "spotify",
      "mediaId": "spotify:track:TRACK_ID"
    }
  }
}
```

**Supported Commands**: PLAY, PAUSE, NEXT, PREVIOUS, SHUFFLE_ON, SHUFFLE_OFF, REPEAT_ONE, REPEAT_OFF

**Response - Success (200)**:

```json
{
  "success": true,
  "code": "200",
  "message": "Command executed successfully"
}
```

---

## Routine/Automation APIs

### GET /api/behaviors/v2/automations

**Description**: Retrieve all user routines/automations.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/behaviors/v2/automations"
}
```

**Response - Success (200)**:

```json
{
  "automations": [
    {
      "automationId": "routine-id-123",
      "name": "Good Morning",
      "description": "Morning routine",
      "enabled": true,
      "creationTime": "2025-01-15T10:00:00.000Z",
      "lastUpdated": "2025-10-17T10:00:00.000Z",
      "status": "enabled",
      "triggers": [
        {
          "triggerId": "trigger-1",
          "triggerType": "TIME",
          "payload": {
            "recurrence": "DAILY",
            "timeOfDay": "07:00:00"
          }
        }
      ],
      "actions": [
        {
          "actionId": "action-1",
          "actionType": "ANNOUNCEMENT",
          "payload": {
            "text": "Good morning!",
            "deviceSerialNumbers": ["ABCD1234567890"]
          }
        },
        {
          "actionId": "action-2",
          "actionType": "MUSIC",
          "payload": {
            "deviceSerialNumbers": ["ABCD1234567890"],
            "mediaSource": "spotify",
            "mediaId": "spotify:playlist:PLAYLIST_ID"
          }
        }
      ]
    }
  ]
}
```

---

### POST /api/behaviors/v2/automations

**Description**: Create a new routine/automation.

**Request**:

```json
{
  "method": "POST",
  "endpoint": "/api/behaviors/v2/automations",
  "body": {
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
        "actionType": "ANNOUNCEMENT",
        "payload": {
          "text": "Good morning!",
          "deviceSerialNumbers": ["ABCD1234567890"]
        }
      }
    ]
  }
}
```

**Response - Success (201)**:

```json
{
  "automationId": "routine-id-123",
  "name": "Good Morning",
  "enabled": true,
  "creationTime": "2025-10-17T12:00:00.000Z"
}
```

---

### PUT /api/behaviors/v2/automations/{routine_id}

**Description**: Update an existing routine.

**Request**:

```json
{
  "method": "PUT",
  "endpoint": "/api/behaviors/v2/automations/routine-id-123",
  "body": {
    "automationId": "routine-id-123",
    "name": "Good Morning Updated",
    "enabled": true,
    "triggers": [],
    "actions": []
  }
}
```

**Response - Success (200)**:

```json
{
  "automationId": "routine-id-123",
  "name": "Good Morning Updated",
  "enabled": true
}
```

---

### DELETE /api/behaviors/v2/automations/{routine_id}

**Description**: Delete a routine.

**Request**:

```json
{
  "method": "DELETE",
  "endpoint": "/api/behaviors/v2/automations/routine-id-123"
}
```

**Response - Success (204)**: Empty body (No Content)

---

## Timer & Alarm APIs

### GET /api/alarms

**Description**: Retrieve all alarms for all devices.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/alarms"
}
```

**Response - Success (200)**:

```json
{
  "alarms": [
    {
      "id": "alarm-id-123",
      "deviceSerialNumber": "ABCD1234567890",
      "deviceName": "Salon",
      "label": "Wake up",
      "alarmTime": "07:00:00",
      "timezone": "Europe/Paris",
      "recurrencePattern": "DAILY",
      "recurrenceDays": ["MON", "TUE", "WED", "THU", "FRI"],
      "status": "ENABLED",
      "originalTime": "2025-10-18T07:00:00+02:00",
      "createdTime": "2025-01-15T10:00:00.000Z",
      "updatedTime": "2025-10-17T10:00:00.000Z",
      "alarmLabel": "Wake up",
      "sound": {
        "id": "amzn_echo_alarm_default",
        "name": "Default",
        "displayName": "Default Alarm"
      }
    }
  ]
}
```

---

### POST /api/alarms

**Description**: Create a new alarm.

**Request**:

```json
{
  "method": "POST",
  "endpoint": "/api/alarms",
  "body": {
    "deviceSerialNumber": "ABCD1234567890",
    "label": "Wake up",
    "alarmTime": "07:00:00",
    "timezone": "Europe/Paris",
    "recurrencePattern": "DAILY",
    "recurrenceDays": ["MON", "TUE", "WED", "THU", "FRI"]
  }
}
```

**Response - Success (201)**:

```json
{
  "id": "alarm-id-123",
  "deviceSerialNumber": "ABCD1234567890",
  "label": "Wake up",
  "alarmTime": "07:00:00"
}
```

---

### DELETE /api/alarms/{alarm_id}

**Description**: Delete an alarm.

**Request**:

```json
{
  "method": "DELETE",
  "endpoint": "/api/alarms/alarm-id-123"
}
```

**Response - Success (204)**: Empty body (No Content)

---

### GET /api/timers

**Description**: Retrieve all timers for all devices.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/timers"
}
```

**Response - Success (200)**:

```json
{
  "timers": [
    {
      "id": "timer-id-123",
      "deviceSerialNumber": "ABCD1234567890",
      "deviceName": "Salon",
      "label": "Cooking",
      "status": "RUNNING",
      "duration": 600,
      "remainingTime": 300,
      "creationTime": "2025-10-17T12:00:00.000Z",
      "triggerTime": "2025-10-17T12:10:00.000Z",
      "pausedTime": null,
      "notificationSoundUrl": "https://alexa.amazon.fr/api/sound/..."
    }
  ]
}
```

---

### POST /api/timers

**Description**: Create a new timer.

**Request**:

```json
{
  "method": "POST",
  "endpoint": "/api/timers",
  "body": {
    "deviceSerialNumber": "ABCD1234567890",
    "label": "Cooking",
    "duration": 600
  }
}
```

**Response - Success (201)**:

```json
{
  "id": "timer-id-123",
  "deviceSerialNumber": "ABCD1234567890",
  "label": "Cooking",
  "status": "RUNNING",
  "duration": 600,
  "remainingTime": 600
}
```

---

## Reminder APIs

### GET /api/reminders

**Description**: Retrieve all reminders.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/reminders"
}
```

**Response - Success (200)**:

```json
{
  "reminders": [
    {
      "id": "reminder-id-123",
      "deviceSerialNumber": "ABCD1234567890",
      "deviceName": "Salon",
      "label": "Call mom",
      "reminderTime": "2025-10-18T15:00:00",
      "timezone": "Europe/Paris",
      "status": "ACTIVE",
      "creationTime": "2025-10-17T10:00:00.000Z",
      "lastModifiedTime": "2025-10-17T10:00:00.000Z",
      "recurrenceRule": null,
      "triggerTime": "2025-10-18T15:00:00.000Z"
    }
  ]
}
```

---

### POST /api/reminders

**Description**: Create a new reminder.

**Request**:

```json
{
  "method": "POST",
  "endpoint": "/api/reminders",
  "body": {
    "deviceSerialNumber": "ABCD1234567890",
    "label": "Call mom",
    "reminderTime": "2025-10-18T15:00:00",
    "timezone": "Europe/Paris"
  }
}
```

**Response - Success (201)**:

```json
{
  "id": "reminder-id-123",
  "label": "Call mom",
  "reminderTime": "2025-10-18T15:00:00"
}
```

---

### DELETE /api/reminders/{reminder_id}

**Description**: Delete a reminder.

**Request**:

```json
{
  "method": "DELETE",
  "endpoint": "/api/reminders/reminder-id-123"
}
```

**Response - Success (204)**: Empty body (No Content)

---

## DND (Do Not Disturb) APIs

### GET /api/dnd/status

**Description**: Get DND status for a device.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/dnd/status",
  "headers": {
    "deviceSerialNumber": "ABCD1234567890"
  }
}
```

**Response - Success (200)**:

```json
{
  "enabled": true,
  "durationInMinutes": 120,
  "nextScheduledEvent": "2025-10-17T14:30:00.000Z"
}
```

---

### PUT /api/dnd/status

**Description**: Enable/Disable DND for a device.

**Request**:

```json
{
  "method": "PUT",
  "endpoint": "/api/dnd/status",
  "headers": {
    "deviceSerialNumber": "ABCD1234567890"
  },
  "body": {
    "enabled": true,
    "durationInMinutes": 60
  }
}
```

**Response - Success (200)**:

```json
{
  "enabled": true,
  "durationInMinutes": 60
}
```

---

### POST /api/dnd/schedule

**Description**: Set a DND schedule for recurring days/times.

**Request**:

```json
{
  "method": "POST",
  "endpoint": "/api/dnd/schedule",
  "headers": {
    "deviceSerialNumber": "ABCD1234567890"
  },
  "body": {
    "startTime": "22:00:00",
    "endTime": "08:00:00",
    "recurringDays": ["MON", "TUE", "WED", "THU", "FRI"]
  }
}
```

**Response - Success (200)**:

```json
{
  "scheduleId": "schedule-123",
  "startTime": "22:00:00",
  "endTime": "08:00:00",
  "recurringDays": ["MON", "TUE", "WED", "THU", "FRI"]
}
```

---

## Multiroom Audio APIs

### GET /api/phoenix

**Description**: Get multiroom audio/group status.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/phoenix"
}
```

**Response - Success (200)**:

```json
{
  "groups": [
    {
      "id": "group-123",
      "name": "Downstairs",
      "devices": [
        {
          "serialNumber": "ABCD1234567890",
          "name": "Salon",
          "role": "MASTER"
        },
        {
          "serialNumber": "EFGH0987654321",
          "name": "Kitchen",
          "role": "SLAVE"
        }
      ],
      "playbackState": "PLAYING",
      "currentTrack": "Song Title"
    }
  ]
}
```

---

## Lists APIs

### GET /api/namedLists

**Description**: Retrieve all shopping/to-do lists.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/namedLists"
}
```

**Response - Success (200)**:

```json
{
  "lists": [
    {
      "listId": "list-123",
      "name": "Shopping",
      "listType": "SHOPPING",
      "version": 5,
      "itemCount": 3,
      "createdDate": "2025-01-15",
      "updatedDate": "2025-10-17T12:00:00Z",
      "archived": false
    }
  ]
}
```

---

### GET /api/namedLists/{listId}/items

**Description**: Get items in a specific list.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/namedLists/list-123/items"
}
```

**Response - Success (200)**:

```json
{
  "items": [
    {
      "id": "item-123",
      "value": "Milk",
      "status": "active",
      "createdDate": "2025-10-17T12:00:00Z",
      "updatedDate": "2025-10-17T12:00:00Z"
    }
  ]
}
```

---

## Notification APIs

### GET /api/notifications

**Description**: Retrieve notifications.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/notifications"
}
```

**Response - Success (200)**:

```json
{
  "notifications": [
    {
      "id": "notif-123",
      "type": "MESSAGE",
      "source": "user",
      "timestamp": "2025-10-17T12:00:00.000Z",
      "read": false,
      "data": {
        "from": "John Doe",
        "message": "Hello!"
      }
    }
  ]
}
```

---

## Calendar APIs

### GET /api/calendar/events

**Description**: Get calendar events.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/calendar/events",
  "query_params": {
    "timeMin": "2025-10-17T00:00:00Z",
    "timeMax": "2025-10-24T23:59:59Z"
  }
}
```

**Response - Success (200)**:

```json
{
  "events": [
    {
      "id": "event-123",
      "summary": "Meeting",
      "description": "Team meeting",
      "start": "2025-10-18T10:00:00Z",
      "end": "2025-10-18T11:00:00Z",
      "location": "Conference Room"
    }
  ]
}
```

---

## Smart Home APIs

### GET /api/smart-home/devices

**Description**: Get smart home devices (lights, plugs, etc.).

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/smart-home/devices"
}
```

**Response - Success (200)**:

```json
{
  "devices": [
    {
      "id": "device-123",
      "name": "Living Room Light",
      "type": "LIGHT",
      "state": {
        "on": true,
        "brightness": 75,
        "colorTemp": 3000
      }
    }
  ]
}
```

---

## Bluetooth APIs

### GET /api/bluetooth

**Description**: Get Bluetooth device status.

**Request**:

```json
{
  "method": "GET",
  "endpoint": "/api/bluetooth",
  "headers": {
    "deviceSerialNumber": "ABCD1234567890"
  }
}
```

**Response - Success (200)**:

```json
{
  "pairedDevices": [
    {
      "name": "iPhone 12",
      "address": "AA:BB:CC:DD:EE:FF",
      "paired": true,
      "connected": true
    }
  ],
  "discoveredDevices": []
}
```

---

## Authentication APIs

### POST /api/login

**Description**: User authentication (if applicable).

**Request**:

```json
{
  "method": "POST",
  "endpoint": "/api/login",
  "body": {
    "email": "user@example.com",
    "password": "password"
  }
}
```

**Response - Success (200)**:

```json
{
  "sessionId": "session-123",
  "accessToken": "token-abc...",
  "refreshToken": "refresh-xyz...",
  "expiresIn": 3600
}
```

---

## General Error Responses

### Standard Error Response Format

**400 Bad Request**:

```json
{
  "errors": [
    {
      "code": "INVALID_REQUEST",
      "message": "Missing required field: deviceSerialNumber",
      "field": "deviceSerialNumber"
    }
  ]
}
```

**401 Unauthorized**:

```json
{
  "errors": [
    {
      "code": "AUTH_ERROR",
      "message": "Authentication failed or token expired"
    }
  ]
}
```

**403 Forbidden**:

```json
{
  "errors": [
    {
      "code": "FORBIDDEN",
      "message": "Insufficient permissions for this operation"
    }
  ]
}
```

**404 Not Found**:

```json
{
  "errors": [
    {
      "code": "NOT_FOUND",
      "message": "Resource not found: alarm-id-123"
    }
  ]
}
```

**429 Too Many Requests**:

```json
{
  "errors": [
    {
      "code": "RATE_LIMITED",
      "message": "Rate limit exceeded. Retry after 60 seconds",
      "retryAfter": 60
    }
  ]
}
```

**500 Internal Server Error**:

```json
{
  "errors": [
    {
      "code": "INTERNAL_ERROR",
      "message": "An unexpected error occurred"
    }
  ]
}
```

---

## Summary of API Contracts

### Common Patterns

1. **List endpoints**: Return array of objects wrapped in property (e.g., `devices`, `alarms`, `reminders`)
2. **Create endpoints**: Accept POST request with payload, return created object with ID
3. **Update endpoints**: Accept PUT request with full/partial payload
4. **Delete endpoints**: Return 204 No Content on success
5. **Error responses**: Always include `errors` array with `code` and `message`

### HTTP Methods Used

- **GET**: Retrieve data (read-only)
- **POST**: Create new resource or perform action
- **PUT**: Update existing resource
- **DELETE**: Remove resource

### Common Headers

```
Authorization: Bearer {access_token}
Content-Type: application/json
X-Device-Serial: {device_serial_number}  # For device-specific operations
```

### Status Codes

- 200: OK (successful GET/PUT)
- 201: Created (successful POST)
- 204: No Content (successful DELETE)
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

---

## Next Steps

1. ✅ **Phase 3.1 COMPLETE**: API contracts documented
2. ⏭️ **Phase 3.2**: Design DTO layer architecture (create design_dto_layer.md)
3. ⏭️ **Phase 3.3**: Implement base DTO classes (core/schemas/base.py)
4. ⏭️ **Phase 3.4-5**: Implement specific domain schemas with TDD

---

**Document Version**: 1.0  
**Last Updated**: 17 octobre 2025  
**Phase**: 3.1 Complete ✅
