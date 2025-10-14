"""
Module de gestion de l'aide pour Alexa CLI.

Ce module centralise toute la logique d'affichage et de génération
des différents types d'aide (principale, catégories, actions, etc.).

Il fournit une API propre pour générer l'aide sans dépendre
de la logique de parsing argparse.

ARCHITECTURE:
    Utilise le système modulaire de utils.help_formatter pour garantir
    une cohérence visuelle parfaite et éviter la duplication de code.
"""

from typing import Optional
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH pour l'import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.help_formatter import (
    format_header,
    format_features,
    format_usage,
    format_global_options,
    format_categories,
    format_subcategories,
    format_actions,
    format_examples,
    format_more_help_main,
    format_prerequisites
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 AIDE PRINCIPALE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_main_help() -> str:
    """Génère l'aide principale (alexa -h) en assemblant les sections."""
    sections = []
    
    # Header
    sections.append(format_header("🎙️", "ALEXA ADVANCED CONTROL - CONTRÔLE AVANCÉ D'ALEXA"))
    
    # Fonctionnalités
    sections.append(format_features([
        "Contrôle complet des appareils Alexa",
        "Gestion des médias (musique, playlists, volume)",
        "Programmation temporelle (minuteurs, alarmes, rappels)",
        "Contrôle domotique (lumières, thermostats, etc.)",
        "Notifications et annonces vocales",
        "Synchronisation multi-appareils"
    ], show_title=False))
    
    # Usage
    sections.append(format_usage(is_main=True))
    
    # Options globales
    sections.append(format_global_options())
    
    # Catégories
    sections.append(format_categories([
        {"name": "auth", "desc": "Gestion de l'authentification et connexion"},
        {"name": "device", "desc": "Contrôle et gestion des appareils"},
        {"name": "timers", "desc": "Gestion du temps (minuteurs, alarmes, rappels)"},
        {"name": "music", "desc": "Contrôle musical et médias"},
        {"name": "smarthome", "desc": "Domotique et appareils connectés"},
        {"name": "notification", "desc": "Gestion des notifications"},
        {"name": "routine", "desc": "Automatisations et routines"},
        {"name": "activity", "desc": "Historique d'activité"},
        {"name": "calendar", "desc": "Gestion du calendrier"},
        {"name": "cache", "desc": "Gestion du cache local"}
    ]))
    
    # Sous-catégories
    sections.append(format_subcategories([
        {"name": "countdown", "desc": "Minuteurs et compteurs de temps"},
        {"name": "alarm", "desc": "Gestion des alarmes programmées"},
        {"name": "reminder", "desc": "Rappels et notifications"},
        {"name": "playback", "desc": "Contrôle de lecture musicale"},
        {"name": "volume", "desc": "Gestion du volume audio"},
        {"name": "equalizer", "desc": "Égaliseur et réglages audio"},
        {"name": "light", "desc": "Contrôle de l'éclairage"},
        {"name": "thermostat", "desc": "Gestion de la température"},
        {"name": "security", "desc": "Sécurité et surveillance"},
        {"name": "camera", "desc": "Contrôle des caméras"}
    ]))
    
    # Actions
    sections.append(format_actions([
        {"name": "create", "desc": "Créer un nouvel élément (minuteur, alarme, etc.)"},
        {"name": "list", "desc": "Lister les éléments existants"},
        {"name": "delete", "desc": "Supprimer un élément"},
        {"name": "update", "desc": "Modifier un élément existant"},
        {"name": "play/pause/stop", "desc": "Contrôler la lecture média"},
        {"name": "on/off", "desc": "Contrôler l'état des appareils"}
    ]))
    
    # Exemples
    sections.append(format_examples([
        "alexa device list",
        "alexa timers countdown create --duration 10m",
        'alexa music play --playlist "Ma playlist"',
        'alexa smarthome light on --name "Salon"',
        'alexa --verbose device list                       # Avec option globale'
    ]))
    
    # Pour plus d'aide
    sections.append(format_more_help_main())
    
    # Prérequis
    sections.append(format_prerequisites([
        "Authentification Alexa configurée (alexa auth login)",
        "Appareils Alexa connectés et accessibles",
        "Connexion internet stable",
        "Cookies d'authentification valides"
    ]))
    
    return "\n\n".join(sections) + "\n"


# Export pour compatibilité avec l'ancien code
MAIN_HELP_TEMPLATE = get_main_help()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 DÉFINITIONS DES CATÉGORIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from utils.help_formatter import create_category_help

