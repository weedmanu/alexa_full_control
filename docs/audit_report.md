# Audit API Calls

## Synthèse

- Fichiers contenant des occurrences: 39
- Endpoints uniques détectés: 112

## Top endpoints détectés

- `https://alexa.{self.config.amazon_domain}/spa/index.html` — 10 occurrence(s)
- `https://{self.config.alexa_domain}/api/phoenix` — 9 occurrence(s)
- `/api/notifications` — 7 occurrence(s)
- `https://alexa.amazon.fr/api/devices` — 5 occurrence(s)
- `https://{self.config.alexa_domain}/api/notifications` — 5 occurrence(s)
- `/api/behaviors/preview` — 4 occurrence(s)
- `/api/behaviors/v2/automations` — 4 occurrence(s)
- `https://alexa.amazon.fr` — 4 occurrence(s)
- `https://alexa.{self.config.amazon_domain}` — 4 occurrence(s)
- `/api/alarms` — 4 occurrence(s)
- `/api/devices-v2/device` — 3 occurrence(s)
- `/api/np/player` — 3 occurrence(s)
- `/api/dnd/status` — 3 occurrence(s)
- `/api/bluetooth` — 3 occurrence(s)
- `https://{self.config.alexa_domain}/api/alarms/{alarm_id}` — 3 occurrence(s)
- `https://{self.config.alexa_domain}/api/timers/{timer_id}` — 3 occurrence(s)
- `/api/bootstrap?version=0` — 2 occurrence(s)
- `/api/np/queue` — 2 occurrence(s)
- `/api/media/state` — 2 occurrence(s)
- `/api/tunein/queue-and-play` — 2 occurrence(s)
- `/api/namedLists` — 2 occurrence(s)
- `/api/dnd/device-status-list` — 2 occurrence(s)
- `/api/calendar` — 2 occurrence(s)
- `https://alexa.amazon.fr/api/devices-v2/device` — 2 occurrence(s)
- `/api/notifications/{notification_id}` — 2 occurrence(s)
- `https://{self.config.alexa_domain}/api/cloudplayer/queue-and-play` — 2 occurrence(s)
- `https://{self.config.alexa_domain}/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome` — 2 occurrence(s)
- `https://alexa.amazon.fr/api/behaviors/preview` — 2 occurrence(s)
- `https://alexa.amazon.fr/spa/index.html` — 2 occurrence(s)
- `/api/alarms/{alarm_id}` — 2 occurrence(s)
- `/api/equalizer/{device_serial}/{device_type}` — 2 occurrence(s)
- `/api/np/command` — 2 occurrence(s)
- `/api/tunein/favorites` — 2 occurrence(s)
- `https://{self.config.alexa_domain}/api/notifications/{reminder_id}` — 2 occurrence(s)
- `/api/behaviors/v2/automations/{routine_id}` — 2 occurrence(s)
- `/api/behaviors/v2/automations/{routine_id}/schedule` — 2 occurrence(s)
- `https://{self.config.alexa_domain}/api/alarms` — 2 occurrence(s)
- `https://{self.config.alexa_domain}/api/reminders` — 2 occurrence(s)
- `https://alexa.amazon.fr/api/timers` — 1 occurrence(s)
- `/api/devices` — 1 occurrence(s)
- `/api/language` — 1 occurrence(s)
- `/api/strings` — 1 occurrence(s)
- `/api/devices-v2/device?cached=false` — 1 occurrence(s)
- `/api/device-preferences` — 1 occurrence(s)
- `/api/notifications/status` — 1 occurrence(s)
- `/api/namedLists/{listId}/items` — 1 occurrence(s)
- `/api/phoenix/state` — 1 occurrence(s)
- `/api/phoenix/group` — 1 occurrence(s)
- `/api/behaviors/automations` — 1 occurrence(s)
- `/api/bluetooth/pair-sink` — 1 occurrence(s)

## Détails par fichier

