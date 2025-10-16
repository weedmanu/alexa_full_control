"""Système centralisé de coloration ANSI pour la CLI.

Ce module centralise TOUTES les opérations de coloration métier (business-logic),
garantissant une API uniforme pour formatage des sections d'aide.

Architecture claire:
- term.py       : Infrastructure ANSI brute (Colors, COLOR_KEY_MAP, span, should_colorize)
- colorizer.py  : API métier (formatage de sections, lignes, exemples, etc.)

Tous les fichiers help_texts et command_parser utilisent UNIQUEMENT ce module.
"""

from typing import List, Optional

from utils.term import COLOR_KEY_MAP, Colors, should_colorize, span

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 API DE COLORATION MÉTIER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def colorize(text: str, key: str) -> str:
    """Alias de span() pour cohérence avec l'API CLI.

    Délègue directement à span() de term.py.
    """
    if not should_colorize(no_color=False):
        return text
    return span(text, key)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 HELPERS DE FORMATAGE MÉTIER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def colorize_section_separator(length: int = 100, key: str = "color_text_dim") -> str:
    """Génère une ligne de séparation colorée.

    Args:
        length: Longueur de la ligne de séparation
        key: Clé sémantique pour la couleur (color_text_dim par défaut)

    Returns:
        Ligne de séparation colorée.
    """
    separator = "━" * length
    return colorize(separator, key)


def colorize_section_title(emoji: str, title: str, key: str = "color_usage") -> str:
    """Génère un titre de section standardisé coloré.

    Args:
        emoji: Emoji pour le titre (ex: "📖", "⚡", "💡")
        title: Titre de la section (ex: "Usage", "Actions disponibles")
        key: Clé sémantique pour la couleur

    Returns:
        Titre formaté et coloré.
    """
    title_colored = colorize(title + ":", key)
    return f"{emoji} {title_colored}"


def colorize_usage_line(
    category: str,
    action: Optional[str] = None,
    global_options: bool = True,
    action_options: bool = True,
) -> str:
    """Génère une ligne d'usage colorée selon le schéma standardisé.

    Format: alexa [OPTIONS_GLOBALES] <CATEGORIE> [<ACTION>] [OPTIONS_ACTION]

    Args:
        category: Nom de la catégorie (ex: "device")
        action: Nom de l'action si applicable (ex: "list")
        global_options: Afficher [OPTIONS_GLOBALES]
        action_options: Afficher [OPTIONS_ACTION]

    Returns:
        Ligne d'usage colorée.
    """
    parts = [colorize("alexa", "color_text_dim")]

    if global_options:
        parts.append(f"[{colorize('OPTIONS_GLOBALES', 'color_action_options')}]")

    parts.append(colorize(category, "color_category"))

    if action:
        parts.append(colorize(action, "color_action"))

    if action_options:
        parts.append(f"[{colorize('OPTIONS_ACTION', 'color_action_options')}]")

    return " ".join(parts)


def colorize_action_line(
    action: str,
    description: str,
    align_column: int = 50,
    option_suffix: str = "",
) -> str:
    """Formate et colore une ligne d'action.

    Exemple output:
    • list                                              : Lister tous les appareils

    Args:
        action: Nom de l'action (ex: "list")
        description: Description de l'action
        align_column: Colonne d'alignement pour la description
        option_suffix: Suffixe optionnel (ex: " --refresh", " --filter")

    Returns:
        Ligne d'action formatée et colorée.
    """
    action_colored = colorize(action, "color_action")
    if option_suffix:
        option_colored = colorize(option_suffix, "color_action_options")
        action_part = action_colored + " " + option_colored
    else:
        action_part = action_colored

    description_colored = colorize(description, "color_text_dim")

    # Alignement : compléter avec des espaces jusqu'à align_column
    padding = max(0, align_column - len(action_part))
    return f"  • {action_part}{' ' * padding} : {description_colored}"


def colorize_category_line(
    category: str,
    description: str,
    align_column: int = 50,
    option_suffix: str = "",
) -> str:
    """Formate et colore une ligne de catégorie (pour l'aide principale).

    Exemple output:
    • auth                                              : Authentification et gestion des tokens

    Args:
        category: Nom de la catégorie (ex: "auth")
        description: Description de la catégorie
        align_column: Colonne d'alignement pour la description
        option_suffix: Suffixe optionnel

    Returns:
        Ligne de catégorie formatée et colorée.
    """
    category_colored = colorize(
        category, "color_category"
    )  # Utilise "color_category" (vert) au lieu de "action" (bleu)
    if option_suffix:
        option_colored = colorize(option_suffix, "color_action_options")
        category_part = category_colored + " " + option_colored
    else:
        category_part = category_colored

    description_colored = colorize(description, "color_text_dim")

    # Alignement : compléter avec des espaces jusqu'à align_column
    padding = max(0, align_column - len(category_part))
    return f"  • {category_part}{' ' * padding} : {description_colored}"


