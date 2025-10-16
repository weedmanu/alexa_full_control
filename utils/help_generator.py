"""Générateur centralisé de textes d'aide pour les catégories CLI.

Ce module fournit une seule fonction générique `generate_category_help()` qui
crée les textes d'aide standardisés pour toutes les catégories (device, auth,
alarm, music, etc.).

Remplace les 17 fichiers help_texts/*.py par un seul générateur, réduisant
la duplication et assurant la cohérence visuelle.

Usage typique (dans chaque catégorie):
    >>> help_text = generate_category_help(
    ...     category="device",
    ...     icon="📱",
    ...     title="Gestion des appareils",
    ...     usage_patterns=["alexa [OPTIONS] device <ACTION> [OPTIONS_ACTION]"],
    ...     actions=[
    ...         {"name": "list", "description": "Lister tous les appareils"},
    ...         {"name": "info", "description": "Afficher info d'un appareil", "options": "--device DEVICE"},
    ...     ],
    ...     examples=["alexa device list", "alexa device info --device 'Salon Echo'"],
    ... )
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from utils.colorizer import (
    colorize,
    colorize_category_line,
    colorize_example,
    colorize_section_separator,
    colorize_section_title,
)


def get_category_actions(category: str) -> List[Dict[str, str]]:
    """Retourne les vraies actions et options pour une catégorie donnée.

    Args:
        category: Nom de la catégorie

    Returns:
        Liste des actions avec leurs descriptions et options
    """
    actions_map = {
        "device": [
            {
                "name": "list",
                "description": "Lister tous les appareils Alexa",
                "options": "--filter PATTERN, --online-only, --refresh, --json",
            },
            {
                "name": "info",
                "description": "Informations détaillées sur un appareil",
                "options": "-d/--device DEVICE, --json",
            },
            {
                "name": "volume",
                "description": "Gérer le volume d'un appareil",
                "options": "get/set -d/--device DEVICE [--level VOLUME]",
            },
        ],
        "music": [
            {
                "name": "play",
                "description": "Lire de la musique",
                "options": "-d/--device DEVICE, --provider PROVIDER, --search QUERY",
            },
            {"name": "pause", "description": "Mettre en pause la lecture", "options": "-d/--device DEVICE"},
            {"name": "stop", "description": "Arrêter la lecture", "options": "-d/--device DEVICE"},
            {
                "name": "control",
                "description": "Contrôler la lecture",
                "options": "-d/--device DEVICE, --action next/prev/play/pause",
            },
            {
                "name": "shuffle",
                "description": "Activer/désactiver le mode aléatoire",
                "options": "-d/--device DEVICE, --state on/off",
            },
            {
                "name": "repeat",
                "description": "Activer/désactiver la répétition",
                "options": "-d/--device DEVICE, --state on/off",
            },
            {
                "name": "track",
                "description": "Jouer un morceau de bibliothèque",
                "options": "-d/--device DEVICE, --track-id ID ou --album ALBUM --artist ARTIST, --shuffle",
            },
            {
                "name": "playlist",
                "description": "Lire une playlist",
                "options": "-d/--device DEVICE, --id PLAYLIST_ID, --type library/prime-asin/prime-station/prime-queue, --shuffle",
            },
            {
                "name": "library",
                "description": "Bibliothèque musicale",
                "options": "--playlists, --purchases, --imported, --prime-playlists, --prime-stations, -d/--device DEVICE, --json",
            },
            {
                "name": "radio",
                "description": "Jouer une station TuneIn",
                "options": "-d/--device DEVICE, --station-id STATION_ID",
            },
            {"name": "status", "description": "État de la lecture", "options": "-d/--device DEVICE, --complete"},
            {"name": "queue", "description": "Afficher la file d'attente", "options": "-d/--device DEVICE"},
        ],
        "alarm": [
            {
                "name": "create",
                "description": "Créer une alarme",
                "options": "-d/--device DEVICE, --time HH:MM, --label LABEL, --repeat PATTERN, --sound SOUND_ID",
            },
            {"name": "list", "description": "Lister les alarmes", "options": "-d/--device DEVICE, --active-only"},
            {"name": "delete", "description": "Supprimer une alarme", "options": "-d/--device DEVICE, --id ALARM_ID"},
            {
                "name": "update",
                "description": "Modifier une alarme",
                "options": "-d/--device DEVICE, --id ALARM_ID, --time HH:MM, --label LABEL, --repeat PATTERN, --sound SOUND_ID",
            },
            {"name": "enable", "description": "Activer une alarme", "options": "-d/--device DEVICE, --id ALARM_ID"},
            {"name": "disable", "description": "Désactiver une alarme", "options": "-d/--device DEVICE, --id ALARM_ID"},
        ],
        "timer": [
            {
                "name": "countdown",
                "description": "Gérer les minuteurs",
                "options": "create/list/cancel/pause/resume -d/--device DEVICE",
            },
            {
                "name": "create",
                "description": "Créer un minuteur",
                "options": "-d/--device DEVICE, --duration DURATION, --label LABEL",
            },
            {"name": "list", "description": "Lister les minuteurs", "options": "-d/--device DEVICE, --active-only"},
            {
                "name": "cancel",
                "description": "Annuler un minuteur",
                "options": "-d/--device DEVICE, --id TIMER_ID ou --all",
            },
            {
                "name": "pause",
                "description": "Mettre en pause un minuteur",
                "options": "-d/--device DEVICE, --id TIMER_ID",
            },
            {"name": "resume", "description": "Reprendre un minuteur", "options": "-d/--device DEVICE, --id TIMER_ID"},
        ],
        "reminder": [
            {
                "name": "list",
                "description": "Lister les rappels",
                "options": "-d/--device DEVICE, --active-only, --all",
            },
            {
                "name": "create",
                "description": "Créer un rappel",
                "options": "--label TEXT, --datetime YYYY-MM-DD HH:MM ou --recurrence daily/weekly/monthly --time HH:MM",
            },
            {"name": "delete", "description": "Supprimer un rappel", "options": "--id REMINDER_ID, --force"},
            {"name": "complete", "description": "Marquer un rappel comme complété", "options": "--id REMINDER_ID"},
        ],
        "routine": [
            {"name": "list", "description": "Lister les routines", "options": "--only-active"},
            {
                "name": "info",
                "description": "Détails d'une routine",
                "options": "--name ROUTINE_NAME, -d/--device DEVICE",
            },
            {
                "name": "execute",
                "description": "Exécuter une routine",
                "options": "--name ROUTINE_NAME, -d/--device DEVICE",
            },
            {
                "name": "enable",
                "description": "Activer une routine",
                "options": "--name ROUTINE_NAME, -d/--device DEVICE",
            },
            {
                "name": "disable",
                "description": "Désactiver une routine",
                "options": "--name ROUTINE_NAME, -d/--device DEVICE",
            },
        ],
        "lists": [
            {
                "name": "add",
                "description": "Ajouter un élément",
                "options": "TEXT, --list shopping/todo, -d/--device DEVICE, --priority low/medium/high, --due-date YYYY-MM-DD",
            },
            {
                "name": "remove",
                "description": "Supprimer un élément",
                "options": "TEXT, --list shopping/todo, -d/--device DEVICE",
            },
            {
                "name": "clear",
                "description": "Vider la liste",
                "options": "--list shopping/todo, -d/--device DEVICE, --completed-only",
            },
        ],
        "announcement": [
            {
                "name": "send",
                "description": "Envoyer une annonce",
                "options": "-d/--device DEVICE, --message TEXT, --title TITLE",
            },
            {"name": "list", "description": "Lister les annonces", "options": "--limit N, --device DEVICE"},
            {"name": "clear", "description": "Supprimer les annonces", "options": "-d/--device DEVICE, --all"},
            {"name": "read", "description": "Marquer comme lu", "options": "--id ANNOUNCEMENT_ID"},
        ],
        "smarthome": [
            {
                "name": "list",
                "description": "Lister les appareils Smart Home",
                "options": "--filter KEYWORD, --type TYPE",
            },
            {"name": "info", "description": "Informations détaillées", "options": "--entity ENTITY_ID"},
            {
                "name": "control",
                "description": "Allumer/éteindre un appareil",
                "options": "--entity ENTITY_ID, --operation on/off/toggle",
            },
            {"name": "lock", "description": "Verrouiller une serrure", "options": "--entity ENTITY_ID, --code CODE"},
            {
                "name": "unlock",
                "description": "Déverrouiller une serrure",
                "options": "--entity ENTITY_ID, --code CODE",
            },
            {"name": "status", "description": "État actuel", "options": "--entity ENTITY_ID"},
        ],
        "dnd": [
            {"name": "status", "description": "Statut DND d'un appareil", "options": "-d/--device DEVICE"},
            {"name": "enable", "description": "Activer le mode DND", "options": "-d/--device DEVICE"},
            {"name": "disable", "description": "Désactiver le mode DND", "options": "-d/--device DEVICE"},
            {
                "name": "schedule",
                "description": "Programmer le DND",
                "options": "-d/--device DEVICE, --start HH:MM, --end HH:MM, --days DAYS",
            },
        ],
        "multiroom": [
            {"name": "list", "description": "Lister les groupes multiroom", "options": ""},
            {
                "name": "create",
                "description": "Créer un groupe",
                "options": "--name GROUP_NAME, --devices DEVICE1,DEVICE2,... --primary DEVICE",
            },
            {"name": "delete", "description": "Supprimer un groupe", "options": "--name GROUP_NAME, --force"},
            {"name": "info", "description": "Informations sur un groupe", "options": "--name GROUP_NAME"},
        ],
        "calendar": [
            {"name": "list", "description": "Consulter les événements", "options": "-d/--device DEVICE, --days N"},
            {
                "name": "add",
                "description": "Ajouter un événement",
                "options": "--title TEXT, --start DATETIME, --end DATETIME, --location TEXT, --description TEXT",
            },
            {"name": "delete", "description": "Supprimer un événement", "options": "--id EVENT_ID"},
            {"name": "info", "description": "Détails d'un événement", "options": "--id EVENT_ID, --json"},
        ],
        "activity": [
            {
                "name": "list",
                "description": "Lister les activités récentes",
                "options": "--type voice/music/alarm/timer/reminder/smart_home/all, --limit N",
            },
            {"name": "lastdevice", "description": "Dernier appareil utilisé", "options": ""},
            {"name": "lastcommand", "description": "Dernière commande vocale", "options": "-d/--device DEVICE"},
            {"name": "lastresponse", "description": "Dernière réponse d'Alexa", "options": "-d/--device DEVICE"},
        ],
        "cache": [
            {"name": "status", "description": "Afficher statistiques cache", "options": ""},
            {
                "name": "refresh",
                "description": "Forcer resynchronisation",
                "options": "--category devices/smart_home/alarms_and_reminders/all",
            },
            {"name": "clear", "description": "Supprimer tout le cache", "options": ""},
            {
                "name": "show",
                "description": "Afficher contenu JSON",
                "options": "--category devices/smart_home/alarms_and_reminders/routines/sync_stats",
            },
        ],
        "auth": [
            {
                "name": "create",
                "description": "Créer une nouvelle authentification",
                "options": "--email EMAIL, --password PASSWORD, --method METHOD",
            },
            {"name": "list", "description": "Lister les authentifications", "options": ""},
            {"name": "delete", "description": "Supprimer une authentification", "options": "--id AUTH_ID"},
            {"name": "test", "description": "Tester une authentification", "options": "--id AUTH_ID"},
            {"name": "status", "description": "Statut de l'authentification", "options": ""},
        ],
    }

    return actions_map.get(category, [])


@dataclass
class Action:
    """Définition d'une action (commande).

    Attributes:
        name: Nom de l'action (ex: "list", "create")
        description: Description courte de l'action
        options: Options spécifiques (optionnel, ex: "--device DEVICE")
    """

    name: str
    description: str
    options: Optional[str] = None


def generate_category_help(
    category: str,
    icon: str,
    title: str,
    usage_patterns: List[str],
    actions: Optional[List[Dict[str, str]]] = None,
    examples: Optional[List[str]] = None,
    prerequisites: Optional[List[str]] = None,
) -> str:
    """Génère un texte d'aide standardisé pour une catégorie.

    Args:
        category: Nom de la catégorie (ex: "device")
        icon: Emoji pour le header (ex: "📱")
        title: Titre complet (ex: "Gestion des appareils")
        usage_patterns: Patterns d'usage (ex: ["alexa [OPTIONS] device <ACTION> [OPTIONS_ACTION]"])
        actions: Liste des actions avec descriptions (optionnel, auto-rempli si None)
                 Format: [{"name": "list", "description": "..."}, ...]
        examples: Exemples de commandes (optionnel)
        prerequisites: Prérequis optionnels

    Returns:
        Texte d'aide complet formaté avec couleurs.
    """
    # Utiliser les vraies actions si aucune n'est fournie
    if actions is None:
        actions = get_category_actions(category)

    # Exemples par défaut si aucun fourni
    if examples is None:
        examples = [f"alexa {category} list"]
    lines: List[str] = []

    # ─────────────────────────────────────────────────────────────
    # Séparateur de début
    # ─────────────────────────────────────────────────────────────
    lines.append(colorize_section_separator(length=100, key="color_text_dim"))

    # ─────────────────────────────────────────────────────────────
    # Section Usage
    # ─────────────────────────────────────────────────────────────
    lines.append("")
    lines.append(colorize_section_title("📖", "Usage", key="usage"))
    lines.append("")

    for pattern in usage_patterns:
        # Initialiser colored_pattern avec le pattern original
        colored_pattern = pattern
        # Colorer les éléments clés du pattern dans l'ordre logique de la ligne de commande
        colored_pattern = colored_pattern.replace(
            "<COMMAND>",
            colorize("<COMMAND>", "color_usage"),
        )
        colored_pattern = colored_pattern.replace(
            "<COMMANDE>",
            colorize("<COMMANDE>", "color_usage"),
        )
        colored_pattern = colored_pattern.replace(
            "[OPTIONS_COMMAND]",
            f"[{colorize('OPTIONS_COMMAND', 'color_action_options')}]",
        )
        colored_pattern = colored_pattern.replace(
            "[OPTIONS_COMMANDE]",
            f"[{colorize('OPTIONS_COMMANDE', 'color_action_options')}]",
        )
        colored_pattern = colored_pattern.replace(
            "[OPTIONS_GLOBALES]",
            f"[{colorize('OPTIONS_GLOBALES', 'color_global_options')}]",
        )
        colored_pattern = colored_pattern.replace(
            "[OPTIONS_CATEGORIE]",
            f"[{colorize('OPTIONS_CATEGORIE', 'color_category_options')}]",
        )
        colored_pattern = colored_pattern.replace(
            "<CATEGORIE>",
            colorize("<CATEGORIE>", "color_category"),
        )
        # Traiter category en dernier pour éviter les conflits avec "alexa"
        if category != "alexa":
            colored_pattern = colored_pattern.replace(
                category,
                colorize(category, "color_category"),
            )
        colored_pattern = colored_pattern.replace(
            "<ACTION>",
            colorize("<ACTION>", "color_action"),
        )
        colored_pattern = colored_pattern.replace(
            "[OPTIONS_ACTION]",
            f"[{colorize('OPTIONS_ACTION', 'color_action_options')}]",
        )
        # Traiter "alexa" en dernier pour qu'il garde sa couleur gris gras
        colored_pattern = colored_pattern.replace(
            "alexa",
            colorize("alexa", "color_text_dim"),
        )

        lines.append(f"  {colored_pattern}")

    # ─────────────────────────────────────────────────────────────
    # Structure spéciale pour l'aide principale (alexa)
    # ─────────────────────────────────────────────────────────────
    if category == "alexa":
        # Section Options globales
        lines.append("")
        lines.append(colorize("Options globales :", "gray"))
        lines.append("")
        lines.append("  • --verbose, -v                   : Mode verbeux (affiche logs détaillés)")
        lines.append("  • --debug                         : Mode debug (affiche tous les logs)")
        lines.append("  • --json                          : Sortie au format JSON")
        lines.append("  • --no-color                      : Désactiver la coloration ANSI")
        lines.append("  • --config CONFIG                 : Fichier de configuration personnalisé")
        lines.append("  • --help, -h                      : Afficher l'aide contextuelle")

        # Section Catégorie et options
        lines.append("")
        lines.append(colorize("Catégorie et options :", "category"))
        lines.append("")

        # Calculer la colonne d'alignement pour les catégories
        max_category_length = max(len(a.get("name", "")) for a in actions) if actions else 0
        align_column = max(50, max_category_length + 10)

        for action_dict in actions:
            name = action_dict.get("name", "")
            description = action_dict.get("description", "")
            line = colorize_category_line(name, description, align_column)
            lines.append(line)

            # Récupérer les vraies actions pour cette catégorie et afficher les options
            category_actions = get_category_actions(name)
            if category_actions:
                # Prendre seulement les 2-3 premières actions pour ne pas surcharger
                for action in category_actions[:3]:
                    action_options = action.get("options", "")
                    if action_options:
                        # Diviser les options par virgule et prendre les 2-3 premières
                        option_parts = [opt.strip() for opt in action_options.split(",") if opt.strip()][:3]
                        for opt in option_parts:
                            # Colorer l'option avec la couleur category_options (vert non bold)
                            opt_colored = colorize(opt, "color_category_options")
                            lines.append(f"    └─ {opt_colored}")
                # Ajouter "..." si il y a plus d'actions
                if len(category_actions) > 3:
                    lines.append(f"    └─ {colorize('...', 'color_text_dim')}")
            lines.append("")  # Ligne vide après chaque catégorie

        # Section Actions et options
        lines.append("")
        lines.append(colorize("Actions et options :", "action"))
        lines.append("")
        lines.append("  • <ACTION>                        : Action à exécuter selon la catégorie")
        lines.append("  • [OPTIONS_ACTION]                : Options spécifiques à l'action")

        # Section Commandes et options
        lines.append("")
        lines.append(colorize("Commandes et options :", "usage"))
        lines.append("")
        lines.append("  • <COMMAND>                       : Commande principale à exécuter")
        lines.append("  • [OPTIONS_COMMAND]               : Options spécifiques à la commande")

    else:
        # Structure normale pour les autres catégories
        # ─────────────────────────────────────────────────────────────
        # Section Actions disponibles
        # ─────────────────────────────────────────────────────────────
        lines.append("")
        lines.append(colorize_section_title("⚡", "Actions et options disponibles", key="action"))
        lines.append("")

        # Calculer la colonne d'alignement
        max_action_length = max(len(a.get("name", "")) for a in actions) if actions else 0
        align_column = max(50, max_action_length + 10)

        for action_dict in actions:
            name = action_dict.get("name", "")
            description = action_dict.get("description", "")
            options = action_dict.get("options", "")

            # Ligne principale de l'action
            action_colored = colorize(name, "action")
            description_colored = colorize(description, "color_text_dim")
            action_line = f"  • {action_colored} : {description_colored}"
            lines.append(action_line)

            # Sous-liste des options si elles existent
            if options:
                # Diviser les options par virgule et nettoyer
                option_parts = [opt.strip() for opt in options.split(",") if opt.strip()]
                for opt in option_parts:
                    # Colorer l'option avec la couleur category_options (vert non bold)
                    opt_colored = colorize(opt, "color_category_options")
                    lines.append(f"    └─ {opt_colored}")

        # ─────────────────────────────────────────────────────────────
        # Section Exemples
        # ─────────────────────────────────────────────────────────────
        lines.append("")
        lines.append(colorize_section_title("💡", "Exemples d'utilisation", key="usage"))
        lines.append("")

        for example in examples:
            lines.append(f"  {colorize_example(example)}")

        # Ajouter des exemples avec options globales
        lines.append("")
        lines.append(colorize("Avec une option globale :", "color_text_dim"))
        lines.append("")
        lines.append(f"  {colorize_example(f'alexa --verbose {category} list')}")
        lines.append(f"  {colorize_example(f'alexa --debug {category} list')}")

    # ─────────────────────────────────────────────────────────────
    # Section Prérequis (commun à tous)
    # ─────────────────────────────────────────────────────────────
    if prerequisites:
        lines.append("")
        lines.append(colorize_section_title("⚠️", "Prérequis essentiels", key="color_text_dim"))
        lines.append("")

        for prereq in prerequisites:
            lines.append(f"  • {colorize(prereq, 'color_text_dim')}")

    # ─────────────────────────────────────────────────────────────
    # Section Pour plus d'aide (commun à tous)
    # ─────────────────────────────────────────────────────────────
    lines.append("")
    lines.append(colorize("Pour plus de détails:", "color_text_dim"))
    lines.append(f"  {colorize_example('alexa --help-web')}")
    lines.append(f"  {colorize_example('alexa -hw')}")

    # ─────────────────────────────────────────────────────────────
    # Séparateur de fin
    # ─────────────────────────────────────────────────────────────
    lines.append("")
    lines.append(colorize_section_separator(length=100, key="color_text_dim"))

    return "\n".join(lines)


def generate_short_description(category: str, title: str) -> str:
    """Génère une courte description pour une catégorie (utilisée par argparse).

    Args:
        category: Nom de la catégorie
        title: Titre complet

    Returns:
        Description courte.
    """
    return f"Aide pour la catégorie '{category}' — {title.lower()}"
