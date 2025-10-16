"""Aide pour la commande ALEXA principale — accueil et orientation.

Généré automatiquement par utils.help_generator.generate_category_help()
"""

from utils.help_generator import generate_category_help


def get_main_help() -> str:
    """Retourne le texte d'aide complet pour la commande principale 'alexa'."""
    return generate_category_help(
        category="alexa",
        icon="🎙️",
        title="ALEXA ADVANCED CONTROL - Contrôle avancé d'Alexa",
        usage_patterns=[
            "alexa [OPTIONS_GLOBALES] <CATEGORIE> [OPTIONS_CATEGORIE] [<ACTION>] [OPTIONS_ACTION] <COMMAND> [OPTIONS_COMMAND]",
        ],
        actions=[
            {
                "name": "auth",
                "description": "Authentification et gestion des tokens",
            },
            {
                "name": "device",
                "description": "Gestion des appareils Alexa",
            },
            {
                "name": "timers",
                "description": "Minuteurs, alarmes, rappels",
            },
            {
                "name": "music",
                "description": "Contrôle musical et médias",
            },
            {
                "name": "smarthome",
                "description": "Domotique et appareils connectés",
            },
            {
                "name": "alarm",
                "description": "Gestion des alarmes programmées",
            },
            {
                "name": "reminder",
                "description": "Rappels et notifications",
            },
            {
                "name": "routine",
                "description": "Automatisations et routines",
            },
            {
                "name": "activity",
                "description": "Historique d'activité",
            },
            {
                "name": "calendar",
                "description": "Gestion du calendrier",
            },
            {
                "name": "lists",
                "description": "Listes (TODO, shopping, etc.)",
            },
            {
                "name": "announcement",
                "description": "Envoi d'annonces audio",
            },
            {
                "name": "notification",
                "description": "Gestion des notifications",
            },
            {
                "name": "dnd",
                "description": "Mode Ne pas déranger",
            },
            {
                "name": "multiroom",
                "description": "Musique en multisalles",
            },
            {
                "name": "cache",
                "description": "Gestion du cache",
            },
        ],
        examples=[
            "alexa device list",
            "alexa device info --device 'Salon Echo'",
            "alexa music play",
            "alexa auth status",
            "alexa --verbose device list",
        ],
        prerequisites=[
            "Authentification Alexa configurée (alexa auth create)",
            "Appareils Alexa connectés et accessibles",
            "Connexion internet stable",
            "Cookies d'authentification valides",
        ],
    )


# Réexports pour compatibilité avec ancien code
MAIN_HELP_TEMPLATE = get_main_help()
