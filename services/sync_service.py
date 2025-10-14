"""
Service de synchronisation pour récupérer et mettre en cache toutes les données Alexa.

Ce service récupère en une seule fois après l'authentification:
- Appareils Alexa (devices)
- Smart Home devices (lumières, prises, thermostats, etc.)
- Routines
- Listes de courses/tâches
- Playlists musicales
- Stations TuneIn favorites
- Contacts/groupes multiroom
- Rappels actifs
- Historique d'activité récent

Auteur: M@nu
Date: 7 octobre 2025
"""

import time
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

from services.cache_service import CacheService

logger = get_logger("sync_service")


class SyncService:
    """
    Service de synchronisation lazy des données Alexa.

    Charge uniquement les appareils au démarrage pour une réactivité optimale.
    Les autres données (smart home, routines, listes, etc.) sont chargées
    à la demande (lazy loading) quand elles sont nécessaires.

    Attributes:
        auth: Instance AlexaAuth
        config: Configuration
        cache_service: Service de cache
        state_machine: Machine à états
        _lazy_loaded: Dictionnaire des données déjà chargées
    """

    def __init__(self, auth, config, state_machine, cache_service: Optional[CacheService] = None):
        """
        Initialise le service de synchronisation.

        Args:
            auth: AlexaAuth instance
            config: Config instance
            state_machine: AlexaStateMachine instance
            cache_service: CacheService (optionnel, créé si None)
        """
        self.auth = auth
        self.config = config
        self.state_machine = state_machine
        self.cache_service = cache_service or CacheService()

        # Statistiques de sync
        self.last_sync_time = 0.0
        self.sync_stats = {}

        # Suivi du chargement lazy
        self._lazy_loaded = {
            "devices": False,
            "smart_home": False,
            "alarms_and_reminders": False,
            "lists": False,
            "routines": False,
            "activities": False,
        }

        logger.info("Initialisation du SyncService (lazy loading activé)")
        logger.success("SyncService initialisé (lazy loading activé)")

    def sync_devices_only(self, force: bool = False) -> Dict[str, Any]:
        """
        Synchronise uniquement les appareils Alexa au démarrage.

        Cette méthode est appelée au démarrage pour charger rapidement
        les appareils essentiels. Les autres données sont chargées
        à la demande via les getters lazy.

        Args:
            force: Forcer la sync même si cache valide

        Returns:
            Dict avec statistiques de synchronisation
        """
        if not self.state_machine.can_execute_commands:
            logger.warning("⚠️  State machine non connectée, sync impossible")
            return {"success": False, "error": "not_connected"}

        start_time = time.time()
        stats = {
            "success": True,
            "timestamp": start_time,
            "synced": {},
            "failed": [],
        }

        logger.info("Démarrage de la synchronisation des appareils (lazy loading)")
        logger.success("Démarrage synchronisation des appareils (lazy loading)...")

        # 1. Devices Alexa uniquement
        try:
            devices = self._sync_alexa_devices()
            stats["synced"]["devices"] = len(devices)
            self._lazy_loaded["devices"] = True
            logger.success(f"{len(devices)} appareils Alexa synchronisés")
        except Exception as e:
            logger.error(f"❌ Erreur sync devices: {e}")
            stats["failed"].append({"category": "devices", "error": str(e)})

        # Sauvegarder les stats
        duration = time.time() - start_time
        stats["duration_seconds"] = round(duration, 2)
        self.last_sync_time = time.time()
        self.sync_stats = stats

        # Sauvegarder les stats dans le cache
        self.cache_service.set("sync_stats", stats, ttl_seconds=86400)  # 24h

        total_synced = sum(stats["synced"].values())
        logger.success(
            f"Synchronisation appareils terminée: {total_synced} éléments en {duration:.1f}s"
        )

        return stats

    def sync_all(self, force: bool = False) -> Dict[str, Any]:
        """
        Synchronise toutes les données Alexa (méthode legacy).

        Cette méthode est maintenue pour compatibilité mais utilise
        désormais le chargement lazy. Elle force le chargement de
        toutes les données non encore chargées.

        Args:
            force: Forcer la sync même si cache valide

        Returns:
            Dict avec statistiques de synchronisation
        """
        logger.info("🔄 Synchronisation complète demandée (lazy loading activé)...")

        # Forcer le chargement de toutes les données
        self.get_smart_home_devices(force=force)
        self.get_alarms_reminders(force=force)
        self.get_lists(force=force)
        self.get_routines(force=force)
        self.get_activities(force=force)

        # Retourner les stats globales
        return self.get_sync_stats()

    # ===== GETTERS LAZY =====

    def get_smart_home_devices(self, force: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les smart home devices (lazy loading).

        Charge les données depuis le cache ou l'API si nécessaire.

        Args:
            force: Forcer le refresh depuis l'API

        Returns:
            Liste des smart home devices
        """
        if not force and self._lazy_loaded["smart_home"]:
            # Récupérer depuis le cache
            cached = self.cache_service.get("smart_home_all")
            if cached and "devices" in cached:
                return cached["devices"]

        # Charger depuis l'API
        try:
            devices = self._sync_smart_home_devices()
            self._lazy_loaded["smart_home"] = True
            logger.debug(f"Lazy loaded: {len(devices)} smart home devices")
            return devices
        except Exception as e:
            logger.error(f"Erreur lazy loading smart home: {e}")
            return []

    def get_alarms_reminders(self, force: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les alarmes et rappels (lazy loading).

        Args:
            force: Forcer le refresh depuis l'API

        Returns:
            Liste des alarmes et rappels
        """
        if not force and self._lazy_loaded["alarms_and_reminders"]:
            cached = self.cache_service.get("alarms_and_reminders")
            if cached and "notifications" in cached:
                return cached["notifications"]

        try:
            notifications = self._sync_notifications()
            self._lazy_loaded["alarms_and_reminders"] = True
            logger.debug(f"Lazy loaded: {len(notifications)} alarmes et rappels")
            return notifications
        except Exception as e:
            logger.error(f"Erreur lazy loading alarmes et rappels: {e}")
            return []

    def get_lists(self, force: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les listes (courses, tâches) (lazy loading).

        Args:
            force: Forcer le refresh depuis l'API

        Returns:
            Liste des listes
        """
        if not force and self._lazy_loaded["lists"]:
            cached = self.cache_service.get("lists")
            if cached and "lists" in cached:
                return cached["lists"]

        try:
            lists = self._sync_lists()
            self._lazy_loaded["lists"] = True
            logger.debug(f"Lazy loaded: {len(lists)} listes")
            return lists
        except Exception as e:
            logger.error(f"Erreur lazy loading listes: {e}")
            return []

    def get_routines(self, force: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les routines (lazy loading).

        Args:
            force: Forcer le refresh depuis l'API

        Returns:
            Liste des routines
        """
        if not force and self._lazy_loaded["routines"]:
            cached = self.cache_service.get("routines")
            if cached and "routines" in cached:
                return cached["routines"]

        try:
            routines = self._sync_routines()
            self._lazy_loaded["routines"] = True
            logger.debug(f"Lazy loaded: {len(routines)} routines")
            return routines
        except Exception as e:
            logger.error(f"Erreur lazy loading routines: {e}")
            return []

    def get_activities(self, force: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les activités récentes (lazy loading).

        Args:
            force: Forcer le refresh depuis l'API
            limit: Nombre maximum d'activités à récupérer

        Returns:
            Liste des activités
        """
        if not force and self._lazy_loaded["activities"]:
            cached = self.cache_service.get("activities")
            if cached and "activities" in cached:
                return cached["activities"]

        try:
            activities = self._sync_activities(limit)
            self._lazy_loaded["activities"] = True
            logger.debug(f"Lazy loaded: {len(activities)} activités")
            return activities
        except Exception as e:
            logger.error(f"Erreur lazy loading activités: {e}")
            return []

    def get_lazy_loading_status(self) -> Dict[str, bool]:
        """
        Retourne l'état du chargement lazy pour chaque catégorie.

        Returns:
            Dictionnaire avec l'état de chargement pour chaque catégorie
        """
        return self._lazy_loaded.copy()

    def preload_all_data(self, force: bool = False) -> Dict[str, Any]:
        """
        Précharge toutes les données (équivalent à l'ancienne sync_all).

        Utile pour les opérations qui nécessitent toutes les données.

        Args:
            force: Forcer le refresh de toutes les données

        Returns:
            Statistiques de préchargement
        """
        logger.info("🔄 Préchargement de toutes les données...")

        start_time = time.time()
        stats = {
            "success": True,
            "timestamp": start_time,
            "preloaded": {},
            "failed": [],
        }

        # Précharger toutes les catégories
        categories = [
            ("smart_home", self.get_smart_home_devices),
            ("alarms_and_reminders", self.get_alarms_reminders),
            ("lists", self.get_lists),
            ("routines", self.get_routines),
            ("activities", self.get_activities),
        ]

        for category, getter in categories:
            try:
                data = getter(force=force)
                stats["preloaded"][category] = len(data)
                logger.debug(f"✅ {len(data)} {category} préchargés")
            except Exception as e:
                logger.error(f"❌ Erreur préchargement {category}: {e}")
                stats["failed"].append({"category": category, "error": str(e)})

        duration = time.time() - start_time
        stats["duration_seconds"] = round(duration, 2)

        total_preloaded = sum(stats["preloaded"].values())
        logger.success(f"🎉 Préchargement terminé: {total_preloaded} éléments en {duration:.1f}s")

        return stats

    def _sync_alexa_devices(self) -> List[Dict[str, Any]]:
        """Synchronise les appareils Alexa."""
        try:
            response = self.auth.session.get(
                f"https://{self.config.alexa_domain}/api/devices-v2/device",
                headers={"csrf": self.auth.csrf},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            devices = data.get("devices", [])

            # Sauvegarder dans cache
            self.cache_service.set("devices", {"devices": devices}, ttl_seconds=3600)  # 1h

            return devices
        except Exception as e:
            logger.error(f"Erreur récupération devices Alexa: {e}")
            return []

    def _sync_smart_home_devices(self) -> List[Dict[str, Any]]:
        """Synchronise les smart home devices."""
        try:
            response = self.auth.session.get(
                f"https://{self.config.alexa_domain}/api/behaviors/entities?skillId=amzn1.ask.1p.smarthome",
                headers={
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                },
                timeout=10,
            )
            response.raise_for_status()
            devices = response.json()

            # Sauvegarder UNIQUEMENT le fichier global
            # Le tri par catégorie se fera à la demande par les controllers
            self.cache_service.set(
                "smart_home_all", {"devices": devices}, ttl_seconds=1800
            )  # 30min

            return devices
        except Exception as e:
            logger.error(f"Erreur récupération smart home: {e}")
            return []

    def _sync_notifications(self) -> List[Dict[str, Any]]:
        """Synchronise les alarmes et rappels."""
        try:
            response = self.auth.session.get(
                f"https://{self.config.alexa_domain}/api/notifications",
                headers={"csrf": self.auth.csrf},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            notifications = data.get("notifications", [])

            # Sauvegarder dans cache
            self.cache_service.set(
                "alarms_and_reminders", {"notifications": notifications}, ttl_seconds=600
            )  # 10min

            return notifications
        except Exception as e:
            logger.error(f"Erreur récupération alarmes et rappels: {e}")
            return []

    def _sync_lists(self) -> List[Dict[str, Any]]:
        """
        Synchronise les listes (courses, tâches).

        Note: L'endpoint /api/namedLists retourne 503 (Service Temporarily Unavailable).
        Cette méthode retourne une liste vide pour éviter les erreurs.
        """
        logger.debug("Synchronisation listes: service temporairement indisponible (503), ignoré")
        # L'endpoint /api/namedLists retourne 503, service temporairement indisponible
        # Retourner une liste vide pour éviter l'erreur
        return []

    def _sync_routines(self) -> List[Dict[str, Any]]:
        """Synchronise les routines Alexa."""
        try:
            response = self.auth.session.get(
                f"https://{self.config.alexa_domain}/api/behaviors/v2/automations",
                headers={"csrf": self.auth.csrf},
                timeout=15,
            )
            response.raise_for_status()
            routines = response.json()

            # Vérifier si c'est une liste ou un dict
            if isinstance(routines, dict):
                routines = routines.get("routines", [])
            elif not isinstance(routines, list):
                routines = []

            # Sauvegarder dans cache
            self.cache_service.set("routines", {"routines": routines}, ttl_seconds=3600)  # 1h

            return routines
        except Exception as e:
            logger.error(f"Erreur récupération routines: {e}")
            return []

    def _sync_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Synchronise les activités récentes.

        Note: L'endpoint /api/activities semble ne plus être disponible (404).
        Cette méthode retourne une liste vide pour éviter les erreurs.
        """
        logger.debug("Synchronisation activités: endpoint non disponible (404), ignoré")
        # L'endpoint /api/activities retourne 404, probablement supprimé par Amazon
        # Retourner une liste vide pour éviter l'erreur
        return []

    def get_sync_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la dernière sync."""
        return self.sync_stats

    def is_cache_valid(self, max_age_seconds: int = 3600) -> bool:
        """Vérifie si le cache est encore valide."""
        if self.last_sync_time == 0:
            return False
        age = time.time() - self.last_sync_time
        return age < max_age_seconds
