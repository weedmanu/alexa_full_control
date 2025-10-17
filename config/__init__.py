"""
Configuration centralisée pour Alexa Full Control.

Ce module centralise TOUTES les configurations de l'application :
- Constantes (régions, endpoints API)
- Chemins (dossiers, fichiers)
- Settings (timeouts, retries, etc.)

Usage:
    from config import AmazonRegions, AlexaAPI, AppPaths, get_settings
    
    # Obtenir la configuration
    settings = get_settings()
    
    # Obtenir l'URL de base Alexa
    base_url = AlexaAPI.get_base_url(settings.region)
    
    # Obtenir un endpoint complet
    devices_url = AlexaAPI.get_full_url("DEVICES_LIST", settings.region)
    
    # Obtenir un chemin
    config_dir = AppPaths.get_config_dir()
"""

from config.constants import AlexaAPI, AmazonRegions, AppConstants
from config.paths import AppPaths
from config.settings import AppSettings, get_settings, reset_settings, set_settings

__all__ = [
    # Constantes
    "AmazonRegions",
    "AlexaAPI",
    "AppConstants",
    # Chemins
    "AppPaths",
    # Paramètres
    "AppSettings",
    "get_settings",
    "set_settings",
    "reset_settings",
]

# Version du module de configuration
__version__ = "1.0.0"
