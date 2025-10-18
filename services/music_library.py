"""
Service de gestion de la bibliothèque musicale Amazon.

Gère les playlists, achats, importations, Prime Music, TuneIn.

Auteur: M@nu
Date: 8 octobre 2025
"""

import base64
import json
from threading import RLock
from typing import Any, Dict, List, Optional, cast

from loguru import logger
from pybreaker import CircuitBreaker

from core.config import Config
from services.auth import AuthClient
from utils.logger import SharedIcons

# NOTE: Ne pas initialiser le logger ici (au moment de l'import) car cela
# provoquerait l'ajout d'un sink console par défaut lors de l'import de modules
# dans des contextes non-verbeux. L'initialisation doit être faite explicitement
# par l'application principale (`alexa`) via `setup_loguru_logger(enable_console=...)`.

# Common header values to avoid long repeated literals (helps ruff E501)
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 bash-script/1.0"


def _make_headers(auth: Any, config: Config, referer_path: str = "spa/index.html") -> dict[str, str]:
    return {
        "User-Agent": _USER_AGENT,
        "DNT": "1",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=UTF-8",
        "Referer": f"https://alexa.{config.amazon_domain}/{referer_path}",
        "Origin": f"https://alexa.{config.amazon_domain}",
        "csrf": getattr(auth, "csrf", ""),
    }


