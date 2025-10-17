"""
Service de gestion des Favoris - TDD Implementation

Permet de sauvegarder et réutiliser des stations radio, scènes, etc.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from utils.json_storage import JsonStorage
from utils.text_utils import normalize_name


class FavoriteService:
    """Service de gestion des favoris."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialise le service."""
        # Déterminer le répertoire de config
        if config_dir is None:
            config_dir = Path.home() / ".alexa"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.favorites_file = self.config_dir / "favorites.json"
        self._storage = JsonStorage(self.config_dir)
        self._favorites: Dict[str, Dict[str, Any]] = {}
        
        # Charger les favoris existants
        self._load_favorites()

    def _normalize_name(self, name: str) -> str:
        """Normalise le nom du favori pour la clé."""
        return normalize_name(name)

    def _load_favorites(self) -> None:
        """Charge les favoris depuis le fichier."""
        self._favorites = self._storage.load("favorites.json", default={})

    def save_favorites(self) -> bool:
        """Sauvegarde les favoris dans le fichier."""
        try:
            self._storage.save("favorites.json", self._favorites)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des favoris: {e}")
            return False

    def add_favorite(
        self,
        name: str,
        favorite_type: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Ajoute un nouveau favori.
        
        Args:
            name: Nom du favori
            favorite_type: Type (music.tunein, scene, etc)
            params: Paramètres (dict)
            
        Returns:
            True si succès, False sinon
        """
        # Validation
        if not name or not name.strip():
            logger.warning("Nom du favori manquant")
            return False
        
        if not favorite_type or not favorite_type.strip():
            logger.warning("Type du favori manquant")
            return False
        
        # Vérifier s'il existe déjà
        key = self._normalize_name(name)
        if key in self._favorites:
            logger.warning(f"Favori '{name}' existe déjà")
            return False
        
        # Ajouter le favori
        self._favorites[key] = {
            "name": name,
            "type": favorite_type,
            "params": params or {},
            "created": datetime.now().isoformat(),
            "last_used": None,
        }
        
        logger.info(f"Favori '{name}' ajouté")
        
        # Sauvegarder
        return self.save_favorites()

    def delete_favorite(self, name: str) -> bool:
        """Supprime un favori.
        
        Args:
            name: Nom du favori
            
        Returns:
            True si succès, False sinon
        """
        key = self._normalize_name(name)
        
        if key not in self._favorites:
            logger.warning(f"Favori '{name}' introuvable")
            return False
        
        del self._favorites[key]
        logger.info(f"Favori '{name}' supprimé")
        
        return self.save_favorites()

    def get_favorite(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un favori par son nom.
        
        Args:
            name: Nom du favori
            
        Returns:
            Dict du favori ou None
        """
        key = self._normalize_name(name)
        return self._favorites.get(key)

    def get_favorites(self) -> Dict[str, Dict[str, Any]]:
        """Récupère tous les favoris.
        
        Returns:
            Dict de tous les favoris
        """
        return self._favorites.copy()

    def get_favorites_by_type(self, favorite_type: str) -> List[Dict[str, Any]]:
        """Récupère les favoris d'un type particulier.
        
        Args:
            favorite_type: Type de favori
            
        Returns:
            Liste des favoris du type
        """
        return [
            fav for fav in self._favorites.values()
            if fav["type"] == favorite_type
        ]

    def search_favorites(self, query: str) -> List[Dict[str, Any]]:
        """Cherche des favoris par texte.
        
        Args:
            query: Texte à chercher
            
        Returns:
            Liste des favoris matchant
        """
        query_lower = query.lower()
        results = []
        
        for fav in self._favorites.values():
            if (query_lower in fav["name"].lower() or
                query_lower in fav["type"].lower()):
                results.append(fav)
        
        return results

    def update_favorite(
        self,
        name: str,
        params: Optional[Dict[str, Any]] = None,
        favorite_type: Optional[str] = None,
    ) -> bool:
        """Met à jour un favori.
        
        Args:
            name: Nom du favori
            params: Nouveaux paramètres
            favorite_type: Nouveau type (optionnel)
            
        Returns:
            True si succès, False sinon
        """
        key = self._normalize_name(name)
        
        if key not in self._favorites:
            logger.warning(f"Favori '{name}' introuvable")
            return False
        
        if params is not None:
            self._favorites[key]["params"] = params
        
        if favorite_type is not None:
            self._favorites[key]["type"] = favorite_type
        
        self._favorites[key]["last_updated"] = datetime.now().isoformat()
        
        logger.info(f"Favori '{name}' mis à jour")
        
        return self.save_favorites()

    def mark_as_used(self, name: str) -> bool:
        """Marque un favori comme utilisé récemment.
        
        Args:
            name: Nom du favori
            
        Returns:
            True si succès, False sinon
        """
        key = self._normalize_name(name)
        
        if key not in self._favorites:
            return False
        
        self._favorites[key]["last_used"] = datetime.now().isoformat()
        
        return self.save_favorites()

    def export_to_json(self) -> str:
        """Exporte tous les favoris en JSON.
        
        Returns:
            String JSON
        """
        return json.dumps(self._favorites, indent=2)

    def import_from_json(self, json_data: str) -> bool:
        """Importe des favoris depuis JSON.
        
        Args:
            json_data: String JSON
            
        Returns:
            True si succès, False sinon
        """
        try:
            imported = json.loads(json_data)
            
            # Valider chaque favori
            for key, fav in imported.items():
                if not isinstance(fav, dict):
                    logger.warning(f"Favori '{key}' invalide")
                    return False
                
                if "name" not in fav or "type" not in fav:
                    logger.warning(f"Favori '{key}' manque des champs requis")
                    return False
            
            # Fusionner avec les favoris existants
            self._favorites.update(imported)
            
            return self.save_favorites()
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON invalide: {e}")
            return False

    def get_favorites_sorted_by_usage(self) -> List[Dict[str, Any]]:
        """Retourne les favoris triés par utilisation récente.
        
        Returns:
            Liste des favoris triés
        """
        favorites = list(self._favorites.values())
        
        # Trier par last_used (les plus récents d'abord)
        favorites.sort(
            key=lambda x: x.get("last_used") or "",
            reverse=True
        )
        
        return favorites
