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
from typing import TYPE_CHECKING, Any, Optional

from loguru import logger

from core.circuit_breaker import CircuitBreaker

# Runtime imports
from core.config import Config
from core.state_machine import AlexaStateMachine
from services.cache_service import CacheService
from services.favorite_service import FavoriteService

if TYPE_CHECKING:
    # Importer uniquement pour annotations afin d'éviter cycles d'import
    from alexa_auth.alexa_auth import AlexaAuth
    from core.audio import BluetoothManager, EqualizerManager
    from core.device_manager import DeviceManager
    from core.settings import DeviceSettingsManager
    from services.music_library import MusicLibraryService
    from services.sync_service import SyncService
    from services.voice_command_service import VoiceCommandService


class Context:
    """
    Contexte partagé contenant toutes les ressources nécessaires aux commandes.

    Ce contexte est créé au démarrage de la CLI et injecté dans chaque commande.
    Il centralise:
    - L'authentification (auth)
    - La configuration (config)
    - La state machine (état de connexion)
    - Le circuit breaker (protection API)
    - Les managers audio et paramètres

    Attributes:
        config (Config): Configuration de l'application
        auth: Objet d'authentification AlexaAuth
        state_machine (AlexaStateMachine): Machine à états de connexion
        breaker (CircuitBreaker): Circuit breaker pour protection API

        # Managers de fonctionnalités
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

        # DI container exposure for gradual migration
        self.di_container: Optional[Any] = None

        # Auth et device manager (initialisés à None, créés au login)
        self.auth: Optional[AlexaAuth] = None
        self._sync_service: Optional[SyncService] = None

        # Services additionnels
        self.favorite_service = FavoriteService()  # Service de gestion des favoris

        # Managers de fonctionnalités (lazy-loaded)
        self._equalizer_mgr: Optional[EqualizerManager] = None
        self._bluetooth_mgr: Optional[BluetoothManager] = None
        self._device_settings_mgr: Optional[DeviceSettingsManager] = None
        self._device_mgr_instance: Optional["DeviceManager"] = None  # Gestionnaire d'appareils
        self._voice_service: Optional[VoiceCommandService] = None  # Service de commandes vocales

        logger.debug("Context initialisé")

    # ========================================================================
    # PROPRIÉTÉS LAZY-LOADED POUR LES MANAGERS
    # ========================================================================

    @property
    def device_mgr(self) -> Optional[Any]:
        """Gestionnaire d'appareils (lazy-loaded)."""
        if self._device_mgr_instance is None and self.auth:
            from services.alexa_api_service import AlexaAPIService

            # Utiliser directement AlexaAPIService comme device manager
            self._device_mgr_instance = AlexaAPIService(self.auth, self.cache_service)
            logger.debug("AlexaAPIService chargé comme device_mgr")
        return self._device_mgr_instance

    @property
    def equalizer_mgr(self) -> Optional["EqualizerManager"]:
        """Gestionnaire égaliseur (lazy-loaded)."""
        if self._equalizer_mgr is None and self.auth:
            from core.audio import EqualizerManager

            self._equalizer_mgr = EqualizerManager(self.auth, self.state_machine)
            logger.debug("EqualizerManager chargé")
        return self._equalizer_mgr

    @property
    def bluetooth_mgr(self) -> Optional["BluetoothManager"]:
        """Gestionnaire Bluetooth (lazy-loaded)."""
        if self._bluetooth_mgr is None and self.auth:
            from core.audio import BluetoothManager

            self._bluetooth_mgr = BluetoothManager(self.auth, self.state_machine)
            logger.debug("BluetoothManager chargé")
        return self._bluetooth_mgr

    @property
    def device_settings_mgr(self) -> Optional["DeviceSettingsManager"]:
        """Gestionnaire paramètres appareils (lazy-loaded)."""
        if self._device_settings_mgr is None and self.auth:
            from core.settings import DeviceSettingsManager

            self._device_settings_mgr = DeviceSettingsManager(self.auth, self.config, self.state_machine)
            logger.debug("DeviceSettingsManager chargé")
        return self._device_settings_mgr

    @property
    def settings_mgr(self):
        """Alias pour device_settings_mgr (compatibilité commandes)."""
        return self.device_settings_mgr

    @property
    def sync_service(self):
        """Service de synchronisation (lazy-loaded)."""

        from services.sync_service import SyncService

        if self._sync_service is None and self.auth:
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

    def initialize_auth(self, auth_instance: "AlexaAuth") -> None:
        """
        Initialise l'authentification et lance la synchronisation initiale.

        Args:
            auth_instance: "AlexaAuth"
        """
        self.auth = auth_instance
        logger.info("Authentification initialisée dans le contexte")

        # Lancer synchronisation automatique
        if self.sync_service:
            try:
                logger.info("🔄 Lancement synchronisation initiale (appareils uniquement)...")
                stats = self.sync_service.sync_devices_only()
                total = sum(stats.get("synced", {}).values())
                logger.success(f"✅ Synchronisation appareils terminée: {total} éléments en cache")
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
        self._equalizer_mgr = None
        self._bluetooth_mgr = None
        self._device_settings_mgr = None

        logger.info("Contexte nettoyé")

    def __enter__(self):
        """Support context manager."""
        return self

    def __exit__(self, _exc_type: Optional[type], _exc_val: Optional[BaseException], _exc_tb: Optional[Any]) -> None:
        """Support context manager (cleanup automatique)."""
        self.cleanup()
        # Return None to follow standard __exit__ signature; exceptions won't be suppressed
        return None


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
