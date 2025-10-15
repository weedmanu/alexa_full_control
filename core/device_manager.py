"""
Gestionnaire des appareils Alexa.

Ce module gère toutes les opérations liées aux appareils Amazon Alexa :
- Récupération de la liste des appareils
- Informations détaillées sur un appareil
- Recherche d'appareils par nom
- Gestion du cache multi-niveaux (mémoire + disque)

Le DeviceManager maintient un cache hybride pour optimiser les performances :
- Niveau 1 : Cache mémoire (rapide, volatile)
- Niveau 2 : Cache disque persistant (survit aux redémarrages)

Auteur: M@nu
Date: 7 octobre 2025
"""

import time
from threading import RLock
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from loguru import logger

from services.cache_service import CacheService

if TYPE_CHECKING:
    from alexa_auth.alexa_auth import AlexaAuth
    from core.state_machine import AlexaStateMachine


class DeviceManager:
    """
    Gestionnaire des appareils Alexa.

    Gère la liste des appareils, leur cache, et les opérations de recherche.

    Attributes:
        auth: Gestionnaire d'authentification AlexaAuth
        state_machine: Machine d'états AlexaStateMachine
        _devices_cache: Cache des appareils (thread-safe)
        _cache_timestamp: Timestamp du dernier refresh du cache
        _cache_ttl: Durée de vie du cache en secondes (défaut: 300s = 5min)
        _lock: Verrou pour accès thread-safe au cache

    Example:
        >>> device_mgr = DeviceManager(auth, state_machine)
        >>> devices = device_mgr.get_devices()
        >>> for device in devices:
        ...     print(f"{device['accountName']}: {device['online']}")
        >>> salon = device_mgr.find_device_by_name("Salon")
        >>> print(f"Serial: {salon['serialNumber']}")
    """

    def __init__(
        self,
        auth: "AlexaAuth",
        state_machine: "AlexaStateMachine",
        cache_ttl: int = 300,
        cache_service: Optional[CacheService] = None,
    ):
        """
        Initialise le gestionnaire d'appareils.

        Args:
            auth: Instance AlexaAuth pour les appels API
            state_machine: Instance AlexaStateMachine pour gérer l'état
            cache_ttl: Durée de vie du cache mémoire en secondes (défaut: 300)
            cache_service: Service de cache persistant (créé si None)

        Raises:
            ValueError: Si auth ou state_machine est None
        """
        if not auth:
            raise ValueError("auth ne peut pas être None")
        if not state_machine:
            raise ValueError("state_machine ne peut pas être None")

        self.auth: AlexaAuth = auth
        self.state_machine: AlexaStateMachine = state_machine
        self._cache_ttl = cache_ttl
        self._cache_service = cache_service or CacheService()

        # Cache mémoire thread-safe (Niveau 1)
        self._devices_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: float = 0.0
        self._lock: RLock = RLock()

        logger.debug(f"DeviceManager initialisé (cache_ttl={cache_ttl}s)")

    def get_devices(self, force_refresh: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère la liste de tous les appareils Alexa.

        Utilise un cache à 2 niveaux :
        1. Cache mémoire (rapide, TTL 5min)
        2. Cache disque (persistant, SANS TTL - toujours valide)
        3. API Amazon (si cache mémoire expiré ET cache disque absent)

        Le cache disque sert uniquement de fallback lors du démarrage ou après
        un force_refresh. Il n'a pas de durée d'expiration et est mis à jour
        uniquement lors d'un appel API.

        Args:
            force_refresh: Force le refresh du cache (ignore tous les niveaux)

        Returns:
            Liste des appareils ou None en cas d'erreur

        Example:
            >>> devices = device_mgr.get_devices()
            >>> online_devices = [d for d in devices if d.get('online')]
            >>> print(f"{len(online_devices)} appareils en ligne")
        """
        with self._lock:
            # Niveau 1 : Cache mémoire (avec TTL)
            if not force_refresh and self._is_cache_valid() and self._devices_cache is not None:
                logger.debug(f"✅ Cache mémoire: {len(self._devices_cache)} appareils")
                return self._devices_cache

            # Niveau 2 : Cache disque (SANS TTL - toujours valide si présent)
            # Utilisé uniquement si cache mémoire expiré/absent
            if not force_refresh:
                disk_cache = self._cache_service.get("devices", ignore_ttl=True)
                if disk_cache and "devices" in disk_cache:
                    logger.debug(
                        f"💾 Cache disque: {len(disk_cache['devices'])} appareils (fallback)"
                    )
                    self._devices_cache = disk_cache["devices"]
                    self._cache_timestamp = time.time()
                    return self._devices_cache

            # Niveau 3 : API
            return self._refresh_cache()

    def _is_cache_valid(self) -> bool:
        """
        Vérifie si le cache est encore valide.

        Returns:
            True si le cache existe et n'a pas expiré
        """
        if self._devices_cache is None:
            return False

        age = time.time() - self._cache_timestamp
        is_valid = age < self._cache_ttl

        if not is_valid:
            logger.debug(f"Cache expiré (âge: {age:.1f}s, TTL: {self._cache_ttl}s)")

        return is_valid

    def _refresh_cache(self) -> Optional[List[Dict[str, Any]]]:
        """
        Rafraîchit le cache en effectuant un appel API.

        Sauvegarde dans cache mémoire ET cache disque.

        Returns:
            Liste des appareils ou None en cas d'erreur
        """
        try:
            logger.debug("🌐 Récupération de la liste des appareils depuis l'API")

            # Appel API pour récupérer les appareils (type: ignore pour auth qui est Any)
            response = self.auth.get(  # type: ignore[attr-defined]
                f"https://alexa.{self.auth.amazon_domain}/api/devices-v2/device",  # type: ignore[attr-defined]
                params={"cached": "false"},
            )

            if not response or response.status_code != 200:  # type: ignore[attr-defined]
                logger.error(
                    f"Échec de récupération des appareils (status: {response.status_code if response else 'None'})"  # type: ignore[attr-defined]
                )
                return None

            data: Dict[str, Any] = response.json()  # type: ignore[attr-defined]
            devices: List[Dict[str, Any]] = data.get("devices", [])

            # Mise à jour cache mémoire (Niveau 1)
            self._devices_cache = devices
            self._cache_timestamp = time.time()

            # Mise à jour cache disque (Niveau 2) - TTL 1h
            self._cache_service.set("devices", {"devices": devices}, ttl_seconds=3600)

            logger.info(f"✅ {len(devices)} appareils récupérés et mis en cache (mémoire + disque)")
            return devices

        except Exception:
            logger.exception("Erreur lors de la récupération des appareils")
            return None

    def find_device_by_name(self, device_name: str) -> Optional[Dict[str, Any]]:
        """
        Recherche un appareil par son nom (accountName).

        La recherche est insensible à la casse et cherche une correspondance exacte.
        Si aucune correspondance exacte n'est trouvée, cherche une correspondance partielle.

        Args:
            device_name: Nom de l'appareil à rechercher

        Returns:
            Dictionnaire de l'appareil ou None si non trouvé

        Example:
            >>> device = device_mgr.find_device_by_name("Salon")
            >>> if device:
            ...     print(f"Trouvé: {device['deviceType']}")
            ... else:
            ...     print("Appareil non trouvé")
        """
        if not device_name:
            logger.warning("Nom d'appareil vide fourni à find_device_by_name")
            return None

        devices = self.get_devices()
        if not devices:
            logger.warning("Aucun appareil disponible pour la recherche")
            return None

        device_name_lower = device_name.lower()

        # Correspondance exacte (insensible à la casse)
        for device in devices:
            account_name = device.get("accountName", "")
            if account_name.lower() == device_name_lower:
                logger.debug(f"Appareil trouvé (exact): {account_name}")
                return device

        # Correspondance partielle (fallback)
        for device in devices:
            account_name = device.get("accountName", "")
            if device_name_lower in account_name.lower():
                logger.debug(f"Appareil trouvé (partiel): {account_name}")
                return device

        logger.warning(f"Appareil '{device_name}' non trouvé")
        return None

    def find_device_by_serial(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Recherche un appareil par son numéro de série.

        Args:
            serial_number: Numéro de série de l'appareil

        Returns:
            Dictionnaire de l'appareil ou None si non trouvé

        Example:
            >>> device = device_mgr.find_device_by_serial("G091UC0123456789")
            >>> print(device['accountName'] if device else "Non trouvé")
        """
        if not serial_number:
            logger.warning("Serial number vide fourni à find_device_by_serial")
            return None

        devices = self.get_devices()
        if not devices:
            return None

        for device in devices:
            if device.get("serialNumber") == serial_number:
                logger.debug(f"Appareil trouvé par serial: {device.get('accountName')}")
                return device

        logger.warning(f"Appareil avec serial '{serial_number}' non trouvé")
        return None

    def get_device_serial(self, device_name: str) -> Optional[str]:
        """
        Récupère le numéro de série d'un appareil à partir de son nom.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Numéro de série ou None si appareil non trouvé

        Example:
            >>> serial = device_mgr.get_device_serial("Salon")
            >>> print(f"Serial: {serial}")
        """
        device = self.find_device_by_name(device_name)
        if device:
            serial = device.get("serialNumber")
            logger.debug(f"Serial pour '{device_name}': {serial}")
            return serial

        return None

    def get_online_devices(self) -> List[Dict[str, Any]]:
        """
        Récupère uniquement les appareils en ligne.

        Returns:
            Liste des appareils en ligne (peut être vide)

        Example:
            >>> online = device_mgr.get_online_devices()
            >>> print(f"{len(online)} appareils en ligne")
        """
        devices = self.get_devices()
        if not devices:
            return []

        online = [d for d in devices if d.get("online", False)]
        logger.debug(f"{len(online)}/{len(devices)} appareils en ligne")
        return online

    def get_device_info(self, device_name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations complètes d'un appareil.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Dictionnaire avec toutes les infos ou None si non trouvé

        Example:
            >>> info = device_mgr.get_device_info("Salon")
            >>> if info:
            ...     print(f"Type: {info['deviceType']}")
            ...     print(f"Family: {info['deviceFamily']}")
            ...     print(f"Online: {info['online']}")
        """
        return self.find_device_by_name(device_name)

    def invalidate_cache(self) -> None:
        """
        Invalide le cache mémoire ET disque.

        Force le refresh au prochain appel get_devices().

        Example:
            >>> device_mgr.invalidate_cache()
            >>> devices = device_mgr.get_devices()  # Forcera un appel API
        """
        with self._lock:
            self._devices_cache = None
            self._cache_timestamp = 0.0
            self._cache_service.invalidate("devices")
            logger.info("🗑️ Cache appareils invalidé (mémoire + disque)")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur l'état du cache.

        Returns:
            Dictionnaire avec les infos du cache

        Example:
            >>> cache_info = device_mgr.get_cache_info()
            >>> print(f"Devices: {cache_info['device_count']}")
            >>> print(f"Age: {cache_info['age_seconds']:.1f}s")
            >>> print(f"Valid: {cache_info['is_valid']}")
        """
        with self._lock:
            age = time.time() - self._cache_timestamp if self._cache_timestamp > 0 else None

            return {
                "device_count": len(self._devices_cache) if self._devices_cache else 0,
                "is_valid": self._is_cache_valid(),
                "age_seconds": age,
                "ttl_seconds": self._cache_ttl,
                "last_refresh": self._cache_timestamp,
            }

    def __repr__(self) -> str:
        """Représentation du DeviceManager."""
        cache_info = self.get_cache_info()
        return (
            f"DeviceManager(devices={cache_info['device_count']}, "
            f"cache_valid={cache_info['is_valid']}, "
            f"ttl={self._cache_ttl}s)"
        )
