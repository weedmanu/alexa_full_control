"""
Contexte partagé pour toutes les commandes CLI.

Ce module définit l'objet Context qui contient toutes les ressources partagées
(authentification, configuration, state machine, managers, circuit breaker).

Le Context est injecté dans chaque commande pour éviter les variables globales
et faciliter les tests (injection de dépendances).

Auteur: M@nu
Date: 7 octobre 2025
"""

from pathlib import Path
from typing import Optional

from utils.logger import get_logger

from core.circuit_breaker import CircuitBreaker
from core.config import Config
from core.state_machine import AlexaStateMachine
from services.cache_service import CacheService

logger = get_logger("context")


class Context:
    """
    Contexte partagé contenant toutes les ressources nécessaires aux commandes.

    Ce contexte est créé au démarrage de la CLI et injecté dans chaque commande.
    Il centralise:
    - L'authentification (auth)
    - La configuration (config)
    - La state machine (état de connexion)
    - Le gestionnaire d'appareils (device_mgr)
    - Le circuit breaker (protection API)
    - Tous les managers de fonctionnalités

    Attributes:
        config (Config): Configuration de l'application
        auth: Objet d'authentification AlexaAuth
        state_machine (AlexaStateMachine): Machine à états de connexion
        device_mgr: Gestionnaire d'appareils
        breaker (CircuitBreaker): Circuit breaker pour protection API

        # Managers de fonctionnalités
        timer_mgr: Gestionnaire de timers
        alarm_mgr: Gestionnaire d'alarmes
        reminder_mgr: Gestionnaire de rappels
        light_ctrl: Contrôleur de lumières
        thermostat_ctrl: Contrôleur de thermostats
        smarthome_ctrl: Contrôleur smart home général
        playback_mgr: Gestionnaire de playback musique
        tunein_mgr: Gestionnaire TuneIn
        library_mgr: Gestionnaire de bibliothèque musicale
        notification_mgr: Gestionnaire de notifications
        dnd_mgr: Gestionnaire Do Not Disturb
        activity_mgr: Gestionnaire d'activités
        announcement_mgr: Gestionnaire d'annonces
        list_mgr: Gestionnaire de listes
        equalizer_mgr: Gestionnaire égaliseur
        bluetooth_mgr: Gestionnaire Bluetooth
        device_settings_mgr: Gestionnaire paramètres appareils
    """

    def __init__(self, config: Optional[Config] = None, config_file: Optional[Path] = None):
        """
        Initialise le contexte.

        Args:
            config: Configuration (optionnel, créée si None)
            config_file: Fichier de configuration personnalisé (non utilisé actuellement)
        """
        # Configuration
        if config:
            self.config = config
        else:
            # TODO: Ajouter support config_file à Config si nécessaire
            self.config = Config()

        # State machine (état de connexion)
        self.state_machine = AlexaStateMachine()

        # Circuit breaker (protection API)
        self.breaker = CircuitBreaker(failure_threshold=3, timeout=30.0, half_open_max_calls=1)

        # Services centraux
        self.cache_service = CacheService()

        # Auth et device manager (initialisés à None, créés au login)
        self.auth = None
        self._device_mgr_instance = None
        self._sync_service = None

        # Managers de fonctionnalités (lazy-loaded)
        self._timer_mgr = None
        self._alarm_mgr = None
        self._reminder_mgr = None
        self._light_ctrl = None
        self._thermostat_ctrl = None
        self._smarthome_ctrl = None
        self._playback_mgr = None
        self._tunein_mgr = None
        self._library_mgr = None
        self._music_library = None  # Service MusicLibrary (nouveau - shell script parity)
        self._notification_mgr = None
        self._dnd_mgr = None
        self._activity_mgr = None
        self._announcement_mgr = None
        self._calendar_mgr = None
        self._routine_mgr = None
        self._list_mgr = None
        self._equalizer_mgr = None
        self._bluetooth_mgr = None
        self._device_settings_mgr = None
        self._voice_service = None  # Service de commandes vocales

        logger.debug("Context initialisé")

    # ========================================================================
    # PROPRIÉTÉS LAZY-LOADED POUR LES MANAGERS
    # ========================================================================

    @property
    def device_mgr(self):
        """Gestionnaire d'appareils (lazy-loaded)."""
        if self._device_mgr_instance is None and self.auth:
            from core.device_manager import DeviceManager

            self._device_mgr_instance = DeviceManager(self.auth, self.state_machine)
            logger.debug("DeviceManager chargé")
        return self._device_mgr_instance

    @property
    def timer_mgr(self):
        """Gestionnaire de timers (lazy-loaded)."""
        if self._timer_mgr is None and self.auth:
            from core.timers import TimerManager

            self._timer_mgr = TimerManager(self.auth, self.config, self.state_machine)
            logger.debug("TimerManager chargé")
        return self._timer_mgr

    @property
    def alarm_mgr(self):
        """Gestionnaire d'alarmes (lazy-loaded)."""
        if self._alarm_mgr is None and self.auth:
            from core.alarms import AlarmManager

            self._alarm_mgr = AlarmManager(
                self.auth, self.config, self.state_machine, self.cache_service
            )
            logger.debug("AlarmManager chargé")
        return self._alarm_mgr

    @property
    def reminder_mgr(self):
        """Gestionnaire de rappels (lazy-loaded)."""
        if self._reminder_mgr is None and self.auth:
            from core.reminders import ReminderManager

            self._reminder_mgr = ReminderManager(
                self.auth, self.config, self.state_machine, self.cache_service
            )
            logger.debug("ReminderManager chargé")
        return self._reminder_mgr

    @property
    def light_ctrl(self):
        """Contrôleur de lumières (lazy-loaded)."""
        if self._light_ctrl is None and self.auth:
            from core.smart_home import LightController

            self._light_ctrl = LightController(self.auth, self.config, self.state_machine)
            logger.debug("LightController chargé")
        return self._light_ctrl

    @property
    def thermostat_ctrl(self):
        """Contrôleur de thermostats (lazy-loaded)."""
        if self._thermostat_ctrl is None and self.auth:
            from core.smart_home import ThermostatController

            self._thermostat_ctrl = ThermostatController(self.auth, self.config, self.state_machine)
            logger.debug("ThermostatController chargé")
        return self._thermostat_ctrl

    @property
    def smarthome_ctrl(self):
        """Contrôleur smart home général (lazy-loaded)."""
        if self._smarthome_ctrl is None and self.auth:
            from core.smart_home import SmartDeviceController

            self._smarthome_ctrl = SmartDeviceController(self.auth, self.config, self.state_machine)
            logger.debug("SmartDeviceController chargé")
        return self._smarthome_ctrl

    @property
    def device_ctrl(self):
        """Alias pour smarthome_ctrl (compatibilité commandes)."""
        return self.smarthome_ctrl

    @property
    def playback_mgr(self):
        """Gestionnaire de playback musique (lazy-loaded)."""
        if self._playback_mgr is None and self.auth:
            from core.music import PlaybackManager

            self._playback_mgr = PlaybackManager(self.auth, self.config, self.state_machine)
            logger.debug("PlaybackManager chargé")
        return self._playback_mgr

    @property
    def tunein_mgr(self):
        """Gestionnaire TuneIn (lazy-loaded)."""
        if self._tunein_mgr is None and self.auth:
            from core.music import TuneInManager

            self._tunein_mgr = TuneInManager(self.auth, self.state_machine)
            logger.debug("TuneInManager chargé")
        return self._tunein_mgr

    @property
    def library_mgr(self):
        """Gestionnaire de bibliothèque musicale (lazy-loaded)."""
        if self._library_mgr is None and self.auth:
            from core.music import LibraryManager

            self._library_mgr = LibraryManager(
                self.auth, self.config, self.state_machine, self.voice_service
            )
            logger.debug("LibraryManager chargé")
        return self._library_mgr

    @property
    def music_library(self):
        """
        Service de bibliothèque musicale (lazy-loaded).

        Service implémentant les API Alexa identiques au script shell:
        - TuneIn radio (/api/tunein/queue-and-play)
        - Pistes bibliothèque (/api/cloudplayer/queue-and-play)
        - Playlists Prime Music (/api/prime/prime-playlists)
        - Stations Prime Music (/api/prime/prime-sections)
        - File d'attente historique (/api/entertainment/v1/player/queue)

        Returns:
            MusicLibraryService instance ou None si pas authentifié
        """
        if self._music_library is None and self.auth:
            from services.music_library import MusicLibraryService

            self._music_library = MusicLibraryService(self.auth, self.config, self.breaker)
            logger.debug("MusicLibraryService chargé (shell script parity)")
        return self._music_library

    @property
    def notification_mgr(self):
        """Gestionnaire de notifications (lazy-loaded)."""
        if self._notification_mgr is None and self.auth:
            from core.notification_manager import NotificationManager

            self._notification_mgr = NotificationManager(self.auth, self.state_machine)
            logger.debug("NotificationManager chargé")
        return self._notification_mgr

    @property
    def dnd_mgr(self):
        """Gestionnaire Do Not Disturb (lazy-loaded)."""
        if self._dnd_mgr is None and self.auth:
            from core.dnd_manager import DNDManager

            self._dnd_mgr = DNDManager(self.auth, self.state_machine)
            logger.debug("DNDManager chargé")
        return self._dnd_mgr

    @property
    def activity_mgr(self):
        """Gestionnaire d'activités (lazy-loaded)."""
        if self._activity_mgr is None and self.auth:
            from core.activity_manager import ActivityManager

            self._activity_mgr = ActivityManager(self.auth, self.config, self.state_machine)
            logger.debug("ActivityManager chargé")
        return self._activity_mgr

    @property
    def announcement_mgr(self):
        """Gestionnaire d'annonces (lazy-loaded)."""
        if self._announcement_mgr is None and self.auth:
            from core.communication import AnnouncementManager

            self._announcement_mgr = AnnouncementManager(self.auth, self.config, self.state_machine)
            logger.debug("AnnouncementManager chargé")
        return self._announcement_mgr

    @property
    def calendar_manager(self):
        """Gestionnaire de calendrier (lazy-loaded)."""
        if self._calendar_mgr is None and self.auth:
            from core.calendar import CalendarManager

            self._calendar_mgr = CalendarManager(
                self.auth,
                config=self.config,
                voice_service=self.voice_service,
                device_manager=self.device_mgr
            )
            logger.debug("CalendarManager chargé")
        return self._calendar_mgr

    @property
    def routine_mgr(self):
        """Gestionnaire de routines (lazy-loaded)."""
        if self._routine_mgr is None and self.auth:
            from core.routines import RoutineManager

            self._routine_mgr = RoutineManager(
                self.auth, self.config, self.state_machine, self.cache_service
            )
            logger.debug("RoutineManager chargé")
        return self._routine_mgr

    @property
    def list_mgr(self):
        """Gestionnaire de listes (lazy-loaded)."""
        if self._list_mgr is None and self.auth:
            from core.lists.lists_manager import ListsManager

            self._list_mgr = ListsManager(self.auth, self.config, self.state_machine)
            logger.debug("ListsManager chargé")
        return self._list_mgr

    @property
    def equalizer_mgr(self):
        """Gestionnaire égaliseur (lazy-loaded)."""
        if self._equalizer_mgr is None and self.auth:
            from core.audio import EqualizerManager

            self._equalizer_mgr = EqualizerManager(self.auth, self.state_machine)
            logger.debug("EqualizerManager chargé")
        return self._equalizer_mgr

    @property
    def bluetooth_mgr(self):
        """Gestionnaire Bluetooth (lazy-loaded)."""
        if self._bluetooth_mgr is None and self.auth:
            from core.audio import BluetoothManager

            self._bluetooth_mgr = BluetoothManager(self.auth, self.state_machine)
            logger.debug("BluetoothManager chargé")
        return self._bluetooth_mgr

    @property
    def device_settings_mgr(self):
        """Gestionnaire paramètres appareils (lazy-loaded)."""
        if self._device_settings_mgr is None and self.auth:
            from core.settings import DeviceSettingsManager

            self._device_settings_mgr = DeviceSettingsManager(
                self.auth, self.config, self.state_machine
            )
            logger.debug("DeviceSettingsManager chargé")
        return self._device_settings_mgr

    @property
    def settings_mgr(self):
        """Alias pour device_settings_mgr (compatibilité commandes)."""
        return self.device_settings_mgr

    @property
    def sync_service(self):
        """Service de synchronisation (lazy-loaded)."""
        if self._sync_service is None and self.auth:
            from services.sync_service import SyncService

            self._sync_service = SyncService(self.auth, self.config, self.state_machine)
            logger.debug("SyncService chargé")
        return self._sync_service

    @property
    def voice_service(self):
        """
        Service de commandes vocales (lazy-loaded).

        Permet d'envoyer des commandes textuelles qui sont interprétées
        comme des commandes vocales par Alexa (ex: "règle un timer de 5 minutes").

        Note: VoiceCommandService est la solution universelle pour créer/modifier
              des ressources Alexa quand l'API directe est bloquée (405, etc.)

        Returns:
            VoiceCommandService instance ou None si pas authentifié
        """
        if self._voice_service is None and self.auth:
            from services.voice_command_service import VoiceCommandService

            self._voice_service = VoiceCommandService(self.auth, self.config, self.state_machine)
            logger.debug("VoiceCommandService chargé")
        return self._voice_service

    # ========================================================================
    # MÉTHODES UTILITAIRES
    # ========================================================================

    def initialize_auth(self, auth_instance):
        """
        Initialise l'authentification et lance la synchronisation initiale.

        Args:
            auth_instance: Instance de AlexaAuth
        """
        self.auth = auth_instance
        logger.info("Initialisation de l'authentification dans le contexte")
        logger.success("Authentification initialisée dans le contexte")

        # Lancer synchronisation automatique
        if self.sync_service:
            try:
                logger.info("Lancement de la synchronisation initiale (appareils uniquement)")
                stats = self.sync_service.sync_devices_only()
                total = sum(stats.get("synced", {}).values())
                logger.success(f"Synchronisation appareils terminée: {total} éléments en cache")
            except Exception as e:
                logger.warning(f"⚠️  Erreur synchronisation initiale: {e}")

    def cleanup(self):
        """Nettoie les ressources (appelé à la fermeture)."""
        logger.debug("Nettoyage du contexte")

        # Transition state machine vers DISCONNECTED
        if self.state_machine:
            try:
                # La state machine n'a pas de méthode disconnect, on passe juste au nettoyage
                pass
            except Exception as e:
                logger.warning(f"Erreur lors de la déconnexion state machine: {e}")

        # Reset managers
        self._device_mgr_instance = None
        self._timer_mgr = None
        self._alarm_mgr = None
        self._reminder_mgr = None
        self._light_ctrl = None
        self._thermostat_ctrl = None
        self._smarthome_ctrl = None
        self._playback_mgr = None
        self._tunein_mgr = None
        self._library_mgr = None
        self._music_library = None
        self._notification_mgr = None
        self._dnd_mgr = None
        self._activity_mgr = None
        self._announcement_mgr = None
        self._calendar_mgr = None
        self._equalizer_mgr = None
        self._bluetooth_mgr = None
        self._device_settings_mgr = None

        logger.info("Nettoyage du contexte")
        logger.success("Contexte nettoyé")

    def __enter__(self):
        """Support context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager (cleanup automatique)."""
        self.cleanup()
        return False


# Factory function
def create_context(config_file: Optional[Path] = None) -> Context:
    """
    Crée un nouveau contexte.

    Args:
        config_file: Fichier de configuration personnalisé

    Returns:
        Instance de Context configurée

    Example:
        >>> context = create_context()
        >>> context.initialize_auth(auth)
        >>> context.state_machine.connect()
    """
    return Context(config_file=config_file)
