"""
Formateur d'aide courte pour les commandes CLI.

Ce module génère des aides courtes et colorées pour le flag -h/--help.
Format concis avec sections : Usage, Actions possibles, Exemples.
"""

import argparse
from typing import Dict, List, Optional

from utils.logger import SharedIcons


class ShortHelpFormatter:
    """Générateur d'aide courte avec couleurs ANSI."""

    # Codes couleur ANSI
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Couleurs pour différents types de contenu
    COLOR_HEADER = "\033[1;36m"  # Cyan bold pour les headers
    COLOR_USAGE = "\033[1;33m"  # Jaune bold pour usage
    COLOR_ACTION = "\033[1;32m"  # Vert bold pour actions
    COLOR_OPTION = "\033[1;35m"  # Magenta bold pour options
    COLOR_EXAMPLE = "\033[0;37m"  # Blanc pour exemples
    COLOR_DESCRIPTION = "\033[0;90m"  # Gris pour descriptions
    COLOR_SEPARATOR = "\033[0;36m"  # Cyan pour séparateurs

    @staticmethod
    def _separator(length: int = 120) -> str:
        """Génère une ligne de séparation."""
        return f"{ShortHelpFormatter.COLOR_SEPARATOR}{'━' * length}{ShortHelpFormatter.RESET}"

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

        # Separator top
        lines.append(ShortHelpFormatter._separator())
        lines.append(f"{emoji} {ShortHelpFormatter.BOLD}{title}{ShortHelpFormatter.RESET}")
        lines.append(ShortHelpFormatter._separator())
        lines.append("")

        # Section Usage
        lines.append(ShortHelpFormatter._header(SharedIcons.DOCUMENT, "Usage:"))
        lines.append(ShortHelpFormatter._separator())
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
        for action_info in actions:
            action = action_info.get("action", "")
            description = action_info.get("description", "")

            # Colorer l'action en vert et la description en gris
            colored_action = f"{ShortHelpFormatter.COLOR_ACTION}{action}{ShortHelpFormatter.RESET}"
            colored_desc = (
                f"{ShortHelpFormatter.COLOR_DESCRIPTION}: {description}{ShortHelpFormatter.RESET}"
            )

            lines.append(f"  • {colored_action:<70} {colored_desc}")
        lines.append("")

        # Section Exemples
        lines.append("Exemple :")
        lines.append("")
        for example in examples:
            lines.append(f"  {ShortHelpFormatter.COLOR_EXAMPLE}{example}{ShortHelpFormatter.RESET}")

        # Exemples avec options globales
        if global_examples:
            lines.append("")
            lines.append("  Avec une option globale :")
            lines.append("")
            for example in global_examples:
                lines.append(
                    f"\t{ShortHelpFormatter.COLOR_EXAMPLE}{example}{ShortHelpFormatter.RESET}"
                )

        lines.append("")

        # Hint pour aide web
        if web_help_hint:
            lines.append(ShortHelpFormatter._separator())
            lines.append(
                f"{ShortHelpFormatter.COLOR_HEADER}📚 Documentation complète : "
                f"{ShortHelpFormatter.COLOR_USAGE}alexa {category} --help-web{ShortHelpFormatter.RESET}"
            )
            lines.append(ShortHelpFormatter._separator())

        return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 ARGPARSE FORMATTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ShortHelpArgparseFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter argparse personnalisé pour n'afficher que la description.
    Masque toutes les sections générées automatiquement (positional arguments, options).
    """

    def format_help(self):
        """N'affiche que la description personnalisée."""
        # Récupérer le parser parent pour accéder à la description
        if hasattr(self, "_prog") and hasattr(self, "_root_section"):
            formatter = self._root_section.formatter
            if hasattr(formatter, "_current_section"):
                # Afficher uniquement la description
                help_text = []
                if self._root_section.heading:
                    help_text.append(self._format_text(self._root_section.heading))
                return "\n".join(help_text)

        # Fallback: afficher simplement la description du parser
        # On récupère la description depuis l'attribut de la classe parente
        return self._root_section.format_help() if hasattr(self, "_root_section") else ""


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