class MusicLibraryService:
    """Service de gestion de la bibliothèque musicale."""

    def __init__(
        self,
        auth: AuthClient,
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

        # Legacy compatibility: expose http_client-like wrapper
        # Declare attribute as Any for mypy compatibility with legacy AuthClient
        self.http_client: Any
        try:
            from core.base_manager import create_http_client_from_auth

            self.http_client = create_http_client_from_auth(self.auth)
        except Exception:
            self.http_client = self.auth

        logger.info(f"{SharedIcons.MUSIC} Service bibliothèque musicale initialisé")

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
            try:
                # Encoder le content token comme le shell script
                prefix = '["music/tuneIn/stationId","'
                suffix = '"]|{"previousPageId":"TuneIn_SEARCH"}'
                content_data = prefix + station_id + suffix
                content_token = base64.b64encode(base64.b64encode(content_data.encode()).decode().encode()).decode()

                payload: dict[str, Any] = {"contentToken": f"music:{content_token}"}

                headers = _make_headers(self.auth, self.config)

                response = self.breaker.call(
                    self.http_client.put,
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
                logger.success(f"{SharedIcons.MUSIC} Station TuneIn {station_id} lancée sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture TuneIn {station_id}: {e}")
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
            try:
                # Payload différent selon track_id ou album
                if track_id:
                    payload: dict[str, Any] = {"trackId": track_id, "playQueuePrime": True}
                elif artist and album:
                    payload = {"albumArtistName": artist, "albumName": album}
                else:
                    logger.error("track_id ou (artist+album) requis")
                    return False

                headers = _make_headers(self.auth, self.config)

                response = self.breaker.call(
                    self.http_client.post,
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
                track_info = f"morceau {track_id}" if track_id else f"album '{album}' de {artist}"
                logger.success(f"{SharedIcons.MUSIC} {track_info} lancé sur {device_serial}")
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
            try:
                payload: dict[str, Any] = {"playlistId": playlist_id, "playQueuePrime": True}

                headers = _make_headers(self.auth, self.config)

                response = self.breaker.call(
                    self.http_client.post,
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
                logger.success(f"{SharedIcons.MUSIC} Playlist {playlist_id} lancée sur {device_serial}")
                return True

            except Exception as e:
                logger.error(f"{SharedIcons.ERROR} Erreur lecture playlist {playlist_id}: {e}")
                return False

    def play_prime_playlist(self, device_serial: str, device_type: str, media_owner_id: str, asin: str) -> bool:
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
            try:
                payload = {"asin": asin}

                headers = _make_headers(self.auth, self.config)

                response = self.breaker.call(
                    self.http_client.post,
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
                logger.info(f"Playlist Prime {asin} lancée")
                return True

            except Exception as e:
                logger.error(f"Erreur lecture Prime playlist: {e}")
                return False

    def play_prime_station(self, device_serial: str, device_type: str, media_owner_id: str, seed_id: str) -> bool:
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
            try:
                # Format du seed comme le shell script
                seed_data = {"type": "KEY", "seedId": seed_id}
                payload = {
                    "seed": json.dumps(seed_data),
                    "stationName": "none",
                    "seedType": "KEY",
                }

                headers = _make_headers(self.auth, self.config)

                response = self.breaker.call(
                    self.http_client.post,
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
                logger.info(f"Station Prime {seed_id} lancée")
                return True

            except Exception as e:
                logger.error(f"Erreur lecture Prime station: {e}")
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
            try:
                payload: dict[str, Any] = {
                    "deviceType": device_type,
                    "deviceSerialNumber": device_serial,
                    "mediaOwnerCustomerId": media_owner_id,
                    "queueId": queue_id,
                    "service": None,
                    "trackSource": "TRACK",
                }

                headers = _make_headers(self.auth, self.config)

                response = self.breaker.call(
                    self.http_client.post,
                    f"https://{self.config.alexa_domain}/api/media/play-historical-queue",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                response.raise_for_status()
                logger.success(f"Queue historique {queue_id} lancée")
                return True

            except Exception as e:
                logger.error(f"Erreur lecture queue historique: {e}")
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
                all_tracks: list[dict[str, Any]] = []
                offset = 0
                size = 50

                headers = _make_headers(self.auth, self.config)

                while True:
                    response = self.breaker.call(
                        self.http_client.get,
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

                count = len(all_tracks)
                msg = f"{SharedIcons.MUSIC} {count} entrées bibliothèque récupérées pour {device_serial}"
                logger.success(msg)
                return all_tracks

            except Exception as e:
                msg = f"{SharedIcons.ERROR} Erreur récupération bibliothèque pour {device_serial}: {e}"
                logger.error(msg)
                return []

    def get_prime_playlists(self, device_serial: str, device_type: str, media_owner_id: str) -> List[Dict[str, Any]]:
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
                headers = _make_headers(self.auth, self.config)

                # Récupérer les browse nodes
                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/prime/prime-playlist-browse-nodes",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                    },
                    headers={**headers, "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=15,
                )

                response.raise_for_status()
                data = response.json()

                all_playlists: list[dict[str, Any]] = []

                # Pour chaque browse node, récupérer les playlists
                for browse_node in data.get("primePlaylistBrowseNodeList", []):
                    for sub_node in browse_node.get("subNodes", []):
                        node_id = sub_node.get("nodeId")
                        if not node_id:
                            continue

                        pl_response = self.breaker.call(
                            self.http_client.get,
                            f"https://{self.config.alexa_domain}/api/prime/prime-playlists-by-browse-node",
                            params={
                                "browseNodeId": node_id,
                                "deviceSerialNumber": device_serial,
                                "deviceType": device_type,
                                "mediaOwnerCustomerId": media_owner_id,
                            },
                            headers={
                                **headers,
                                "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", "")),
                            },
                            timeout=15,
                        )

                        pl_response.raise_for_status()
                        pl_data = pl_response.json()
                        all_playlists.extend(pl_data.get("playlists", []))

                count = len(all_playlists)
                msg = f"{SharedIcons.MUSIC} {count} playlists Prime récupérées pour {device_serial}"
                logger.success(msg)
                return all_playlists

            except Exception as e:
                msg = f"{SharedIcons.ERROR} Erreur récupération Prime playlists pour {device_serial}: {e}"
                logger.error(msg)
                return []

    def get_prime_stations(self, device_serial: str, device_type: str, media_owner_id: str) -> List[Dict[str, Any]]:
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
                headers = _make_headers(self.auth, self.config)

                response = self.breaker.call(
                    self.http_client.get,
                    f"https://{self.config.alexa_domain}/api/prime/prime-sections",
                    params={
                        "deviceSerialNumber": device_serial,
                        "deviceType": device_type,
                        "mediaOwnerCustomerId": media_owner_id,
                    },
                    headers={**headers, "csrf": getattr(self.http_client, "csrf", getattr(self.auth, "csrf", ""))},
                    timeout=15,
                )

                response.raise_for_status()
                data = response.json()

                logger.success(f"{SharedIcons.MUSIC} Stations Prime récupérées pour {device_serial}")
                return cast(List[Dict[str, Any]], data.get("primeMusicSections", []))

            except Exception as e:
                msg = f"{SharedIcons.ERROR} Erreur récupération Prime stations pour {device_serial}: {e}"
                logger.error(msg)
                return []
