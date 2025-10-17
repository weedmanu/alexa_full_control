"""
Constantes immuables centralisées.

Ce module contient toutes les constantes qui ne changent jamais :
- Régions Amazon/Alexa supportées
- Endpoints API Alexa
- Constantes de configuration (timeouts, retries, etc.)

Ces valeurs sont en MAJUSCULES et ne doivent JAMAIS être modifiées au runtime.
"""

from typing import Dict


class AmazonRegions:
    """Régions Amazon supportées."""

    FR = "amazon.fr"
    DE = "amazon.de"
    COM = "amazon.com"
    UK = "amazon.co.uk"
    IT = "amazon.it"
    ES = "amazon.es"
    CA = "amazon.ca"

    # Région par défaut
    DEFAULT = FR

    @classmethod
    def get_all(cls) -> Dict[str, str]:
        """Retourne toutes les régions supportées."""
        return {
            "FR": cls.FR,
            "DE": cls.DE,
            "COM": cls.COM,
            "UK": cls.UK,
            "IT": cls.IT,
            "ES": cls.ES,
            "CA": cls.CA,
        }

    @classmethod
    def is_valid(cls, region: str) -> bool:
        """Vérifie si une région est valide."""
        return region in cls.get_all().values()


class AlexaAPI:
    """Endpoints API Alexa centralisés."""

    # === AUTHENTICATION & SESSION ===
    BOOTSTRAP = "/api/bootstrap?version=0"
    CSRF_LANGUAGE = "/api/language"
    CSRF_SPA = "/spa/index.html"
    CSRF_STRINGS = "/api/strings"

    # === DEVICES ===
    DEVICES_LIST = "/api/devices-v2/device"
    DEVICES_CACHED = "/api/devices-v2/device?cached=false"
    DEVICE_PREFERENCES = "/api/device-preferences"

    # === BEHAVIORS (Commandes) ===
    BEHAVIORS_PREVIEW = "/api/behaviors/preview"
    BEHAVIORS_AUTOMATIONS = "/api/behaviors/v2/automations"

    # === MUSIC & PLAYBACK ===
    PLAYER_STATE = "/api/np/player"
    PLAYER_QUEUE = "/api/np/queue"
    MEDIA_STATE = "/api/media/state"
    TUNE_IN = "/api/tunein/queue-and-play"

    # === NOTIFICATIONS ===
    NOTIFICATIONS = "/api/notifications"
    NOTIFICATIONS_STATUS = "/api/notifications/status"

    # === ALARMS & TIMERS ===
    ALARMS = "/api/notifications"  # Même endpoint que notifications
    TIMERS = "/api/notifications"  # Même endpoint que notifications

    # === REMINDERS ===
    REMINDERS = "/api/notifications"  # Même endpoint que notifications

    # === LISTS ===
    LISTS = "/api/namedLists"
    LIST_ITEMS = "/api/namedLists/{listId}/items"

    # === SMART HOME ===
    SMART_HOME_DEVICES = "/api/phoenix/state"
    SMART_HOME_GROUPS = "/api/phoenix/group"

    # === ROUTINES ===
    ROUTINES = "/api/behaviors/automations"

    # === DO NOT DISTURB ===
    DND_STATUS = "/api/dnd/status"
    DND_DEVICE_STATUS = "/api/dnd/device-status-list"

    # === BLUETOOTH ===
    BLUETOOTH_STATE = "/api/bluetooth"
    BLUETOOTH_PAIR = "/api/bluetooth/pair-sink"
    BLUETOOTH_DISCONNECT = "/api/bluetooth/disconnect-sink"

    # === ACTIVITIES ===
    ACTIVITIES = "/api/activities"

    # === CALENDAR ===
    CALENDAR = "/api/calendar"

    # === COMMUNICATION ===
    CONVERSATIONS = "/api/conversations"
    CONTACTS = "/api/contacts"

    @staticmethod
    def get_base_url(region: str = AmazonRegions.DEFAULT) -> str:
        """
        Retourne l'URL de base Alexa pour une région.

        Args:
            region: Région Amazon (ex: "amazon.fr")

        Returns:
            URL de base (ex: "https://alexa.amazon.fr")
        """
        return f"https://alexa.{region}"

    @staticmethod
    def get_amazon_url(region: str = AmazonRegions.DEFAULT) -> str:
        """
        Retourne l'URL de base Amazon pour une région.

        Args:
            region: Région Amazon (ex: "amazon.fr")

        Returns:
            URL de base (ex: "https://www.amazon.fr")
        """
        return f"https://www.{region}"

    @staticmethod
    def get_full_url(endpoint: str, region: str = AmazonRegions.DEFAULT) -> str:
        """
        Construit l'URL complète pour un endpoint.

        Args:
            endpoint: Endpoint API (constante de cette classe)
            region: Région Amazon

        Returns:
            URL complète (ex: "https://alexa.amazon.fr/api/devices-v2/device")

        Example:
            >>> url = AlexaAPI.get_full_url(AlexaAPI.DEVICES_LIST)
            >>> print(url)
            https://alexa.amazon.fr/api/devices-v2/device
        """
        return f"{AlexaAPI.get_base_url(region)}{endpoint}"


class AppConstants:
    """Constantes de configuration de l'application."""

    # === TIMEOUTS ===
    DEFAULT_TIMEOUT = 30  # secondes
    AUTH_TIMEOUT = 60  # secondes
    LONG_TIMEOUT = 120  # secondes

    # === RETRIES ===
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # secondes
    RETRY_BACKOFF_FACTOR = 2

    # === CIRCUIT BREAKER ===
    CIRCUIT_BREAKER_THRESHOLD = 5  # erreurs avant ouverture
    CIRCUIT_BREAKER_TIMEOUT = 60  # secondes avant half-open
    CIRCUIT_BREAKER_MAX_HALF_OPEN_CALLS = 1

    # === CACHE ===
    DEFAULT_CACHE_TTL = 300  # 5 minutes
    DEVICES_CACHE_TTL = 300  # 5 minutes
    ROUTINES_CACHE_TTL = 600  # 10 minutes
    SHORT_CACHE_TTL = 60  # 1 minute

    # === VOLUMES ===
    MIN_VOLUME = 0
    MAX_VOLUME = 100
    DEFAULT_SPEAK_VOLUME = 50
    DEFAULT_NORMAL_VOLUME = 30

    # === RATE LIMITING ===
    RATE_LIMIT_CALLS = 10  # appels
    RATE_LIMIT_PERIOD = 1  # seconde
    RATE_LIMIT_BURST = 20  # burst max

    # === USER AGENTS ===
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:1.0) Alexa-CLI/1.0"
    API_USER_AGENT = "AmazonWebView/Amazon Alexa/2.2.651540.0/iOS/18.3.1/iPhone"

    # === LOCALES ===
    DEFAULT_LANGUAGE = "fr_FR"
    DEFAULT_TTS_LOCALE = "fr-FR"

    # === FILE EXTENSIONS ===
    JSON_EXT = ".json"
    LOG_EXT = ".log"
    BACKUP_EXT = ".bak"

    # === MISC ===
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    DEFAULT_PAGE_SIZE = 50