### alexa_auth\alexa_auth.py
- L18 [requests] : from requests.adapters import HTTPAdapter
- L31 [requests] : session (requests.Session): Session HTTP avec cookies
- L41 [absolute_url] `https://alexa.amazon.fr/api/devices` : ...     response = auth.get("https://alexa.amazon.fr/api/devices")
- L46 [requests] : session: requests.Session
- L68 [requests] : self.session = requests.Session()
- L251 [requests] : def get(self, url: str, **kwargs: Any) -> requests.Response:
- L257 [requests] : **kwargs: Arguments additionnels pour requests.get
- L263 [requests] : requests.RequestException: En cas d'erreur réseau
- L266 [absolute_url] `https://alexa.amazon.fr/api/devices` : >>> response = auth.get("https://alexa.amazon.fr/api/devices")
- L275 [requests] : resp: requests.Response = self.session.get(url, **params)
- L279 [requests] : def post(self, url: str, **kwargs: Any) -> requests.Response:
- L285 [requests] : **kwargs: Arguments additionnels pour requests.post
- L291 [requests] : requests.RequestException: En cas d'erreur réseau
- L295 [absolute_url] `https://alexa.amazon.fr/api/timers` : ...     "https://alexa.amazon.fr/api/timers",
- L311 [requests] : resp: requests.Response = self.session.post(url, **params)
- L315 [requests] : def put(self, url: str, **kwargs: Any) -> requests.Response:
- L321 [requests] : **kwargs: Arguments additionnels pour requests.put
- L335 [requests] : resp: requests.Response = self.session.put(url, **params)
- L339 [requests] : def delete(self, url: str, **kwargs: Any) -> requests.Response:
- L345 [requests] : **kwargs: Arguments additionnels pour requests.delete
- L359 [requests] : resp: requests.Response = self.session.delete(url, **params)

### cli\base_command.py
- L383 [api_path] `/api/devices` : ...     '/api/devices'

### cli\commands\lists.py
- L408 [absolute_url] `https://www.amazon.fr/alexa-privacy/apd/activity?ref=activityHistory` : url = "https://www.amazon.fr/alexa-privacy/apd/activity?ref=activityHistory"

### config\constants.py
- L52 [api_path] `/api/bootstrap?version=0` : BOOTSTRAP = "/api/bootstrap?version=0"
- L53 [api_path] `/api/language` : CSRF_LANGUAGE = "/api/language"
- L55 [api_path] `/api/strings` : CSRF_STRINGS = "/api/strings"
- L58 [api_path] `/api/devices-v2/device` : DEVICES_LIST = "/api/devices-v2/device"
- L59 [api_path] `/api/devices-v2/device?cached=false` : DEVICES_CACHED = "/api/devices-v2/device?cached=false"
- L60 [api_path] `/api/device-preferences` : DEVICE_PREFERENCES = "/api/device-preferences"
- L63 [api_path] `/api/behaviors/preview` : BEHAVIORS_PREVIEW = "/api/behaviors/preview"
- L64 [api_path] `/api/behaviors/v2/automations` : BEHAVIORS_AUTOMATIONS = "/api/behaviors/v2/automations"
- L67 [api_path] `/api/np/player` : PLAYER_STATE = "/api/np/player"
- L68 [api_path] `/api/np/queue` : PLAYER_QUEUE = "/api/np/queue"
- L69 [api_path] `/api/media/state` : MEDIA_STATE = "/api/media/state"
- L70 [api_path] `/api/tunein/queue-and-play` : TUNE_IN = "/api/tunein/queue-and-play"
- L73 [api_path] `/api/notifications` : NOTIFICATIONS = "/api/notifications"
- L74 [api_path] `/api/notifications/status` : NOTIFICATIONS_STATUS = "/api/notifications/status"
- L77 [api_path] `/api/notifications` : ALARMS = "/api/notifications"  # Même endpoint que notifications
- L78 [api_path] `/api/notifications` : TIMERS = "/api/notifications"  # Même endpoint que notifications
- L81 [api_path] `/api/notifications` : REMINDERS = "/api/notifications"  # Même endpoint que notifications
- L84 [api_path] `/api/namedLists` : LISTS = "/api/namedLists"
- L85 [api_path] `/api/namedLists/{listId}/items` : LIST_ITEMS = "/api/namedLists/{listId}/items"
- L88 [api_path] `/api/phoenix/state` : SMART_HOME_DEVICES = "/api/phoenix/state"
- L89 [api_path] `/api/phoenix/group` : SMART_HOME_GROUPS = "/api/phoenix/group"
- L92 [api_path] `/api/behaviors/automations` : ROUTINES = "/api/behaviors/automations"
- L95 [api_path] `/api/dnd/status` : DND_STATUS = "/api/dnd/status"
- L96 [api_path] `/api/dnd/device-status-list` : DND_DEVICE_STATUS = "/api/dnd/device-status-list"
- L99 [api_path] `/api/bluetooth` : BLUETOOTH_STATE = "/api/bluetooth"
- L100 [api_path] `/api/bluetooth/pair-sink` : BLUETOOTH_PAIR = "/api/bluetooth/pair-sink"
- L101 [api_path] `/api/bluetooth/disconnect-sink` : BLUETOOTH_DISCONNECT = "/api/bluetooth/disconnect-sink"
- L104 [api_path] `/api/activities` : ACTIVITIES = "/api/activities"
- L107 [api_path] `/api/calendar` : CALENDAR = "/api/calendar"
- L110 [api_path] `/api/conversations` : CONVERSATIONS = "/api/conversations"
- L111 [api_path] `/api/contacts` : CONTACTS = "/api/contacts"
- L122 [absolute_url] `https://alexa.amazon.fr` : URL de base (ex: "https://alexa.amazon.fr")
- L124 [absolute_url] `https://alexa.{region}` : return f"https://alexa.{region}"
- L135 [absolute_url] `https://www.amazon.fr` : URL de base (ex: "https://www.amazon.fr")
- L137 [absolute_url] `https://www.{region}` : return f"https://www.{region}"
- L149 [absolute_url] `https://alexa.amazon.fr/api/devices-v2/device` : URL complète (ex: "https://alexa.amazon.fr/api/devices-v2/device")
- L154 [absolute_url] `https://alexa.amazon.fr/api/devices-v2/device` : https://alexa.amazon.fr/api/devices-v2/device

