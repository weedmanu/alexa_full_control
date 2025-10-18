"""
Formateur d'aide courte pour les commandes CLI.

Ce module génère des aides courtes et colorées pour le flag -h/--help.
Format concis avec sections : Usage, Actions possibles, Exemples.
"""

import argparse
from typing import Dict, List, Optional

from utils.logger import SharedIcons
from utils.term import Colors


class ShortHelpFormatter:
    """Générateur d'aide courte avec couleurs ANSI."""

    # Codes couleur ANSI - utilisation centralisée depuis term.Colors
    RESET = Colors.RESET
    BOLD = Colors.BOLD

    # Couleurs pour différents types de contenu
    COLOR_HEADER = Colors.CYAN_BOLD  # Cyan bold pour les headers
    COLOR_USAGE = Colors.YELLOW_BOLD  # Jaune bold pour usage
    COLOR_ACTION = Colors.GREEN_BOLD  # Vert bold pour actions
    COLOR_OPTION = Colors.MAGENTA_BOLD  # Magenta bold pour options
    COLOR_EXAMPLE = Colors.WHITE_BOLD  # Blanc pour exemples
    COLOR_DESCRIPTION = Colors.GRAY  # Gris pour descriptions
    COLOR_SEPARATOR = Colors.CYAN  # Cyan pour séparateurs

    @staticmethod
    def _separator(length: int = 120) -> str:
        """Génère une ligne de séparation."""
        # Legacy: keep API but return empty (we prefer short discrete lines).
        return ""

    @staticmethod
    def _short_line(length: int = 40) -> str:
        """Génère une ligne courte et discrète pour séparer les sections."""
        l = max(0, min(length, 40))
        return f"{ShortHelpFormatter.COLOR_SEPARATOR}{'─' * l}{ShortHelpFormatter.RESET}"

    @staticmethod
    def _header(emoji: str, title: str) -> str:
        """Génère un header de section."""
        return f"{ShortHelpFormatter.COLOR_HEADER}{emoji} {title}{ShortHelpFormatter.RESET}"

    @staticmethod
    def format_short_help(
        category: str,
        emoji: str,
        title: str,
        usage_patterns: List[str],
        actions: List[Dict[str, str]],
        examples: List[str],
        global_examples: Optional[List[str]] = None,
        web_help_hint: bool = True,
    ) -> str:
        """
        Génère une aide courte formatée.

        Args:
            category: Nom de la catégorie (ex: "device")
            emoji: Emoji pour le header (ex: "📱")
            title: Titre de la section (ex: "DEVICE - Gestion des appareils")
            usage_patterns: Patterns d'usage (ex: ["alexa [OPTIONS_GLOBALES] device <ACTION> [OPTIONS_ACTION]"])
            actions: Liste des actions avec descriptions
                     Format: [{"action": "list", "description": "Lister tous les appareils"}, ...]
            examples: Liste des exemples de commandes
            global_examples: Exemples avec options globales (optionnel)
            web_help_hint: Afficher le hint pour --help-web

        Returns:
            Aide courte formatée avec couleurs ANSI
        """
        lines = []

        # Determine terminal width to size separators and wrapping
        try:
            import shutil

            term_width = shutil.get_terminal_size((80, 20)).columns
        except Exception:
            term_width = 80

        # We'll compute the effective content width and make separators adapt to it
        content_width = min(term_width, 120)

        # Title header (no heavy separators)
        lines.append(f"{emoji} {ShortHelpFormatter.BOLD}{title}{ShortHelpFormatter.RESET}")
        lines.append("")

        # Section Usage
        lines.append(ShortHelpFormatter._header(SharedIcons.DOCUMENT, "Usage:"))
        lines.append("")
        lines.append("Champs possible :")
        lines.append("")
        for pattern in usage_patterns:
            # Colorer les différentes parties de l'usage
            colored_pattern = (
                pattern.replace(
                    "[OPTIONS_GLOBALES]",
                    f"{ShortHelpFormatter.COLOR_OPTION}[OPTIONS_GLOBALES]{ShortHelpFormatter.RESET}",
                )
                .replace(
                    "<ACTION>",
                    f"{ShortHelpFormatter.COLOR_ACTION}<ACTION>{ShortHelpFormatter.RESET}",
                )
                .replace(
                    "[OPTIONS_ACTION]",
                    f"{ShortHelpFormatter.COLOR_OPTION}[OPTIONS_ACTION]{ShortHelpFormatter.RESET}",
                )
                .replace(
                    "<COMMANDE>",
                    f"{ShortHelpFormatter.COLOR_ACTION}<COMMANDE>{ShortHelpFormatter.RESET}",
                )
                .replace(
                    "[OPTION_COMMANDE]",
                    f"{ShortHelpFormatter.COLOR_OPTION}[OPTION_COMMANDE]{ShortHelpFormatter.RESET}",
                )
            )
            lines.append(f"  {colored_pattern}")
        lines.append("")

        # Section Actions possibles
        lines.append("Actions possibles :")
        lines.append("")
        # Calculer la largeur d'alignement dynamiquement : s'aligner sur la
        # longueur de la plus longue action (ex: "device communicate") et
        # ajouter un petit padding. Limiter quand même à 60 cols pour éviter
        # des mises en page trop larges.
        max_len = max((len(a.get("action", "")) for a in actions), default=0)
        align_width = max(10, min(60, max_len + 2))

        # Reserve space: bullet + spaces + action column + space
        reserved = 4 + align_width + 1
        desc_max = max(20, min(content_width - reserved, 80))

        # Prepare wrapper for descriptions
        import textwrap

        for action_info in actions:
            action = action_info.get("action", "")
            description = action_info.get("description", "") or ""

            # Normalize description: remove repetitive prefixes like
            # "Commande pour", "Commande de", "Commande" which sont
            # souvent verbeux et inutiles in the compact help.
            import re

            plain_desc = description.strip()
            # Use IGNORECASE flag instead of inline (?i) which must be at start
            plain_desc = re.sub(r'^(?:commande(?:s)?(?:\s+(?:pour|de))?)\s*[:\-]?\s*', '', plain_desc, flags=re.IGNORECASE)

            # Support explicit paragraph breaks in descriptions (\n).
            # Wrap each paragraph separately to preserve intentional newlines.
            wrapped = []
            for para in plain_desc.splitlines():
                if not para.strip():
                    # keep blank paragraph as a visual break
                    wrapped.append("")
                    continue
                parts = textwrap.wrap(
                    para, width=desc_max, break_long_words=False, break_on_hyphens=False
                )
                if parts:
                    wrapped.extend(parts)
                else:
                    wrapped.append("")

            # Colorer l'action en vert (colorer uniquement le texte, ajouter la
            # padding séparément pour s'aligner sur la longueur visible)
            action_len = len(action)
            colored_action = f"{ShortHelpFormatter.COLOR_ACTION}{action}{ShortHelpFormatter.RESET}"
            padding = " " * max(0, align_width - action_len)

            # Première ligne avec action et première partie de description
            first_desc = wrapped[0]
            colored_desc_first = f"{ShortHelpFormatter.COLOR_DESCRIPTION}: {first_desc}{ShortHelpFormatter.RESET}"
            lines.append(f"  • {colored_action}{padding} {colored_desc_first}")

            # Lignes suivantes (si wrap) alignées sous la description
            if len(wrapped) > 1:
                # Align continuation lines under the description column.
                # Prefix consists of: two spaces, bullet, space => 4 chars, plus
                # the action column (align_width) and one separating space.
                indent = 4 + align_width + 1
                for cont in wrapped[1:]:
                    lines.append(" " * indent + f"{ShortHelpFormatter.COLOR_DESCRIPTION}{cont}{ShortHelpFormatter.RESET}")
        lines.append("")

        # (Exemples et options globales retirés pour un -h compact)

        # Hint pour aide web
        if web_help_hint:
            doc_header = f"{ShortHelpFormatter.COLOR_HEADER}📚 Documentation complète : "
            doc_link = f"{ShortHelpFormatter.COLOR_USAGE}alexa {category} --help-web{ShortHelpFormatter.RESET}"
            lines.append(doc_header + doc_link)

        return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 ARGPARSE FORMATTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ShortHelpArgparseFormatter removed: we use UniversalHelpFormatter for argparse formatting.


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 FONCTIONS UTILITAIRES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def strip_ansi_codes(text: str) -> str:
    """
    Supprime les codes ANSI d'un texte (pour tests ou export).

    Args:
        text: Texte avec codes ANSI

    Returns:
        Texte sans codes ANSI
    """
    import re

    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)
