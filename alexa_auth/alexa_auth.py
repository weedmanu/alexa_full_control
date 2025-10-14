"""
Gestionnaire d'authentification Alexa.

Ce module fournit la classe AlexaAuth qui gère l'authentification
avec l'API Amazon Alexa en utilisant les cookies générés par le
processus Node.js.

Auteur: M@nu
Date: 7 octobre 2025
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from loguru import logger


class AlexaAuth:
    """
    Gestionnaire d'authentification Alexa.

    Charge et gère les cookies d'authentification Amazon Alexa,
    fournit une session requests configurée pour les appels API.
    Utilise le cache pour éviter les rechargements coûteux.

    Attributes:
        session (requests.Session): Session HTTP avec cookies
        amazon_domain (str): Domaine Amazon (ex: "amazon.fr")
        csrf (str): Token CSRF pour les requêtes
        refresh_token (str): Token de rafraîchissement
        cookies_loaded (bool): État du chargement des cookies
        cache_service: Service de cache pour les données d'auth

    Example:
        >>> auth = AlexaAuth()
        >>> if auth.load_cookies():
        ...     response = auth.get("https://alexa.amazon.fr/api/devices")
        ...     devices = response.json()
    """

    def __init__(self, data_dir: Optional[Path] = None, cache_service=None):
        """
        Initialise le gestionnaire d'authentification.

        Args:
            data_dir: Répertoire contenant les fichiers de cookies
                     (défaut: alexa_auth/data)
            cache_service: Service de cache optionnel (non utilisé pour l'auth)
        """
        if data_dir is None:
            # Chemin par défaut
            self.data_dir = Path(__file__).parent / "data"
        else:
            self.data_dir = Path(data_dir)

        self.session = requests.Session()
        self.amazon_domain = "amazon.fr"  # Défaut
        self.csrf: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.cookies_loaded = False
        # Note: cache_service n'est plus utilisé pour l'authentification
        # Les données d'auth restent uniquement dans alexa_auth/data/

        # Headers par défaut
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "fr-FR,fr;q=0.9",
            }
        )

        logger.debug(f"AlexaAuth initialisé (data_dir={self.data_dir})")

    def load_cookies(self) -> bool:
        """
        Charge les cookies depuis les fichiers de données.

        Essaie les fichiers cookie-resultat.json puis cookie.txt.

        Returns:
            True si cookies chargés avec succès, False sinon

        Example:
            >>> auth = AlexaAuth()
            >>> if auth.load_cookies():
            ...     print("Authentification OK")
            ... else:
            ...     print("Pas de cookies valides")
        """
        # Essai 1: cookie-resultat.json (format complet)
        cookie_json = self.data_dir / "cookie-resultat.json"
        if cookie_json.exists():
            if self._load_from_json(cookie_json):
                logger.info("Cookies chargés depuis cookie-resultat.json")
                self.cookies_loaded = True
                return True

        # Essai 2: cookie.txt (format Netscape)
        cookie_txt = self.data_dir / "cookie.txt"
        if cookie_txt.exists():
            if self._load_from_txt(cookie_txt):
                logger.info("Cookies chargés depuis cookie.txt")
                self.cookies_loaded = True
                return True

        logger.warning("Aucun fichier de cookies valide trouvé")
        return False

    def _load_from_json(self, filepath: Path) -> bool:
        """
        Charge les cookies depuis cookie-resultat.json.

        Args:
            filepath: Chemin vers cookie-resultat.json

        Returns:
            True si succès, False sinon
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            # Extraire les données du récapitulatif
            recapitulatif = data.get("recapitulatif", {})
            donnees_completes = data.get("donneesCompletes", {})

            # Charger le cookie (format compact)
            cookie_str = recapitulatif.get("cookie", "")
            if cookie_str:
                self._parse_cookie_string(cookie_str)

            # Extraire les métadonnées importantes
            self.csrf = recapitulatif.get("csrf")
            self.refresh_token = recapitulatif.get("refreshToken")

            # Extraire le domaine Amazon
            amazon_page = donnees_completes.get("amazonPage", "amazon.fr")
            self.amazon_domain = amazon_page

            logger.debug(
                f"Cookies JSON chargés: {len(self.session.cookies)} cookies, domain={self.amazon_domain}"
            )
            return len(self.session.cookies) > 0

        except Exception as e:
            logger.error(f"Erreur lors du chargement de {filepath}: {e}")
            return False

    def _load_from_txt(self, filepath: Path) -> bool:
        """
        Charge les cookies depuis cookie.txt (format Netscape).

        Args:
            filepath: Chemin vers cookie.txt

        Returns:
            True si succès, False sinon
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            # Parser le format Netscape HTTP Cookie File
            # Format: domain flag path secure expiration name value
            for line in lines:
                line = line.strip()

                # Ignorer les commentaires et lignes vides
                if not line or line.startswith("#"):
                    continue

                parts = line.split("\t")
                if len(parts) != 7:
                    continue

                domain, _, path, secure, expiration, name, value = parts

                # Déterminer le domaine Amazon
                if "amazon." in domain and not self.amazon_domain:
                    # Extraire amazon.XX du domain
                    self.amazon_domain = domain.lstrip(".")

                # Ajouter le cookie à la session
                self.session.cookies.set(
                    name=name,
                    value=value,
                    domain=domain,
                    path=path,
                    secure=secure.upper() == "TRUE",
                )

                # Extraire CSRF si présent
                if name == "csrf":
                    self.csrf = value

            logger.debug(
                f"Cookies TXT chargés: {len(self.session.cookies)} cookies, domain={self.amazon_domain}"
            )
            return len(self.session.cookies) > 0

        except Exception as e:
            logger.error(f"Erreur lors du chargement de {filepath}: {e}")
            return False

    def _parse_cookie_string(self, cookie_str: str) -> None:
        """
        Parse une chaîne de cookies (format: name1=value1; name2=value2).

        Args:
            cookie_str: Chaîne de cookies à parser
        """
        for cookie in cookie_str.split("; "):
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                self.session.cookies.set(name, value, domain=f".{self.amazon_domain}")

    def _save_to_cache(self) -> None:
        """
        Méthode de compatibilité - ne fait rien.

        Les données d'authentification restent uniquement dans alexa_auth/data/
        """
        # Les données d'authentification sont déjà dans les fichiers
        # Pas besoin de cache supplémentaire
        pass

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Effectue une requête GET avec la session authentifiée.

        Args:
            url: URL à requêter
            **kwargs: Arguments additionnels pour requests.get

        Returns:
            Objet Response de requests

        Raises:
            requests.RequestException: En cas d'erreur réseau

        Example:
            >>> response = auth.get("https://alexa.amazon.fr/api/devices")
            >>> devices = response.json()
        """
        if not self.cookies_loaded:
            logger.warning("GET sans cookies chargés")

        logger.debug(f"GET {url}")
        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Effectue une requête POST avec la session authentifiée.

        Args:
            url: URL à requêter
            **kwargs: Arguments additionnels pour requests.post

        Returns:
            Objet Response de requests

        Raises:
            requests.RequestException: En cas d'erreur réseau

        Example:
            >>> response = auth.post(
            ...     "https://alexa.amazon.fr/api/timers",
            ...     json={"type": "Timer", "duration": "PT10M"}
            ... )
        """
        if not self.cookies_loaded:
            logger.warning("POST sans cookies chargés")

        # Ajouter le CSRF token si disponible
        if self.csrf and "headers" not in kwargs:
            kwargs["headers"] = {}
        if self.csrf:
            kwargs.setdefault("headers", {})["csrf"] = self.csrf

        logger.debug(f"POST {url}")
        return self.session.post(url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """
        Effectue une requête PUT avec la session authentifiée.

        Args:
            url: URL à requêter
            **kwargs: Arguments additionnels pour requests.put

        Returns:
            Objet Response de requests
        """
        if not self.cookies_loaded:
            logger.warning("PUT sans cookies chargés")

        if self.csrf:
            kwargs.setdefault("headers", {})["csrf"] = self.csrf

        logger.debug(f"PUT {url}")
        return self.session.put(url, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Effectue une requête DELETE avec la session authentifiée.

        Args:
            url: URL à requêter
            **kwargs: Arguments additionnels pour requests.delete

        Returns:
            Objet Response de requests
        """
        if not self.cookies_loaded:
            logger.warning("DELETE sans cookies chargés")

        if self.csrf:
            kwargs.setdefault("headers", {})["csrf"] = self.csrf

        logger.debug(f"DELETE {url}")
        return self.session.delete(url, **kwargs)

    def is_authenticated(self) -> bool:
        """
        Vérifie si l'authentification est valide.

        Returns:
            True si cookies chargés et session valide

        Example:
            >>> if auth.is_authenticated():
            ...     print("Connecté")
        """
        return self.cookies_loaded and len(self.session.cookies) > 0

    def get_cookie_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur les cookies chargés.

        Returns:
            Dictionnaire avec infos cookies

        Example:
            >>> info = auth.get_cookie_info()
            >>> print(f"Domain: {info['domain']}, Cookies: {info['count']}")
        """
        return {
            "loaded": self.cookies_loaded,
            "domain": self.amazon_domain,
            "count": len(self.session.cookies),
            "has_csrf": self.csrf is not None,
            "has_refresh_token": self.refresh_token is not None,
        }

    def __repr__(self) -> str:
        """Représentation de AlexaAuth."""
        return (
            f"AlexaAuth(domain={self.amazon_domain}, "
            f"authenticated={self.is_authenticated()}, "
            f"cookies={len(self.session.cookies)})"
        )