def _get_timers_help() -> str:
    """Génère l'aide de la catégorie TIMERS avec le système modulaire."""
    return create_category_help(
        icon="⏰",
        name="timers",
        description="GESTION DU TEMPS ALEXA",
        features=[
            "Gestion complète des minuteurs et alarmes",
            "Création et gestion des rappels",
            "Contrôle précis du temps (pause, reprise, annulation)",
            "Notifications et alertes programmées",
            "Synchronisation multi-appareils"
        ],
        subcategories=[
            {"name": "countdown", "desc": "Minuteurs et compteurs de temps"},
            {"name": "alarm", "desc": "Gestion des alarmes programmées"},
            {"name": "reminder", "desc": "Rappels et notifications"}
        ],
        examples=[
            'alexa timers countdown create --duration 10m --label "Pâtes"',
            'alexa timers countdown list',
            'alexa timers countdown cancel --id 123',
            'alexa timers alarm create --time 07:30 --label "Réveil"',
            'alexa timers alarm list',
            'alexa timers reminder create --label "Réunion équipe"'
        ],
        prerequisites=[
            "Authentification requise pour la synchronisation",
            "Connexion internet obligatoire pour les rappels",
            "Appareil cible doit être spécifié (-d)",
            "Programmations synchronisées entre appareils"
        ]
    )


def _get_music_help() -> str:
    """Génère l'aide de la catégorie MUSIC avec le système modulaire."""
    return create_category_help(
        icon="🎵",
        name="music",
        description="CONTRÔLE MUSICAL ALEXA",
        features=[
            "Lecture et contrôle de musique",
            "Gestion des playlists et stations",
            "Contrôle du volume et égaliseur",
            "Recherche et découverte musicale",
            "Synchronisation multi-room"
        ],
        subcategories=[
            {"name": "playback", "desc": "Contrôle de lecture musicale"},
            {"name": "volume", "desc": "Gestion du volume audio"},
            {"name": "equalizer", "desc": "Égaliseur et réglages audio"},
            {"name": "library", "desc": "Bibliothèque musicale"}
        ],
        examples=[
            'alexa music playback play --song "Bohemian Rhapsody"',
            'alexa music volume set --level 75',
            'alexa music playback pause',
            'alexa music equalizer bass --level 5'
        ],
        prerequisites=[
            "Service musical configuré (Amazon Music, Spotify)",
            "Appareil cible avec capacités audio",
            "Connexion internet pour le streaming",
            "Authentification du service musical"
        ]
    )


class AlexaHelp:
    """
    Gestionnaire centralisé de l'aide Alexa CLI.

    Fournit des méthodes pour générer différents types d'aide
    avec une interface unifiée.
    
    NOUVEAU: Utilise le système modulaire de utils.help_formatter
    pour garantir cohérence et réduire la duplication de code.
    """

    def __init__(self):
        """Initialise le gestionnaire d'aide."""
        pass

    def get_main_help_instance(self) -> str:
        """
        Retourne l'aide principale (alexa --help).

        Returns:
            Aide principale formatée avec le système modulaire
        """
        return get_main_help()

    def get_category_help(self, category: str) -> Optional[str]:
        """
        Retourne l'aide d'une catégorie spécifique.

        Args:
            category: Nom de la catégorie

        Returns:
            Aide de catégorie ou None si non trouvé
        """
        category_generators = {
            'timers': _get_timers_help,
            'music': _get_music_help,
        }
        
        generator = category_generators.get(category)
        return generator() if generator else None

    def get_subcategory_help(self, category: str, subcategory: str) -> Optional[str]:
        """
        Retourne l'aide d'une sous-catégorie spécifique.

        Args:
            category: Nom de la catégorie
            subcategory: Nom de la sous-catégorie

        Returns:
            Template d'aide de sous-catégorie ou None si non trouvé
        """
        # Pour l'instant, retourner None - à implémenter avec le système modulaire
        return None

    def get_action_help(self, category: str, subcategory: Optional[str], action: str) -> Optional[str]:
        """
        Retourne l'aide d'une action spécifique.

        Args:
            category: Nom de la catégorie
            subcategory: Nom de la sous-catégorie (optionnel)
            action: Nom de l'action

        Returns:
            Template d'aide d'action ou None si non trouvé
        """
        # Pour l'instant, retourner None - à implémenter avec le système modulaire
        return None


# Instance globale pour utilisation facile
help_manager = AlexaHelp()


def get_category_help_util(category: str) -> Optional[str]:
    """
    Fonction utilitaire pour obtenir l'aide d'une catégorie.

    Args:
        category: Nom de la catégorie

    Returns:
        Aide de catégorie ou None
    """
    return help_manager.get_category_help(category)


def get_help_hierarchy() -> str:
    """
    Fonction utilitaire pour obtenir l'explication de hiérarchie.

    Returns:
        Texte d'explication de la navigation d'aide
    """
    return (
        "\033[1;37m💡 Navigation dans l'aide:\033[0m\n"
        "  alexa --help                              # Cette aide générale\n"
        "  alexa <categorie> --help                  # Aide d'une catégorie\n"
        "  alexa <categorie> <sous-categorie> --help # Aide d'une sous-catégorie\n"
        "  alexa <categorie> <action> --help         # Aide d'une action\n\n"
        "\033[1;37m📝 Astuces:\033[0m\n"
        "  • Utilisez --help à chaque niveau pour explorer\n"
        "  • Les couleurs indiquent les éléments importants\n"
        "  • L'auto-complétion (Tab) facilite la découverte\n"
    )