def colorize_option_line(
    flag: str,
    metavar: Optional[str] = None,
    description: str = "",
    align_column: int = 50,
) -> str:
    """Formate et colore une ligne d'option.

    Exemple output:
    -v, --verbose                                       : Mode verbeux

    Args:
        flag: Drapeau d'option (ex: "-v, --verbose")
        metavar: Métavariable si applicable (ex: "LEVEL")
        description: Description de l'option
        align_column: Colonne d'alignement pour la description

    Returns:
        Ligne d'option formatée et colorée.
    """
    flag_colored = colorize(flag, "color_action_options")

    if metavar:
        metavar_colored = colorize(metavar, "color_action")
        flag_part = f"{flag_colored} {metavar_colored}"
    else:
        flag_part = flag_colored

    description_colored = colorize(description, "color_text_dim")

    # Alignement
    padding = max(0, align_column - len(flag_part))
    return f"  {flag_part}{' ' * padding} : {description_colored}"


def colorize_example(command: str) -> str:
    """Formate et colore une ligne d'exemple de commande.

    Exemple output:
    alexa device list --refresh

    Args:
        command: Commande complète (ex: "alexa device list --refresh")

    Returns:
        Commande formatée avec coloration partielle.
    """
    # Remplacer les éléments connus avec leurs couleurs respectives
    result = command.replace("alexa", colorize("alexa", "color_text_dim"))

    # Colorer les catégories (mots après "alexa" s'il y a un espace)
    # Ceci est simplifié : on pourrait parser plus sophistiqué au besoin
    for cat in [
        "device",
        "auth",
        "alarm",
        "music",
        "activity",
        "reminder",
        "routine",
        "calendar",
        "lists",
        "multiroom",
        "announcement",
        "dnd",
        "cache",
        "smarthome",
        "timers",
        "notification",
    ]:
        result = result.replace(f" {cat} ", f" {colorize(cat, 'color_category')} ")

    # Colorer les drapeaux (--...)
    import re

    result = re.sub(r"(--?\w+)", lambda m: colorize(m.group(1), "color_action_options"), result)

    return result


def colorize_bullet_list(
    items: List[str],
    key: str = "color_text_dim",
) -> str:
    """Colore une liste à puces.

    Args:
        items: Liste de textes
        key: Clé sémantique pour la couleur

    Returns:
        Texte avec puces colorées.
    """
    result: List[str] = []
    for item in items:
        item_colored = colorize(item, key)
        result.append(f"  • {item_colored}")
    return "\n".join(result)


def strip_colors(text: str) -> str:
    """Supprime tous les codes couleur ANSI d'un texte.

    Utile pour: tests, logs, exports sans couleur.

    Args:
        text: Texte avec codes ANSI

    Returns:
        Texte sans codes ANSI.
    """
    import re

    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏗️ GÉNÉRATEURS DE SECTIONS COMPLÈTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def generate_help_section(
    emoji: str,
    title: str,
    content_lines: List[str],
    title_key: str = "color_usage",
    separator_char: str = "━",
    separator_length: int = 100,
) -> str:
    """Génère une section d'aide standardisée (séparateurs + titre + contenu).

    Args:
        emoji: Emoji pour le titre
        title: Titre de la section
        content_lines: Lignes de contenu (déjà formatées)
        title_key: Clé sémantique pour le titre
        separator_char: Caractère de séparation ("━" ou "─")
        separator_length: Longueur de la séparation

    Returns:
        Section complète avec bordures.
    """
    separator_colored = colorize(separator_char * separator_length, "color_text_dim")
    title_colored = colorize_section_title(emoji, title, title_key)

    content = "\n".join(content_lines)

    return f"\n{separator_colored}\n{title_colored}\n{separator_colored}\n\n{content}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✨ RÉEXPORTS (pour compatibilité avec code existant)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Réexporter les utilitaires de term.py pour accès centralisé
__all__ = [
    "colorize",
    "colorize_section_separator",
    "colorize_section_title",
    "colorize_usage_line",
    "colorize_action_line",
    "colorize_category_line",
    "colorize_option_line",
    "colorize_example",
    "colorize_bullet_list",
    "generate_help_section",
    "strip_colors",
    "COLOR_KEY_MAP",
    "Colors",
]
