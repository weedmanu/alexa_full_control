"""
Service de gestion de la bibliothèque musicale Amazon.

Gère les playlists, achats, importations, Prime Music, TuneIn.

Auteur: M@nu
Date: 8 octobre 2025
"""

import base64
import json
from threading import RLock
from typing import Any, Dict, List, Optional

from pybreaker import CircuitBreaker

from config import Config
from services.auth import AuthenticationService
from utils.logger import SharedIcons, setup_loguru_logger

# Configuration du logger Loguru pour ce service
logger = setup_loguru_logger(
    level="INFO",
    custom_levels=["MUSIC"]
)


class MusicLibraryService:
    """Service de gestion de la bibliothèque musicale."""

    def __init__(
        self,
        auth: AuthenticationService,
        config: Config,
        breaker: Optional[CircuitBreaker] = None,
    ):
        """
        Initialise le service.

        Args:
            auth: Service d'authentification
            config: Configuration
            breaker: Circuit breaker pour la résilience
        """
        self.auth = auth
        self.config = config
        self.breaker = breaker or CircuitBreaker(fail_max=3, reset_timeout=60)
        self._lock = RLock()

    def play_tunein_radio(self, device_serial: str, device_type: str, station_id: str) -> bool:
        """
        Joue une station TuneIn radio.

        Args:
            device_serial: Numéro de série de l'appareil
            device_type: Type d'appareil
            station_id: ID de la station TuneIn

        Returns:
            True si succès
        """
        with self._lock:
            logger.debug(f"{SharedIcons.SEARCH} Préparation lecture TuneIn station {station_id} sur {device_serial}")
            try:
                # Encoder le content token comme le shell script
                content_data = f'["music/tuneIn/stationId","{station_id}"]|{{"previousPageId":"TuneIn_SEARCH"}}'
                content_token = base64.b64encode(
                    base64.b64encode(content_data.encode()).decode().encode()
                ).decode()

                payload = {"contentToken": f"music:{content_token}"}

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                response = self.breaker.call(
                    self.auth.session.put,
                    f"https://{self.config.alexa_domain}/api/entertainment/v1/player/queue",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                    },
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                response.raise_for_status()
                logger.success(f"{SharedIcons.SUCCESS} Station TuneIn {station_id} lancée sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture TuneIn station {station_id}: {e}")
                return False

    def play_library_track(
        self,
        device_serial: str,
        device_type: str,
        media_owner_id: str,
        track_id: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        shuffle: bool = False,
    ) -> bool:
        """
        Joue un morceau de la bibliothèque.

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média
            track_id: ID du morceau (ou None pour album)
            artist: Nom de l'artiste (si album)
            album: Nom de l'album (si album)
            shuffle: Mode aléatoire

        Returns:
            True si succès
        """
        with self._lock:
            logger.debug(f"{SharedIcons.SEARCH} Préparation lecture bibliothèque sur {device_serial}")
            try:
                # Payload différent selon track_id ou album
                if track_id:
                    payload = {"trackId": track_id, "playQueuePrime": True}
                    logger.debug(f"{SharedIcons.FILE} Lecture morceau {track_id}")
                elif artist and album:
                    payload = {"albumArtistName": artist, "albumName": album}
                    logger.debug(f"{SharedIcons.FILE} Lecture album '{album}' de {artist}")
                else:
                    logger.error(f"{SharedIcons.ERROR} track_id ou (artist+album) requis pour la lecture")
                    return False

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/cloudplayer/queue-and-play",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                        "shuffle": "true" if shuffle else "false",
                    },
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                response.raise_for_status()
                if shuffle:
                    logger.success(f"{SharedIcons.SUCCESS} Morceau bibliothèque lancé (shuffle activé) sur {device_serial}")
                else:
                    logger.success(f"{SharedIcons.SUCCESS} Morceau bibliothèque lancé sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture bibliothèque: {e}")
                return False

    def play_library_playlist(
        self,
        device_serial: str,
        device_type: str,
        media_owner_id: str,
        playlist_id: str,
        shuffle: bool = False,
    ) -> bool:
        """
        Joue une playlist de la bibliothèque.

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média
            playlist_id: ID de la playlist
            shuffle: Mode aléatoire

        Returns:
            True si succès
        """
        with self._lock:
            logger.debug(f"{SharedIcons.SEARCH} Préparation lecture playlist {playlist_id} sur {device_serial}")
            try:
                payload = {"playlistId": playlist_id, "playQueuePrime": True}

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/cloudplayer/queue-and-play",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                        "shuffle": "true" if shuffle else "false",
                    },
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                response.raise_for_status()
                if shuffle:
                    logger.success(f"{SharedIcons.SUCCESS} Playlist {playlist_id} lancée (shuffle activé) sur {device_serial}")
                else:
                    logger.success(f"{SharedIcons.SUCCESS} Playlist {playlist_id} lancée sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture playlist {playlist_id}: {e}")
                return False

    def play_prime_playlist(
        self, device_serial: str, device_type: str, media_owner_id: str, asin: str
    ) -> bool:
        """
        Joue une playlist Prime Music (ASIN).

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média
            asin: ASIN de la playlist Prime

        Returns:
            True si succès
        """
        with self._lock:
            logger.debug(f"{SharedIcons.SEARCH} Préparation lecture playlist Prime {asin} sur {device_serial}")
            try:
                payload = {"asin": asin}

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/prime/prime-playlist-queue-and-play",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                    },
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                response.raise_for_status()
                logger.success(f"{SharedIcons.SUCCESS} Playlist Prime {asin} lancée sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture Prime playlist {asin}: {e}")
                return False

    def play_prime_station(
        self, device_serial: str, device_type: str, media_owner_id: str, seed_id: str
    ) -> bool:
        """
        Joue une station Prime Music (seedID).

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média
            seed_id: Seed ID de la station Prime

        Returns:
            True si succès
        """
        with self._lock:
            logger.debug(f"{SharedIcons.SEARCH} Préparation lecture station Prime {seed_id} sur {device_serial}")
            try:
                # Format du seed comme le shell script
                seed_data = {"type": "KEY", "seedId": seed_id}
                payload = {
                    "seed": json.dumps(seed_data),
                    "stationName": "none",
                    "seedType": "KEY",
                }

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/gotham/queue-and-play",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                    },
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                response.raise_for_status()
                logger.success(f"{SharedIcons.SUCCESS} Station Prime {seed_id} lancée sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture Prime station {seed_id}: {e}")
                return False

    def play_historical_queue(
        self,
        device_serial: str,
        device_type: str,
        media_owner_id: str,
        queue_id: str,
    ) -> bool:
        """
        Rejoue une file d'attente historique Prime.

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média
            queue_id: ID de la queue historique

        Returns:
            True si succès
        """
        with self._lock:
            logger.debug(f"{SharedIcons.SEARCH} Préparation lecture queue historique {queue_id} sur {device_serial}")
            try:
                payload = {
                    "deviceType": device_type,
                    "deviceSerialNumber": device_serial,
                    "mediaOwnerCustomerId": media_owner_id,
                    "queueId": queue_id,
                    "service": None,
                    "trackSource": "TRACK",
                }

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                response = self.breaker.call(
                    self.auth.session.post,
                    f"https://{self.config.alexa_domain}/api/media/play-historical-queue",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                response.raise_for_status()
                logger.success(f"{SharedIcons.SUCCESS} Queue historique {queue_id} lancée sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture queue historique {queue_id}: {e}")
                return False

    def get_library_playlists(
        self,
        device_serial: str,
        device_type: str,
        media_owner_id: str,
        playlist_type: str = "cloudplayer",
    ) -> List[Dict[str, Any]]:
        """
        Récupère les playlists de la bibliothèque.

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média
            playlist_type: Type (cloudplayer, imported, purchased)

        Returns:
            Liste des playlists
        """
        with self._lock:
            try:
                all_tracks = []
                offset = 0
                size = 50

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                while True:
                    response = self.breaker.call(
                        self.auth.session.get,
                        f"https://{self.config.alexa_domain}/api/cloudplayer/playlists/{playlist_type}-V0-OBJECTID",
                        params={
                            "deviceSerialNumber": device_serial,
                            "deviceType": device_type,
                            "mediaOwnerCustomerId": media_owner_id,
                            "size": size,
                            "offset": offset,
                        },
                        headers=headers,
                        timeout=15,
                    )

                    response.raise_for_status()
                    data = response.json()

                    playlist = data.get("playlist", {})
                    entries = playlist.get("entryList", [])

                    if not entries:
                        break

                    all_tracks.extend(entries)

                    # Vérifier s'il y a plus de résultats
                    next_token = data.get("nextResultsToken")
                    if not next_token or len(entries) < size:
                        break

                    offset = next_token

                logger.success(f"{SharedIcons.SUCCESS} {len(all_tracks)} entrées bibliothèque récupérées")
                return all_tracks

            except Exception as e:
                logger.error(f"Erreur récupération bibliothèque: {e}")
                return []

    def get_prime_playlists(
        self, device_serial: str, device_type: str, media_owner_id: str
    ) -> List[Dict[str, Any]]:
        """
        Récupère les playlists Prime Music.

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média

        Returns:
            Liste des playlists Prime
        """
        with self._lock:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                # Récupérer les browse nodes
                response = self.breaker.call(
                    self.auth.session.get,
                    f"https://{self.config.alexa_domain}/api/prime/prime-playlist-browse-nodes",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                    },
                    headers=headers,
                    timeout=15,
                )

                response.raise_for_status()
                data = response.json()

                all_playlists = []

                # Pour chaque browse node, récupérer les playlists
                for browse_node in data.get("primePlaylistBrowseNodeList", []):
                    for sub_node in browse_node.get("subNodes", []):
                        node_id = sub_node.get("nodeId")
                        if not node_id:
                            continue

                        pl_response = self.breaker.call(
                            self.auth.session.get,
                            f"https://{self.config.alexa_domain}/api/prime/prime-playlists-by-browse-node",
                            params={
                                "browseNodeId": node_id,
                                "deviceSerialNumber": device_serial,
                                "deviceType": device_type,
                                "mediaOwnerCustomerId": media_owner_id,
                            },
                            headers=headers,
                            timeout=15,
                        )

                        pl_response.raise_for_status()
                        pl_data = pl_response.json()
                        all_playlists.extend(pl_data.get("playlists", []))

                logger.success(f"{SharedIcons.SUCCESS} {len(all_playlists)} playlists Prime récupérées")
                return all_playlists

            except Exception as e:
                logger.error(f"Erreur récupération Prime playlists: {e}")
                return []

    def get_prime_stations(
        self, device_serial: str, device_type: str, media_owner_id: str
    ) -> List[Dict[str, Any]]:
        """
        Récupère les stations Prime Music.

        Args:
            device_serial: Numéro de série
            device_type: Type d'appareil
            media_owner_id: ID propriétaire média

        Returns:
            Liste des stations Prime
        """
        with self._lock:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "Referer": f"https://alexa.{self.config.amazon_domain}/spa/index.html",
                    "Origin": f"https://alexa.{self.config.amazon_domain}",
                    "csrf": self.auth.csrf,
                }

                response = self.breaker.call(
                    self.auth.session.get,
                    f"https://{self.config.alexa_domain}/api/prime/prime-sections",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                    },
                    headers=headers,
                    timeout=15,
                )

                response.raise_for_status()
                data = response.json()

                logger.success(f"{SharedIcons.SUCCESS} Stations Prime récupérées")
                return data.get("primeMusicSections", [])

            except Exception as e:
                logger.error(f"Erreur récupération Prime stations: {e}")
                return []