### core\activity_manager.py
- L73 [absolute_url] `https://www.{self.config.amazon_domain}/alexa-privacy/apd/rvh/customer-history-records-v2/` : privacy_url = f"https://www.{self.config.amazon_domain}/alexa-privacy/apd/rvh/customer-history-records-v2/"
- L280 [absolute_url] `https://www.{self.config.amazon_domain}/alexa-privacy/apd/activity?ref=activityHistory` : privacy_url = f"https://www.{self.config.amazon_domain}/alexa-privacy/apd/activity?ref=activityHistory"

### core\alarms\alarm_manager.py
- L146 [api_path] `/api/alarms` : result = self._api_call("post", "/api/alarms", json=payload)
- L204 [api_path] `/api/notifications` : result = self._api_call("get", "/api/notifications")
- L248 [absolute_url] `https://{self.config.alexa_domain}/api/alarms/{alarm_id}` : f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
- L251 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L265 [requests] : except requests.exceptions.RequestException as e:
- L297 [api_path] `/api/alarms/{alarm_id}` : result = self._api_call("put", f"/api/alarms/{alarm_id}", json=payload)
- L316 [api_path] `/api/alarms/{alarm_id}` : result = self._api_call("put", f"/api/alarms/{alarm_id}", json=payload)

### core\audio\bluetooth_manager.py
- L35 [api_path] `/api/bluetooth` : response = self._api_call("get", r"/api/bluetooth",
- L55 [api_path] `/api/bluetooth/pair-sink/{device_type}/{device_serial}` : self._api_call("post", r"/api/bluetooth/pair-sink/{device_type}/{device_serial}",
- L71 [api_path] `/api/bluetooth/disconnect-sink/{device_type}/{device_serial}` : self._api_call("post", r"/api/bluetooth/disconnect-sink/{device_type}/{device_serial}",

### core\audio\equalizer_manager.py
- L39 [api_path] `/api/equalizer/{device_serial}/{device_type}` : response = self._api_call("get", r"/api/equalizer/{device_serial}/{device_type}",
- L61 [api_path] `/api/equalizer/{device_serial}/{device_type}` : self._api_call("post", r"/api/equalizer/{device_serial}/{device_type}",

### core\base_manager.py
- L34 [requests] : def get(self, url: str, **kwargs: Any) -> "requests.Response":
- L35 [requests] : return cast("requests.Response", self._session.get(url, **kwargs))
- L37 [requests] : def post(self, url: str, **kwargs: Any) -> "requests.Response":
- L38 [requests] : return cast("requests.Response", self._session.post(url, **kwargs))
- L40 [requests] : def put(self, url: str, **kwargs: Any) -> "requests.Response":
- L41 [requests] : return cast("requests.Response", self._session.put(url, **kwargs))
- L43 [requests] : def delete(self, url: str, **kwargs: Any) -> "requests.Response":
- L44 [requests] : return cast("requests.Response", self._session.delete(url, **kwargs))
- L97 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L98 [absolute_url] `https://alexa.{self.config.amazon_domain}` : "Origin": f"https://alexa.{self.config.amazon_domain}",
- L173 [api_path] `/api/alarms` : endpoint: Endpoint relatif (ex: '/api/alarms')
- L181 [api_path] `/api/alarms` : >>> result = self._api_call('post', '/api/alarms', json=payload, timeout=10)
- L184 [absolute_url] `https://{self.config.alexa_domain}{endpoint}` : url = f"https://{self.config.alexa_domain}{endpoint}"
- L216 [requests] : except requests.exceptions.RequestException as e:

### core\calendar\calendar_manager.py
- L120 [api_path] `/api/calendar/events` : ("/api/calendar/events", "GET"),
- L121 [api_path] `/api/calendar-events` : ("/api/calendar-events", "GET"),
- L122 [api_path] `/api/namedLists?listType=CALENDAR` : ("/api/namedLists?listType=CALENDAR", "GET"),
- L127 [absolute_url] `https://www.{self.config.amazon_domain}{endpoint}` : url = f"https://www.{self.config.amazon_domain}{endpoint}"

### core\circuit_breaker.py
- L49 [requests] : return requests.get("https://api.example.com")
- L49 [absolute_url] `https://api.example.com` : return requests.get("https://api.example.com")

### core\config.py
- L231 [absolute_url] `https://{self.alexa_domain}` : return f"https://{self.alexa_domain}"
- L235 [absolute_url] `https://www.{self.amazon_domain}` : return f"https://www.{self.amazon_domain}"

### core\device_manager.py
- L94 [absolute_url] `https://{self.config.amazon_domain}` : self._base_url = f"https://{self.config.amazon_domain}"
- L172 [api_path] `/api/devices-v2/device` : response_data = self._api_call("get", "/api/devices-v2/device", params={"cached": "false"}, timeout=10)

### core\dnd_manager.py
- L37 [api_path] `/api/dnd/status` : data = self._api_call("get", "/api/dnd/status", timeout=10)
- L68 [api_path] `/api/dnd/status` : result = self._api_call("put", "/api/dnd/status", json=payload, timeout=10)
- L101 [api_path] `/api/dnd/device-status-list` : result = self._api_call("put", "/api/dnd/device-status-list", json=schedule, timeout=10)

### core\lists\lists_manager.py
- L61 [api_path] `/api/namedLists` : ("/api/namedLists", "lists"),
- L62 [api_path] `/api/todos` : ("/api/todos", "values"),  # Retourne {"values": [...]}
- L63 [api_path] `/api/household/lists` : ("/api/household/lists", "lists"),

### core\music\playback_manager.py
- L57 [api_path] `/api/np/command` : "/api/np/command",
- L170 [api_path] `/api/np/command` : "/api/np/command",
- L188 [api_path] `/api/media/history` : "/api/media/history",
- L249 [api_path] `/api/np/player` : "/api/np/player",
- L259 [api_path] `/api/media/state` : "/api/media/state",
- L268 [api_path] `/api/np/queue` : "/api/np/queue",

### core\music\tunein_manager.py
- L41 [api_path] `/api/tunein/search` : "/api/tunein/search",
- L67 [api_path] `/api/tunein/queue-and-play` : "/api/tunein/queue-and-play",
- L85 [api_path] `/api/tunein/favorites` : "/api/tunein/favorites",
- L103 [api_path] `/api/tunein/favorites` : "/api/tunein/favorites",

### core\notification_manager.py
- L37 [api_path] `/api/notifications` : data = self._api_call("get", "/api/notifications", params={"size": limit}, timeout=10)
- L52 [api_path] `/api/notifications/{notification_id}` : result = self._api_call("delete", f"/api/notifications/{notification_id}", timeout=10)
- L66 [api_path] `/api/notifications/{notification_id}` : result = self._api_call("put", f"/api/notifications/{notification_id}", json={"status": "READ"}, timeout=10)
- L94 [api_path] `/api/notifications/createReminder` : result = self._api_call("put", "/api/notifications/createReminder", json=payload, timeout=10)

### core\reminders\reminder_manager.py
- L133 [absolute_url] `https://{self.config.alexa_domain}/api/notifications` : f"https://{self.config.alexa_domain}/api/notifications",
- L187 [absolute_url] `https://{self.config.alexa_domain}/api/notifications` : f"https://{self.config.alexa_domain}/api/notifications",
- L261 [absolute_url] `https://{self.config.alexa_domain}/api/notifications` : f"https://{self.config.alexa_domain}/api/notifications",
- L306 [absolute_url] `https://{self.config.alexa_domain}/api/notifications/{reminder_id}` : f"https://{self.config.alexa_domain}/api/notifications/{reminder_id}",
- L340 [absolute_url] `https://{self.config.alexa_domain}/api/notifications/{reminder_id}` : f"https://{self.config.alexa_domain}/api/notifications/{reminder_id}",

### core\routines\routine_manager.py
- L169 [api_path] `/api/behaviors/v2/automations` : response_data = self._api_call("get", "/api/behaviors/v2/automations", timeout=15)
- L290 [api_path] `/api/behaviors/preview` : "/api/behaviors/preview",
- L418 [api_path] `/api/behaviors/v2/automations` : "/api/behaviors/v2/automations",
- L461 [api_path] `/api/behaviors/v2/automations/{routine_id}` : f"/api/behaviors/v2/automations/{routine_id}",
- L520 [api_path] `/api/behaviors/v2/automations/{routine_id}` : f"/api/behaviors/v2/automations/{routine_id}",
- L558 [api_path] `/api/behaviors/v2/actions` : "/api/behaviors/v2/actions",
- L655 [api_path] `/api/behaviors/v2/automations/{routine_id}/schedule` : f"/api/behaviors/v2/automations/{routine_id}/schedule",
- L688 [api_path] `/api/behaviors/v2/automations/{routine_id}/schedule` : f"/api/behaviors/v2/automations/{routine_id}/schedule",

### core\security\secure_headers.py
- L65 [absolute_url] `https://{self.config.alexa_domain}/spa/index.html` : "Referer": f"https://{self.config.alexa_domain}/spa/index.html",
- L66 [absolute_url] `https://{self.config.alexa_domain}` : "Origin": f"https://{self.config.alexa_domain}",

### core\settings\device_settings_manager.py
- L58 [api_path] `/api/device-preferences/{device_serial}` : response = self._api_call("get", r"/api/device-preferences/{device_serial}",
- L86 [absolute_url] `https://{self.config.alexa_domain}/api/wake-word` : f"https://{self.config.alexa_domain}/api/wake-word",
- L109 [absolute_url] `https://{self.config.alexa_domain}/api/device-preferences/time-zone` : f"https://{self.config.alexa_domain}/api/device-preferences/time-zone",
- L132 [absolute_url] `https://{self.config.alexa_domain}/api/device-preferences/locale` : f"https://{self.config.alexa_domain}/api/device-preferences/locale",
- L185 [api_path] `/api/behaviors/preview` : self._api_call("post", r"/api/behaviors/preview",
- L202 [api_path] `/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes` : response = self._api_call("get", r"/api/devices/deviceType/dsn/audio/v1/allDeviceVolumes",
- L228 [api_path] `/api/bootstrap?version=0` : response = self._api_call("get", r"/api/bootstrap?version=0",

### core\smart_home\device_controller.py
- L148 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L183 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L203 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix/state/{entity_id}` : f"https://{self.config.alexa_domain}/api/phoenix/state/{entity_id}",

### core\smart_home\light_controller.py
- L102 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L140 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L175 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L225 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L288 [absolute_url] `https://{self.config.alexa_domain}/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome` : f"https://{self.config.alexa_domain}/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome",
- L291 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L292 [absolute_url] `https://alexa.{self.config.amazon_domain}` : "Origin": f"https://alexa.{self.config.amazon_domain}",
- L429 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix/state` : f"https://{self.config.alexa_domain}/api/phoenix/state",

### core\smart_home\thermostat_controller.py
- L90 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L129 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",
- L161 [absolute_url] `https://{self.config.alexa_domain}/api/phoenix` : f"https://{self.config.alexa_domain}/api/phoenix",

### core\timers\alarm_manager.py
- L114 [absolute_url] `https://{self.config.alexa_domain}/api/alarms` : f"https://{self.config.alexa_domain}/api/alarms",
- L117 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L118 [absolute_url] `https://alexa.{self.config.amazon_domain}` : "Origin": f"https://alexa.{self.config.amazon_domain}",
- L130 [requests] : except requests.exceptions.RequestException as e:
- L156 [absolute_url] `https://{self.config.alexa_domain}/api/alarms` : f"https://{self.config.alexa_domain}/api/alarms",
- L159 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L175 [requests] : except requests.exceptions.RequestException as e:
- L199 [absolute_url] `https://{self.config.alexa_domain}/api/alarms/{alarm_id}` : f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
- L202 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L212 [requests] : except requests.exceptions.RequestException as e:
- L279 [absolute_url] `https://{self.config.alexa_domain}/api/alarms/{alarm_id}` : f"https://{self.config.alexa_domain}/api/alarms/{alarm_id}",
- L282 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L293 [requests] : except requests.exceptions.RequestException as e:

### core\timers\reminder_manager.py
- L68 [absolute_url] `https://{self.config.alexa_domain}/api/reminders` : f"https://{self.config.alexa_domain}/api/reminders",
- L71 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L92 [absolute_url] `https://{self.config.alexa_domain}/api/reminders` : f"https://{self.config.alexa_domain}/api/reminders",
- L95 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L114 [absolute_url] `https://{self.config.alexa_domain}/api/reminders/{reminder_id}` : f"https://{self.config.alexa_domain}/api/reminders/{reminder_id}",

### core\timers\timer_manager.py
- L139 [absolute_url] `https://{self.config.alexa_domain}/api/timers` : f"https://{self.config.alexa_domain}/api/timers",
- L215 [absolute_url] `https://{self.config.alexa_domain}/api/notifications` : f"https://{self.config.alexa_domain}/api/notifications",
- L300 [absolute_url] `https://{self.config.alexa_domain}/api/timers/{timer_id}` : f"https://{self.config.alexa_domain}/api/timers/{timer_id}",
- L330 [absolute_url] `https://{self.config.alexa_domain}/api/timers/{timer_id}` : f"https://{self.config.alexa_domain}/api/timers/{timer_id}",
- L361 [absolute_url] `https://{self.config.alexa_domain}/api/timers/{timer_id}` : f"https://{self.config.alexa_domain}/api/timers/{timer_id}",

### core\types.py
- L14 [requests] : def get(self, url: str, **kwargs: Any) -> requests.Response: ...
- L16 [requests] : def post(self, url: str, **kwargs: Any) -> requests.Response: ...
- L18 [requests] : def put(self, url: str, **kwargs: Any) -> requests.Response: ...
- L20 [requests] : def delete(self, url: str, **kwargs: Any) -> requests.Response: ...

### data\device_family_mapping.py
- L5 [absolute_url] `https://github.com/alandtse/alexa_media_player/blob/master/custom_components/alexa_media/const.py` : https://github.com/alandtse/alexa_media_player/blob/master/custom_components/alexa_media/const.py

### install\install.py
- L882 [absolute_url] `https://python.org` : Logger.info("Installez Python depuis: https://python.org")

### services\auth.py
- L18 [requests] : - session: requests.Session déjà peuplée avec les cookies Alexa
- L24 [requests] : session: requests.Session

### services\music_library.py
- L35 [absolute_url] `https://alexa.{config.amazon_domain}/{referer_path}` : "Referer": f"https://alexa.{config.amazon_domain}/{referer_path}",
- L36 [absolute_url] `https://alexa.{config.amazon_domain}` : "Origin": f"https://alexa.{config.amazon_domain}",
- L101 [absolute_url] `https://{self.config.alexa_domain}/api/entertainment/v1/player/queue` : f"https://{self.config.alexa_domain}/api/entertainment/v1/player/queue",
- L159 [absolute_url] `https://{self.config.alexa_domain}/api/cloudplayer/queue-and-play` : f"https://{self.config.alexa_domain}/api/cloudplayer/queue-and-play",
- L209 [absolute_url] `https://{self.config.alexa_domain}/api/cloudplayer/queue-and-play` : f"https://{self.config.alexa_domain}/api/cloudplayer/queue-and-play",
- L250 [absolute_url] `https://{self.config.alexa_domain}/api/prime/prime-playlist-queue-and-play` : f"https://{self.config.alexa_domain}/api/prime/prime-playlist-queue-and-play",
- L296 [absolute_url] `https://{self.config.alexa_domain}/api/gotham/queue-and-play` : f"https://{self.config.alexa_domain}/api/gotham/queue-and-play",
- L349 [absolute_url] `https://{self.config.alexa_domain}/api/media/play-historical-queue` : f"https://{self.config.alexa_domain}/api/media/play-historical-queue",
- L393 [absolute_url] `https://{self.config.alexa_domain}/api/cloudplayer/playlists/{playlist_type}-V0-OBJECTID` : f"https://{self.config.alexa_domain}/api/cloudplayer/playlists/{playlist_type}-V0-OBJECTID",
- L452 [absolute_url] `https://{self.config.alexa_domain}/api/prime/prime-playlist-browse-nodes` : f"https://{self.config.alexa_domain}/api/prime/prime-playlist-browse-nodes",
- L476 [absolute_url] `https://{self.config.alexa_domain}/api/prime/prime-playlists-by-browse-node` : f"https://{self.config.alexa_domain}/api/prime/prime-playlists-by-browse-node",
- L522 [absolute_url] `https://{self.config.alexa_domain}/api/prime/prime-sections` : f"https://{self.config.alexa_domain}/api/prime/prime-sections",

### services\sync_service.py
- L370 [absolute_url] `https://{self.config.alexa_domain}/api/devices-v2/device` : f"https://{self.config.alexa_domain}/api/devices-v2/device",
- L390 [absolute_url] `https://{self.config.alexa_domain}/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome` : f"https://{self.config.alexa_domain}/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome",
- L393 [absolute_url] `https://alexa.{self.config.amazon_domain}/spa/index.html` : "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
- L394 [absolute_url] `https://alexa.{self.config.amazon_domain}` : "Origin": f"https://alexa.{self.config.amazon_domain}",
- L415 [absolute_url] `https://{self.config.alexa_domain}/api/notifications` : f"https://{self.config.alexa_domain}/api/notifications",
- L447 [absolute_url] `https://{self.config.alexa_domain}/api/behaviors/v2/automations` : f"https://{self.config.alexa_domain}/api/behaviors/v2/automations",

### services\voice_command_service.py
- L196 [absolute_url] `https://alexa.amazon.fr/api/behaviors/preview` : "https://alexa.amazon.fr/api/behaviors/preview",
- L199 [absolute_url] `https://alexa.amazon.fr/spa/index.html` : "Referer": "https://alexa.amazon.fr/spa/index.html",
- L200 [absolute_url] `https://alexa.amazon.fr` : "Origin": "https://alexa.amazon.fr",
- L316 [absolute_url] `https://alexa.amazon.fr/api/behaviors/preview` : "https://alexa.amazon.fr/api/behaviors/preview",
- L319 [absolute_url] `https://alexa.amazon.fr/spa/index.html` : "Referer": "https://alexa.amazon.fr/spa/index.html",
- L320 [absolute_url] `https://alexa.amazon.fr` : "Origin": "https://alexa.amazon.fr",
- L401 [absolute_url] `https://{self.config.alexa_domain}/api/bootstrap?version=0` : url = f"https://{self.config.alexa_domain}/api/bootstrap?version=0"
- L806 [api_path] `/api/behaviors/preview` : "/api/behaviors/preview",
- L808 [absolute_url] `https://alexa.amazon.fr` : headers={"Origin": "https://alexa.amazon.fr"},

### tools\audit_api_calls.py
- L11 [auth_post] : - occurrences de self._auth.post / self._auth.get
- L11 [auth_get] : - occurrences de self._auth.post / self._auth.get
- L12 [requests] : - appels `requests.`
- L33 [api_path] `/api/...` : # Match '/api/...' enclosed in single or double quotes and capture the path

### utils\http_client.py
- L52 [requests] : def _check_response(self, response: requests.Response) -> None:
- L53 [requests] : """Lève une requests.HTTPError si le status indique une erreur."""
- L56 [requests] : except requests.HTTPError as e:
- L63 [requests] : def _handle_http_error(self, error: requests.HTTPError) -> None:
- L64 [requests] : """Convertit requests.HTTPError en exceptions typées du domaine."""
- L84 [requests] : def get(self, url: str, **kwargs: Any) -> requests.Response:
- L99 [requests] : except requests.HTTPError as e:
- L103 [requests] : except requests.RequestException as e:
- L108 [requests] : def post(self, url: str, **kwargs: Any) -> requests.Response:
- L122 [requests] : except requests.HTTPError as e:
- L125 [requests] : except requests.RequestException as e:
- L129 [requests] : def put(self, url: str, **kwargs: Any) -> requests.Response:
- L139 [requests] : except requests.HTTPError as e:
- L142 [requests] : except requests.RequestException as e:
- L146 [requests] : def delete(self, url: str, **kwargs: Any) -> requests.Response:
- L156 [requests] : except requests.HTTPError as e:
- L159 [requests] : except requests.RequestException as e:

### utils\http_session.py
- L20 [requests] : from requests.adapters import HTTPAdapter
- L42 [absolute_url] `https://alexa.amazon.fr/api/devices` : >>> response = session.get("https://alexa.amazon.fr/api/devices")
- L44 [absolute_url] `https://alexa.amazon.fr/api/devices` : >>> response2 = session.get("https://alexa.amazon.fr/api/devices")
- L50 [api_path] `/api/devices-v2/device` : "/api/devices-v2/device": 300,  # 5 minutes
- L51 [api_path] `/api/behaviors/v2/automations` : "/api/behaviors/v2/automations": 600,  # 10 minutes
- L52 [api_path] `/api/behaviors/entities` : "/api/behaviors/entities": 600,  # 10 minutes
- L54 [api_path] `/api/notifications` : "/api/notifications": 60,  # 1 minute
- L55 [api_path] `/api/bluetooth` : "/api/bluetooth": 120,  # 2 minutes
- L56 [api_path] `/api/equalizer` : "/api/equalizer": 300,  # 5 minutes
- L58 [api_path] `/api/np/player` : "/api/np/player": 0,  # Musique en cours
- L59 [api_path] `/api/timers` : "/api/timers": 0,  # Timers actifs
- L60 [api_path] `/api/alarms` : "/api/alarms": 0,  # Alarmes actives
- L106 [requests] : self.session = requests.Session()
- L162 [requests] : def get(self, url: str, **kwargs) -> requests.Response:
- L174 [absolute_url] `https://alexa.amazon.fr/api/devices` : >>> response = session.get("https://alexa.amazon.fr/api/devices")
- L198 [requests] : def post(self, url: str, **kwargs) -> requests.Response:
- L215 [api_path] `/api/phoenix` : if "/api/phoenix" in url:
- L230 [requests] : def put(self, url: str, **kwargs) -> requests.Response:
- L240 [requests] : def delete(self, url: str, **kwargs) -> requests.Response:

### utils\network_discovery.py
- L48 [api_path] `/api/status` : "/api/status",
- L49 [api_path] `/api/device` : "/api/device",
- L50 [api_path] `/api/calendar` : "/api/calendar",
- L51 [api_path] `/api/events` : "/api/events",
- L226 [absolute_url] `http://{ip}:{port}{endpoint}` : url = f"http://{ip}:{port}{endpoint}"
- L229 [requests] : response = requests.get(url, timeout=3)
- L246 [requests] : except requests.exceptions.Timeout:
- L248 [requests] : except requests.exceptions.ConnectionError:

