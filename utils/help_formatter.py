"""
Système modulaire de formatage des aides CLI.

Ce module centralise tout le formatage des sections d'aide pour garantir
une cohérence visuelle parfaite à travers tous les niveaux de -h.

ARCHITECTURE DES FONCTIONS DE FORMATAGE
========================================

Chaque champ de la ligne d'usage possède sa propre fonction de formatage :

Usage complet : alexa [OPTIONS_GLOBALES] <CATEGORIE> [OPTIONS_CATEGORIE] [<SOUS-CATEGORIE>] [OPTIONS_SOUS-CATEGORIE] [<ACTION>] [OPTIONS_ACTION]

Fonctions par champ de la ligne d'usage :
------------------------------------------
1. OPTIONS_GLOBALES (magenta clair)     → format_global_options()
2. CATEGORIE (vert gras)                → format_current_category(name, desc, emoji)
3. OPTIONS_CATEGORIE (vert clair)       → format_category_options(text)
4. SOUS-CATEGORIE (cyan gras)           → format_current_subcategory(name, desc, emoji)
5. OPTIONS_SOUS-CATEGORIE (cyan clair)  → format_subcategory_options(text)
6. ACTION (orange gras)                 → format_actions(actions_list)
7. OPTIONS_ACTION (orange clair)        → format_action_options(options_list)

Fonctions pour listes (aide principale) :
-----------------------------------------
- format_categories(list)               → Liste de toutes les catégories (pour alexa -h)
- format_subcategories(list)            → Liste de toutes les sous-catégories (pour alexa -h)

Autres fonctions communes :
---------------------------
- format_header(emoji, title)           → En-tête principal
- format_features(items, show_title)    → Fonctionnalités
- format_usage(category, subcategory, action, is_main) → Ligne d'usage
- format_examples(examples)             → Exemples d'utilisation
- format_prerequisites(prereqs)         → Prérequis essentiels
- format_more_help_main()               → Section aide (alexa -h uniquement)
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 PALETTE DE COULEURS STANDARDISÉE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Colors:
    """Codes ANSI pour la colorisation standardisée."""
    
    # Couleurs de base
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Couleurs des sections (cohérentes partout)
    GRAY_BOLD = '\033[1;90m'        # 🎯 Fonctionnalités, 💡 Aide, alexa
    CYAN_BOLD = '\033[1;36m'        # 🎯 Sous-catégories, 📖 Usage
    CYAN = '\033[0;36m'  # Options de sous-catégories (plus clair)
    MAGENTA_BOLD = '\033[1;35m'     # 🔧 Titre Options globales
    MAGENTA = '\033[0;35m'  # Options globales (pas en gras)
    GREEN_BOLD = '\033[1;32m'       # 📂 Catégories
    GREEN = '\033[0;32m' # Options de catégories (plus clair)
    ORANGE_BOLD = '\033[1;38;5;208m'  # ⚡ Actions
    ORANGE = '\033[0;38;5;208m'  # Options d'actions (plus clair)
    YELLOW_BOLD = '\033[1;33m'      # 📋 Exemples
    WHITE_BOLD = '\033[1;37m'       # Texte normal, aide
    RED_BOLD = '\033[1;31m'         # ⚠️ Prérequis, erreurs


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏗️ COMPOSANTS DE BASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class HelpComponents:
    """Composants réutilisables pour construire les sections d'aide."""
    
    @staticmethod
    def header(icon: str, title: str) -> str:
        """Crée un en-tête principal imposant avec texte en gras et plus gros."""
        border = "━" * 100
        # Utiliser BOLD pour rendre le titre plus imposant
        full_title = f"{Colors.BOLD}{icon}  {title.upper()}{Colors.RESET}"
        # Centrer le titre (comptage sans les codes ANSI)
        visible_length = len(icon) + 2 + len(title)
        padding = (100 - visible_length) // 2
        centered_title = " " * padding + full_title
        return f"\n{border}\n{centered_title}\n{border}"
    
    @staticmethod
    def section_title(emoji: str, title: str, color: str = Colors.GRAY_BOLD) -> str:
        """Crée un titre de section coloré avec séparateurs au-dessus et en dessous."""
        separator = f"{color}{'━' * 100}{Colors.RESET}"
        title_line = f"{color}{emoji} {title}:{Colors.RESET}"
        return f"\n{separator}\n{title_line}\n{separator}"
    
    @staticmethod
    def bullet_list(items: List[str], indent: str = "  ") -> str:
        """Crée une liste à puces."""
        return "\n".join(f"{indent}• {item}" for item in items)
    
    @staticmethod
    def option_list(options: List[Dict[str, str]], color: str = Colors.MAGENTA_BOLD) -> str:
        """Crée une liste d'options formatées."""
        lines = []
        for opt in options:
            flag = f"{color}{opt['flag']}{Colors.RESET}"
            padding = " " * (35 - len(opt['flag']))
            desc = opt['description']
            lines.append(f"  {flag}{padding}: {desc}")
        return "\n".join(lines)
    
    @staticmethod
    def usage_line(
        command: str,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        action: Optional[str] = None,
        subactions: Optional[str] = None,
        is_main: bool = False
    ) -> str:
        """Crée une ligne d'usage avec couleurs syntaxiques.
        
        Args:
            command: Commande de base (ex: "alexa")
            category: Catégorie (ex: "device")
            subcategory: Sous-catégorie (ex: "playback")
            action: Action (ex: "volume")
            subactions: Sous-actions possibles (ex: "get|set")
            is_main: Si True, affiche l'usage général complet
        """
        parts = [f"{Colors.WHITE_BOLD}alexa{Colors.RESET}"]
        parts.append(f"[{Colors.MAGENTA}OPTIONS_GLOBALES{Colors.RESET}]")
        
        if is_main:
            # Pour l'aide principale : afficher la syntaxe complète avec toutes les options possibles
            # Utiliser des nuances : foncé pour les champs, clair pour leurs options
            parts.append(f"{Colors.GREEN_BOLD}<CATEGORIE>{Colors.RESET}")
            parts.append(f"[{Colors.GREEN}OPTIONS_CATEGORIE{Colors.RESET}]")
            parts.append(f"[{Colors.CYAN_BOLD}<SOUS-CATEGORIE>{Colors.RESET}]")
            parts.append(f"[{Colors.CYAN}OPTIONS_SOUS-CATEGORIE{Colors.RESET}]")
            parts.append(f"[{Colors.ORANGE_BOLD}<ACTION>{Colors.RESET}]")
            parts.append(f"[{Colors.ORANGE}OPTIONS_ACTION{Colors.RESET}]")
        else:
            # Pour les autres niveaux
            if category:
                parts.append(f"{Colors.GREEN_BOLD}{category}{Colors.RESET}")
                # Si pas d'action spécifiée, montrer que ACTION est requis
                if not action:
                    parts.append(f"{Colors.ORANGE_BOLD}<ACTION>{Colors.RESET}")
            if subcategory:
                parts.append(f"{Colors.CYAN_BOLD}{subcategory}{Colors.RESET}")
                # Si pas d'action spécifiée, montrer que ACTION est requis  
                if not action:
                    parts.append(f"{Colors.ORANGE_BOLD}<ACTION>{Colors.RESET}")
            if action:
                parts.append(f"{Colors.ORANGE_BOLD}{action}{Colors.RESET}")
                # Si l'action a des sous-actions (ex: volume get|set)
                if subactions:
                    parts.append(f"{Colors.ORANGE_BOLD}<{subactions}>{Colors.RESET}")
            parts.append(f"[{Colors.ORANGE}OPTIONS_ACTION{Colors.RESET}]")
        
        return " ".join(parts)
    
    @staticmethod
    def example(command: str) -> str:
        """Formate un exemple avec colorisation syntaxique.
        
        Supporte deux formats :
        - Ancien : "commande # description"
        - Nouveau : "commande : description"
        """
        # Séparer la commande de la description
        if ':' in command:
            # Nouveau format avec ':'
            cmd_part, desc_part = command.split(':', 1)
            description = f": {desc_part.strip()}"
        elif '#' in command:
            # Ancien format avec '#' (rétrocompatibilité)
            cmd_part, comment_part = command.split('#', 1)
            description = f"{Colors.GRAY_BOLD}#{comment_part}{Colors.RESET}"
        else:
            cmd_part = command
            description = ""
        
        # Parsing intelligent pour coloriser chaque partie
        parts = cmd_part.strip().split()
        colored_parts = []
        
        # Listes de mots-clés pour la colorisation
        categories = ["timers", "music", "device", "smarthome", "routine", "auth", "announcement", "activity", "cache", "lists", "dnd", "multiroom"]
        subcategories = ["countdown", "alarm", "reminder", "playback", "volume", "equalizer", "light", "thermostat", "security", "camera", "library", "tunein"]
        actions = [
            "create", "list", "delete", "update", "play", "pause", "stop", "on", "off", 
            "status", "refresh", "show", "set", "get", "enable", "disable", "info", 
            "send", "clear", "read", "add", "remove", "complete", "execute", "start",
            "cancel", "resume", "skip", "next", "previous", "mute", "unmute", "shuffle",
            "repeat", "search", "tune", "station"
        ]
        
        # Variable pour suivre si on a déjà vu une catégorie
        seen_category = False
        
        for i, part in enumerate(parts):
            if part == "alexa":
                colored_parts.append(f"{Colors.WHITE_BOLD}{part}{Colors.RESET}")
            elif part in ["--verbose", "--debug", "--json", "-v"]:
                # Options globales en magenta (pas en gras)
                colored_parts.append(f"{Colors.MAGENTA}{part}{Colors.RESET}")
            elif part.startswith("-"):
                # Toutes les autres options en orange clair (pas en gras)
                colored_parts.append(f"{Colors.ORANGE}{part}{Colors.RESET}")
            elif part in categories and not seen_category:
                # Catégories en vert (gras) - seulement si c'est la première après "alexa"
                colored_parts.append(f"{Colors.GREEN_BOLD}{part}{Colors.RESET}")
                seen_category = True
            elif part in subcategories:
                # Sous-catégories en cyan (gras)
                colored_parts.append(f"{Colors.CYAN_BOLD}{part}{Colors.RESET}")
            elif part in actions:
                # Actions en orange (gras)
                colored_parts.append(f"{Colors.ORANGE_BOLD}{part}{Colors.RESET}")
            elif part.startswith('"'):
                # Texte entre guillemets
                colored_parts.append(part)
            else:
                colored_parts.append(part)
        
        # Calculer le padding pour aligner les descriptions à la colonne 50
        cmd_str = " ".join(colored_parts)
        # Estimer la longueur visible (sans codes couleur)
        visible_length = len(" ".join(parts))
        # Aligner à la colonne 50 pour plus de lisibilité
        padding_needed = max(1, 50 - visible_length)
        padding = " " * padding_needed
        
        result = "  " + cmd_str
        if description:
            result += padding + description
        return result
    
    @staticmethod
    def example_with_alignment(text: str, align_column: int) -> str:
        """Formate un exemple avec alignement dynamique des descriptions.
        
        Args:
            text: Texte de l'exemple au format "commande : description"
            align_column: Colonne d'alignement pour les descriptions
        """
        if " : " not in text:
            return f"  {text}"
        
        parts = text.split(" : ", 1)
        cmd = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else ""
        
        # Découper la commande en mots
        words = cmd.split()
        colored_parts = []
        
        # Listes de mots clés pour colorisation
        categories = ["auth", "device", "music", "announcement", "routine", "activity", 
                     "smarthome", "lists", "timers", "multiroom", "dnd", "cache"]
        subcategories = ["countdown", "alarm", "reminder", "library", "playback", "tunein"]
        actions = ["login", "logout", "status", "list", "info", "volume", "create", "delete", 
                  "update", "play", "pause", "stop", "next", "previous", "shuffle", "repeat",
                  "track", "playlist", "radio", "queue", "on", "off", "set", "get", "enable",
                  "disable", "start", "cancel", "show", "clear", "refresh"]
        
        seen_category = False
        for part in words:
            if part == "alexa":
                colored_parts.append(f"{Colors.GRAY_BOLD}{part}{Colors.RESET}")
            elif part in categories and not seen_category:
                # Première occurrence d'un mot de catégorie -> c'est une catégorie
                colored_parts.append(f"{Colors.GREEN_BOLD}{part}{Colors.RESET}")
                seen_category = True
            elif part in subcategories:
                # Sous-catégories en cyan (gras)
                colored_parts.append(f"{Colors.CYAN_BOLD}{part}{Colors.RESET}")
            elif part in actions:
                # Actions en orange (gras)
                colored_parts.append(f"{Colors.ORANGE_BOLD}{part}{Colors.RESET}")
            elif part.startswith('"'):
                # Texte entre guillemets
                colored_parts.append(part)
            else:
                colored_parts.append(part)
        
        # Calculer le padding pour aligner les descriptions
        cmd_str = " ".join(colored_parts)
        # Estimer la longueur visible (sans codes couleur)
        visible_length = len(" ".join(words))
        # Utiliser la colonne d'alignement fournie
        padding_needed = max(1, align_column - visible_length)
        padding = " " * padding_needed
        
        result = "  " + cmd_str
        if description:
            result += padding + ": " + description
        return result
    
    @staticmethod
    def warning_prereq() -> str:
        """Emoji d'avertissement avec double espace (standard)."""
        return f"{Colors.RED_BOLD}⚠️  Prérequis essentiels:{Colors.RESET}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 FONCTIONS DE FORMATAGE PAR SECTION (RÉUTILISABLES)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_header(icon: str, title: str) -> str:
    """Formate un header principal centré avec bordures."""
    comp = HelpComponents()
    return comp.header(icon, title)


def format_features(items: List[str], emoji: str = "✨", title: str = "Fonctionnalités principales", show_title: bool = True) -> str:
    """Formate une section de fonctionnalités avec titre encadré."""
    comp = HelpComponents()
    
    if show_title:
        separator = f"{Colors.GRAY_BOLD}{'━' * 100}{Colors.RESET}"
        title_line = f"{Colors.GRAY_BOLD}{emoji} {title}:{Colors.RESET}"
        content = comp.bullet_list(items)
        return f"{separator}\n{title_line}\n{separator}\n\n{content}"
    else:
        # Pour l'aide principale, juste le contenu sans titre
        content = comp.bullet_list(items)
        return f"\n{content}"


def format_architecture(items: List[str]) -> str:
    """Formate une section architecture avec titre encadré."""
    comp = HelpComponents()
    separator = f"{Colors.GRAY_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.GRAY_BOLD}🏗️ Architecture modulaire:{Colors.RESET}"
    content = comp.bullet_list(items)
    return f"{separator}\n{title_line}\n{separator}\n\n{content}"


def format_usage(category: Optional[str] = None, subcategory: Optional[str] = None, 
                 action: Optional[str] = None, subactions: Optional[str] = None, is_main: bool = False) -> str:
    """Formate une section usage avec titre encadré.
    
    Args:
        category: Nom de la catégorie (ex: "device")
        subcategory: Nom de la sous-catégorie (ex: "playback")
        action: Nom de l'action (ex: "volume")
        subactions: Sous-actions possibles (ex: "get|set")
        is_main: Si True, affiche l'usage général complet
    """
    comp = HelpComponents()
    title_text = "Usage général" if is_main else "Usage"
    separator = f"{Colors.WHITE_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.WHITE_BOLD}📖 {title_text}:{Colors.RESET}"
    usage = comp.usage_line("alexa", category, subcategory, action, subactions, is_main)
    return f"{separator}\n{title_line}\n{separator}\n\n  {usage}"


def format_global_options(include_help_version: bool = True, category: Optional[str] = None) -> str:
    """Formate la section des options globales avec titre encadré.
    
    Args:
        include_help_version: Si False, n'affiche que les modificateurs de comportement
                             (pour les aides de catégories)
        category: Nom de la catégorie pour afficher des exemples contextuels (ex: "auth")
    """
    comp = HelpComponents()
    separator = f"{Colors.MAGENTA_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.MAGENTA_BOLD}🔧 Options globales disponibles:{Colors.RESET}"
    
    alexa_cmd = f"{Colors.GRAY_BOLD}alexa{Colors.RESET}"
    verbose_opt = f"{Colors.MAGENTA}-v, --verbose{Colors.RESET}"
    debug_opt = f"{Colors.MAGENTA}--debug{Colors.RESET}"
    json_opt = f"{Colors.MAGENTA}--json{Colors.RESET}"
    
    if include_help_version:
        # Pour l'aide principale : afficher toutes les options
        help_opt = f"{Colors.MAGENTA}-h, --help{Colors.RESET}"
        version_opt = f"{Colors.MAGENTA}--version{Colors.RESET}"
        
        desc = "\n  Options d'aide et version :\n"
        standalone_options = [
            {"flag": f"{alexa_cmd} {help_opt}            ", "description": "Afficher l'aide"},
            {"flag": f"{alexa_cmd} {version_opt}         ", "description": "Afficher la version du programme"},
        ]
        
        desc2 = "\n\n  Modificateurs de comportement (s'utilisent avec une commande) :\n"
        modifier_options = [
            {"flag": f"{alexa_cmd} {verbose_opt}                  ", "description": "Mode verbeux (affiche logs détaillés)"},
            {"flag": f"{alexa_cmd} {debug_opt}                    ", "description": "Mode debug (affiche tous les logs)"},
            {"flag": f"{alexa_cmd} {json_opt}                     ", "description": "Sortie au format JSON (pour scripts)"},
        ]
        
        content = (
            desc + "\n" +
            comp.option_list(standalone_options) + 
            desc2 + "\n" +
            comp.option_list(modifier_options)
        )
    else:
        # Pour les aides de catégories : afficher uniquement les modificateurs avec <ACTION>
        desc = "\n  Modificateurs de comportement :\n"
        
        # Construire les options avec <ACTION> coloré
        action_colored = f"{Colors.ORANGE_BOLD}<ACTION>{Colors.RESET}"
        
        modifier_options = [
            {"flag": f"{alexa_cmd} {verbose_opt} {action_colored}                  ", "description": "Mode verbeux (affiche logs détaillés)"},
            {"flag": f"{alexa_cmd} {debug_opt} {action_colored}                    ", "description": "Mode debug (affiche tous les logs)"},
            {"flag": f"{alexa_cmd} {json_opt} {action_colored}                     ", "description": "Sortie au format JSON (pour scripts)"},
        ]
        
        content = (
            desc + "\n" +
            comp.option_list(modifier_options)
        )
    
    return f"\n{separator}\n{title_line}\n{separator}\n{content}"


def format_categories(categories: List[Dict[str, str]]) -> str:
    """Formate la section des catégories avec titre encadré."""
    comp = HelpComponents()
    separator = f"{Colors.GREEN_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.GREEN_BOLD}📂 Catégories de commandes:{Colors.RESET}"
    
    desc = (
        "\n  Les catégories regroupent les fonctionnalités par domaine d'usage.\n"
        "  Chaque catégorie contient des sous-catégories et des actions spécifiques\n"
        "  pour contrôler différents aspects de vos appareils Alexa.\n\n"
    )
    
    items = []
    for cat in categories:
        name_colored = f"{Colors.GREEN_BOLD}• {cat['name']}{Colors.RESET}"
        padding = " " * (16 - len(cat['name']))
        items.append(f"  {name_colored}{padding}: {cat['desc']}")
    
    content = desc + "\n".join(items)
    return f"\n{separator}\n{title_line}\n{separator}\n{content}"


def format_subcategories(subcategories: List[Dict[str, str]]) -> str:
    """Formate la section des sous-catégories avec titre encadré."""
    comp = HelpComponents()
    separator = f"{Colors.CYAN_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.CYAN_BOLD}🔖 Sous-catégories disponibles:{Colors.RESET}"
    
    desc = (
        "\n  Les sous-catégories affinent les fonctionnalités d'une catégorie principale.\n"
        "  Elles permettent d'accéder à des sous-domaines spécifiques au sein\n"
        "  d'une catégorie donnée.\n\n"
    )
    
    items = []
    for sub in subcategories:
        name_colored = f"{Colors.CYAN_BOLD}• {sub['name']}{Colors.RESET}"
        padding = " " * (13 - len(sub['name']))
        items.append(f"  {name_colored}{padding}: {sub['desc']}")
    
    content = desc + "\n".join(items)
    return f"\n{separator}\n{title_line}\n{separator}\n{content}"


def format_actions(actions: List[Dict[str, Any]]) -> str:
    """Formate la section des actions avec titre encadré.
    
    Args:
        actions: Liste de dictionnaires avec 'name', 'desc', et optionnellement 'options'
                 Exemple: {"name": "create", "desc": "...", "options": [{"flag": "--force", "description": "..."}]}
    """
    comp = HelpComponents()
    separator = f"{Colors.ORANGE_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.ORANGE_BOLD}⚡ Actions disponibles et options possibles:{Colors.RESET}"
    
    desc = (
        "  Les actions définissent l'opération à effectuer sur une catégorie donnée.\n"
        "  Chaque action peut avoir ses propres options spécifiques pour affiner\n"
        "  le comportement souhaité.\n\n"
    )
    
    items = []
    # Première passe : calculer la longueur maximale pour l'alignement
    max_length = 0
    for act in actions:
        if not act.get('hide_base', False):
            max_length = max(max_length, len(act['name']))
        if 'options' in act and act['options']:
            for opt in act['options']:
                action_with_opt = f"{act['name']} {opt['flag']}"
                max_length = max(max_length, len(action_with_opt))
    
    # Aligner à une colonne fixe (minimum 50 pour lisibilité)
    align_column = max(50, max_length + 2)
    
    # Deuxième passe : construire les lignes avec alignement
    for act in actions:
        # Action de base (seulement si hide_base n'est pas True)
        if not act.get('hide_base', False):
            name_colored = f"{Colors.ORANGE_BOLD}• {act['name']}{Colors.RESET}"
            padding = " " * (align_column - len(act['name']) - 2)
            items.append(f"  {name_colored}{padding}: {act['desc']}")
        
        # Ajouter chaque option comme une variante de l'action
        if 'options' in act and act['options']:
            for opt in act['options']:
                # Action + option (ex: "create --force")
                action_with_opt = f"{act['name']} {opt['flag']}"
                name_colored = f"{Colors.ORANGE_BOLD}• {action_with_opt}{Colors.RESET}"
                opt_padding = " " * max(1, align_column - len(action_with_opt) - 2)
                items.append(f"  {name_colored}{opt_padding}: {opt['description']}")
    
    content = desc + "\n".join(items)
    return f"\n{separator}\n{title_line}\n{separator}\n\n{content}"


def format_action_options(options: List[Dict[str, str]]) -> str:
    """Formate la section des options d'action avec titre encadré."""
    comp = HelpComponents()
    separator = f"{Colors.MAGENTA_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.MAGENTA_BOLD}⚙️ Options d'action:{Colors.RESET}"
    content = comp.option_list(options)
    return f"\n{separator}\n{title_line}\n{separator}\n\n{content}"


def format_examples(examples: List[str]) -> str:
    """Formate la section des exemples avec titre encadré et alignement dynamique."""
    comp = HelpComponents()
    separator = f"{Colors.YELLOW_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.YELLOW_BOLD}📋 Exemples d'utilisation:{Colors.RESET}"
    
    # Première passe : calculer la longueur maximale pour l'alignement
    max_length = 0
    for ex in examples:
        if " : " in ex:
            cmd_part = ex.split(" : ", 1)[0].strip()
            # Calculer la longueur visible (sans codes ANSI)
            max_length = max(max_length, len(cmd_part))
    
    # Aligner à une colonne fixe (minimum 50 pour lisibilité)
    align_column = max(50, max_length + 2)
    
    # Deuxième passe : formater avec alignement
    content = "\n".join(comp.example_with_alignment(ex, align_column) for ex in examples)
    return f"\n{separator}\n{title_line}\n{separator}\n\n{content}"


def format_prerequisites(prereqs: List[str]) -> str:
    """Formate la section des prérequis avec titre encadré."""
    comp = HelpComponents()
    separator = f"{Colors.RED_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.RED_BOLD}⚠️  Prérequis essentiels:{Colors.RESET}"
    content = comp.bullet_list(prereqs)
    closing_separator = "━" * 100  # Ligne finale sans couleur (comme le header principal)
    return f"\n{separator}\n{title_line}\n{separator}\n\n{content}\n\n{closing_separator}"


def format_current_category(category_name: str, description: str, emoji: str = "📂") -> str:
    """Formate la section 'Catégorie actuelle' avec couleurs cohérentes.
    
    Utilise le même vert foncé que <CATEGORIE> dans la ligne d'usage (\\033[1;32m),
    en version GRAS avec des lignes ÉPAISSES (━).
    """
    comp = HelpComponents()
    separator = f"{Colors.GREEN_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.GREEN_BOLD}{emoji} Catégorie actuelle:{Colors.RESET}"
    content = f"  {Colors.GREEN_BOLD}{category_name}{Colors.RESET} : {description}"
    return f"\n{separator}\n{title_line}\n{separator}\n\n{content}"


def format_category_options(category: Optional[str] = None, options_text: Optional[str] = None) -> str:
    """Formate la section 'Options de la catégorie actuelle' avec couleurs cohérentes.
    
    Utilise le MÊME vert foncé que <CATEGORIE> (\\033[0;32m = version NON-GRAS du \\033[1;32m),
    en version NORMALE avec des lignes FINES (─).
    
    Args:
        category: Nom de la catégorie pour construire la ligne alexa <category> -h
        options_text: Texte brut des options (pour compatibilité)
    """
    comp = HelpComponents()
    # Même teinte de vert, mais non-gras
    green_normal = '\033[0;32m'
    separator = f"{green_normal}{'─' * 100}{Colors.RESET}"
    title_line = f"{green_normal}🔧 Options de la catégorie actuelle:{Colors.RESET}"
    
    if category:
        # Construire la ligne avec les bonnes couleurs
        alexa_cmd = f"{Colors.GRAY_BOLD}alexa{Colors.RESET}"
        category_colored = f"{Colors.GREEN_BOLD}{category}{Colors.RESET}"
        help_opt = f"{green_normal}-h, --help{Colors.RESET}"
        option_line = f"  {alexa_cmd} {category_colored} {help_opt}          Afficher l'aide de cette catégorie"
        content = f"\n\n{option_line}"
    else:
        # Utiliser le texte brut (compatibilité)
        content = f"\n\n  {options_text}"
    
    return f"\n{separator}\n{title_line}\n{separator}{content}"


def format_current_subcategory(subcategory_name: str, description: str, emoji: str = "🔖") -> str:
    """Formate la section 'Sous-catégorie actuelle' avec couleurs cohérentes."""
    comp = HelpComponents()
    separator = f"{Colors.CYAN}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.CYAN}{emoji} Sous-catégorie actuelle:{Colors.RESET}"
    content = f"\n  {Colors.CYAN}{subcategory_name}{Colors.RESET} : {description}"
    return f"\n{separator}\n{title_line}\n{separator}{content}"


def format_subcategory_options(options_text: str) -> str:
    """Formate la section 'Options de la sous-catégorie actuelle' avec couleurs cohérentes."""
    comp = HelpComponents()
    separator = f"{Colors.CYAN_BOLD}{'─' * 100}{Colors.RESET}"
    title_line = f"{Colors.CYAN}🔧 Options de la sous-catégorie actuelle:{Colors.RESET}"
    content = f"\n\n  {options_text}"
    return f"\n{separator}\n{title_line}\n{separator}{content}"


def format_more_help_main() -> str:
    """Formate la section 'Pour plus d'aide' pour l'aide principale avec titre encadré."""
    comp = HelpComponents()
    separator = f"{Colors.WHITE_BOLD}{'━' * 100}{Colors.RESET}"
    title_line = f"{Colors.WHITE_BOLD}🆘 Pour plus d'aide:{Colors.RESET}"
    
    desc = (
        "\n  Le système d'aide est organisé de manière hiérarchique pour vous guider\n"
        "  efficacement dans l'utilisation des commandes Alexa.\n\n"
    )
    
    nav_items = [
        f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.MAGENTA}--help{Colors.RESET}                                                  : Cette aide générale",
        f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}<categorie>{Colors.RESET} {Colors.GREEN}--help{Colors.RESET}                                      : Aide détaillée d'une catégorie",
        f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}<categorie>{Colors.RESET} {Colors.CYAN_BOLD}<sous-categorie>{Colors.RESET} {Colors.CYAN}--help{Colors.RESET}                     : Aide spécifique d'une sous-catégorie",
        f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}<categorie>{Colors.RESET} {Colors.CYAN_BOLD}<sous-categorie>{Colors.RESET} {Colors.ORANGE_BOLD}<action>{Colors.RESET} {Colors.ORANGE}--help{Colors.RESET}            : Aide d'une action précise",
    ]
    
    examples_title = f"\n  {Colors.GRAY_BOLD}📚 Exemples pratiques :{Colors.RESET}\n\n"
    examples = [
        f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}timer{Colors.RESET} {Colors.GREEN}--help{Colors.RESET}                        : Découvrir les fonctionnalités temporelles",
        f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}music{Colors.RESET} {Colors.CYAN_BOLD}playback{Colors.RESET} {Colors.CYAN}--help{Colors.RESET}               : Maîtriser le contrôle musical",
        f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}smarthome{Colors.RESET} {Colors.CYAN_BOLD}light{Colors.RESET} {Colors.ORANGE_BOLD}on{Colors.RESET} {Colors.ORANGE}--help{Colors.RESET}           : Contrôler l'éclairage domotique",
    ]
    
    tips_title = f"\n  {Colors.GRAY_BOLD}💫 Astuces :{Colors.RESET}\n\n"
    tips = [
        "  • Utilisez --help à chaque niveau pour explorer progressivement",
        "  • Les couleurs indiquent les éléments syntaxiques importants",
        "  • Les exemples montrent des cas d'usage réels",
        "  • L'auto-complétion (Tab) facilite la découverte des commandes"
    ]
    
    content = (
        desc + 
        "\n".join(nav_items) + 
        "\n" + examples_title + "\n".join(examples) + 
        "\n" + tips_title + "\n".join(tips)
    )
    
    return f"\n{separator}\n{title_line}\n{separator}\n{content}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧱 CONSTRUCTEURS DE SECTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class HelpSection:
    """Représente une section d'aide complète."""
    header: str
    features: Optional[List[str]] = None
    architecture: Optional[List[str]] = None
    usage: Optional[str] = None
    global_options: Optional[List[Dict[str, str]]] = None
    categories: Optional[List[Dict[str, str]]] = None
    subcategories: Optional[List[Dict[str, str]]] = None
    actions: Optional[List[Dict[str, str]]] = None
    examples: Optional[List[str]] = None
    more_help: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class HelpBuilder:
    """Constructeur modulaire de pages d'aide."""
    
    def __init__(self):
        self.components = HelpComponents()
        self._sections = []
    
    def add_header(self, icon: str, title: str) -> 'HelpBuilder':
        """Ajoute l'en-tête."""
        self._sections.append(self.components.header(icon, title))
        return self
    
    def add_features(self, features: List[str], show_title: bool = True) -> 'HelpBuilder':
        """Ajoute la section Fonctionnalités."""
        title = self.components.section_title("✨", "Fonctionnalités principales", Colors.GRAY_BOLD)
        content = self.components.bullet_list(features)
        
        if show_title:
            self._sections.append(f"{title}\n{content}")
        else:
            self._sections.append(content)
        return self
    
    def add_architecture(self, items: List[str]) -> 'HelpBuilder':
        """Ajoute la section Architecture (optionnelle)."""
        title = self.components.section_title("🏗️", "Architecture modulaire", Colors.GRAY_BOLD)
        content = self.components.bullet_list(items)
        self._sections.append(f"{title}\n{content}")
        return self
    
    def add_usage(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        action: Optional[str] = None,
        is_main: bool = False
    ) -> 'HelpBuilder':
        """Ajoute la ligne d'usage."""
        # Titre différent pour l'aide principale
        title_text = "Usage général" if is_main else "Usage"
        title = self.components.section_title("📖", title_text, Colors.WHITE_BOLD)
        usage = self.components.usage_line("alexa", category, subcategory, action, None, is_main)
        self._sections.append(f"{title}\n\n  {usage}")
        return self
    
    def add_global_options(self) -> 'HelpBuilder':
        """Ajoute les options globales standard."""
        title = self.components.section_title("🔧", "Options globales disponibles", Colors.MAGENTA_BOLD)
        
        desc = (
            "\n  Options autonomes (peuvent être utilisées seules) :\n"
        )
        
        standalone_options = [
            {"flag": "-h, --help", "description": "Afficher l'aide contextuelle"},
            {"flag": "-v, --version", "description": "Afficher la version du programme"},
        ]
        
        desc2 = (
            "\n\n  Modificateurs de commande (s'utilisent avec une commande, sauf -h/-v) :\n"
        )
        
        modifier_options = [
            {"flag": "--verbose", "description": "Mode verbeux avec détails supplémentaires"},
            {"flag": "--quiet", "description": "Mode silencieux, réduit les messages"},
            {"flag": "--no-color", "description": "Désactiver les couleurs dans l'affichage"},
        ]
        
        content = (
            self.components.option_list(standalone_options) + 
            desc2 + "\n" +
            self.components.option_list(modifier_options)
        )
        
        self._sections.append(f"{title}{desc}\n{content}")
        return self
    
    def add_categories(self, categories: List[Dict[str, str]]) -> 'HelpBuilder':
        """Ajoute la liste des catégories."""
        title = self.components.section_title("📂", "Catégories de commandes", Colors.GREEN_BOLD)
        
        desc = (
            "\n  Les catégories regroupent les fonctionnalités par domaine d'usage.\n"
            "  Chaque catégorie contient des sous-catégories et des actions spécifiques\n"
            "  pour contrôler différents aspects de vos appareils Alexa.\n"
        )
        
        items = []
        for cat in categories:
            name_colored = f"{Colors.GREEN_BOLD}• {cat['name']}{Colors.RESET}"
            # Padding avec espaces (au lieu de points)
            padding = " " * (16 - len(cat['name']))
            items.append(f"  {name_colored}{padding}: {cat['desc']}")
        content = "\n".join(items)
        
        self._sections.append(f"{title}{desc}\n{content}")
        return self
    
    def add_subcategories(self, subcategories: List[Dict[str, str]]) -> 'HelpBuilder':
        """Ajoute la liste des sous-catégories."""
        title = self.components.section_title("🔖", "Sous-catégories disponibles", Colors.CYAN_BOLD)
        
        desc = (
            "\n  Les sous-catégories affinent les fonctionnalités d'une catégorie principale.\n"
            "  Elles permettent d'accéder à des sous-domaines spécifiques au sein\n"
            "  d'une catégorie donnée.\n"
        )
        
        items = []
        for sub in subcategories:
            name_colored = f"{Colors.CYAN_BOLD}• {sub['name']}{Colors.RESET}"
            # Utiliser des espaces au lieu de points pour l'alignement
            padding = " " * (13 - len(sub['name']))
            items.append(f"  {name_colored}{padding}: {sub['desc']}")
        content = "\n".join(items)
        
        self._sections.append(f"{title}{desc}\n{content}")
        return self
    
    def add_actions(self, actions: List[Dict[str, str]]) -> 'HelpBuilder':
        """Ajoute la liste des actions."""
        title = self.components.section_title("⚡", "Actions principales", Colors.ORANGE_BOLD)
        
        desc = (
            "\n  Les actions définissent l'opération à effectuer sur une catégorie donnée.\n"
            "  Chaque action peut avoir ses propres options spécifiques pour affiner\n"
            "  le comportement souhaité.\n"
        )
        
        items = []
        for act in actions:
            name_colored = f"{Colors.ORANGE_BOLD}• {act['name']}{Colors.RESET}"
            # Utiliser des espaces au lieu de points pour l'alignement
            padding = " " * (16 - len(act['name']))
            items.append(f"  {name_colored}{padding}: {act['desc']}")
        content = "\n".join(items)
        
        self._sections.append(f"{title}{desc}\n{content}")
        return self
    
    def add_action_options(self, options: List[Dict[str, str]]) -> 'HelpBuilder':
        """Ajoute les options spécifiques à une action."""
        title = self.components.section_title("⚙️", "Options d'action", Colors.MAGENTA_BOLD)
        content = self.components.option_list(options)
        self._sections.append(f"{title}\n{content}")
        return self
    
    def add_examples(self, examples: List[str]) -> 'HelpBuilder':
        """Ajoute des exemples d'utilisation."""
        title = self.components.section_title("📋", "Exemples d'utilisation", Colors.YELLOW_BOLD)
        content = "\n".join(self.components.example(ex) for ex in examples)
        self._sections.append(f"{title}\n{content}")
        return self
    
    def add_more_help(self, help_items: List[Dict[str, str]]) -> 'HelpBuilder':
        """Ajoute la section 'Pour plus d'aide'."""
        title = self.components.section_title("💡", "Pour plus d'aide", Colors.WHITE_BOLD)
        
        desc = (
            "\n  Le système d'aide est organisé de manière hiérarchique pour vous guider\n"
            "  efficacement dans l'utilisation des commandes Alexa.\n"
        )
        
        # Navigation
        nav_title = f"\n  {Colors.GRAY_BOLD}Navigation dans l'aide :{Colors.RESET}\n"
        nav_items = []
        for item in help_items:
            nav_items.append(f"  {item['command']:<60} : {item['description']}")
        
        content = desc + nav_title + "\n".join(nav_items)
        self._sections.append(f"{title}{content}")
        return self
    
    def add_main_more_help(self) -> 'HelpBuilder':
        """Ajoute la section 'Pour plus d'aide' spécifique pour l'aide principale."""
        title = self.components.section_title("🆘", "Pour plus d'aide", Colors.WHITE_BOLD)
        
        desc = (
            "\n  Le système d'aide est organisé de manière hiérarchique pour vous guider\n"
            "  efficacement dans l'utilisation des commandes Alexa.\n"
        )
        
        # Navigation dans l'aide (sans titre de sous-section)
        nav_items = [
            f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.MAGENTA}--help{Colors.RESET}                                                  : Cette aide générale",
            f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}<categorie>{Colors.RESET} {Colors.GREEN}--help{Colors.RESET}                                      : Aide détaillée d'une catégorie",
            f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}<categorie>{Colors.RESET} {Colors.CYAN_BOLD}<sous-categorie>{Colors.RESET} {Colors.CYAN}--help{Colors.RESET}                     : Aide spécifique d'une sous-catégorie",
            f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}<categorie>{Colors.RESET} {Colors.CYAN_BOLD}<sous-categorie>{Colors.RESET} {Colors.ORANGE_BOLD}<action>{Colors.RESET} {Colors.ORANGE}--help{Colors.RESET}            : Aide d'une action précise",
        ]
        
        # Exemples pratiques
        examples_title = f"\n  {Colors.GRAY_BOLD}📚 Exemples pratiques :{Colors.RESET}\n\n"
        examples = [
            f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}timers{Colors.RESET} {Colors.GREEN}--help{Colors.RESET}                        : Découvrir les fonctionnalités temporelles",
            f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}music{Colors.RESET} {Colors.CYAN_BOLD}playback{Colors.RESET} {Colors.CYAN}--help{Colors.RESET}               : Maîtriser le contrôle musical",
            f"  {Colors.WHITE_BOLD}alexa{Colors.RESET} {Colors.GREEN_BOLD}smarthome{Colors.RESET} {Colors.CYAN_BOLD}light{Colors.RESET} {Colors.ORANGE_BOLD}on{Colors.RESET} {Colors.ORANGE}--help{Colors.RESET}           : Contrôler l'éclairage domotique",
        ]
        
        # Astuces
        tips_title = f"\n  {Colors.GRAY_BOLD}💫 Astuces :{Colors.RESET}\n\n"
        tips = [
            "  • Utilisez --help à chaque niveau pour explorer progressivement",
            "  • Les couleurs indiquent les éléments syntaxiques importants",
            "  • Les exemples montrent des cas d'usage réels",
            "  • L'auto-complétion (Tab) facilite la découverte des commandes"
        ]
        
        content = (
            desc + "\n" +
            "\n".join(nav_items) + 
            "\n" + examples_title + "\n".join(examples) + 
            "\n" + tips_title + "\n".join(tips)
        )
        
        self._sections.append(f"{title}{content}")
        return self
    
    def add_prerequisites(self, prereqs: List[str]) -> 'HelpBuilder':
        """Ajoute les prérequis."""
        title = self.components.section_title("⚠️ ", "Prérequis essentiels", Colors.RED_BOLD)
        content = self.components.bullet_list(prereqs)
        self._sections.append(f"{title}\n{content}")
        return self
    
    def build(self) -> str:
        """Construit la page d'aide complète."""
        return "\n".join(self._sections) + "\n"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 API PUBLIQUE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_main_help() -> str:
    """Crée l'aide principale (alexa -h)."""
    builder = HelpBuilder()
    
    return (builder
        .add_header("�️", "ALEXA ADVANCED CONTROL - CONTRÔLE AVANCÉ D'ALEXA")
        .add_features([
            "Contrôle complet des appareils Alexa",
            "Gestion des médias (musique, playlists, volume)",
            "Programmation temporelle (minuteurs, alarmes, rappels)",
            "Contrôle domotique (lumières, thermostats, etc.)",
            "Notifications et annonces vocales",
            "Synchronisation multi-appareils"
        ], show_title=False)
        .add_architecture([
            "Interface CLI moderne avec auto-complétion",
            "Architecture modulaire par catégories",
            "Cache intelligent pour les performances",
            "Gestion d'erreurs robuste",
            "Support multi-langues"
        ])
        .add_usage(is_main=True)  # Avec le flag is_main=True
        .add_global_options()
        .add_categories([
            {"name": "auth", "desc": "Gestion de l'authentification et connexion"},
            {"name": "device", "desc": "Contrôle et gestion des appareils"},
            {"name": "timers", "desc": "Gestion du temps (minuteurs, alarmes, rappels)"},
            {"name": "music", "desc": "Contrôle musical et médias"},
            {"name": "smarthome", "desc": "Domotique et appareils connectés"},
            {"name": "announcement", "desc": "Gestion des annonces"},
            {"name": "routine", "desc": "Automatisations et routines"},
            {"name": "activity", "desc": "Historique d'activité"},
            {"name": "cache", "desc": "Gestion du cache local"},
            {"name": "lists", "desc": "Gestion des listes"},
        ])
        .add_subcategories([
            {"name": "countdown", "desc": "Minuteurs et compteurs de temps"},
            {"name": "alarm", "desc": "Gestion des alarmes programmées"},
            {"name": "reminder", "desc": "Rappels et notifications"},
            {"name": "playback", "desc": "Contrôle de lecture musicale"},
            {"name": "volume", "desc": "Gestion du volume audio"},
            {"name": "equalizer", "desc": "Égaliseur et réglages audio"},
            {"name": "light", "desc": "Contrôle de l'éclairage"},
            {"name": "thermostat", "desc": "Gestion de la température"},
            {"name": "security", "desc": "Sécurité et surveillance"},
            {"name": "camera", "desc": "Contrôle des caméras"},
        ])
        .add_actions([
            {"name": "create", "desc": "Créer un nouvel élément (minuteur, alarme, etc.)"},
            {"name": "list", "desc": "Lister les éléments existants"},
            {"name": "delete", "desc": "Supprimer un élément"},
            {"name": "update", "desc": "Modifier un élément existant"},
            {"name": "play/pause/stop", "desc": "Contrôler la lecture média"},
            {"name": "on/off", "desc": "Contrôler l'état des appareils"},
        ])
        .add_examples([
            "alexa device list",
            "alexa timers countdown create --duration 10m",
            'alexa music play --playlist "Ma playlist"',
            'alexa smarthome light on --name "Salon"'
        ])
        .add_main_more_help()  # Nouvelle méthode pour l'aide principale
        .add_prerequisites([
            "Authentification Alexa configurée (alexa auth login)",
            "Appareils Alexa connectés et accessibles",
            "Connexion internet stable",
            "Cookies d'authentification valides"
        ])
        .build()
    )


def create_category_help(
    icon: str,
    name: str,
    description: str,
    features: List[str],
    subcategories: Optional[List[Dict[str, str]]] = None,
    actions: Optional[List[Dict[str, str]]] = None,
    examples: List[str] = None,
    prerequisites: List[str] = None
) -> str:
    """Crée l'aide d'une catégorie (ex: alexa timers -h)."""
    builder = HelpBuilder()
    
    builder.add_header(icon, f"{name.upper()} - {description}")
    builder.add_features(features)
    builder.add_usage(category=name)
    builder.add_global_options()
    
    if subcategories:
        builder.add_subcategories(subcategories)
    
    if actions:
        builder.add_actions(actions)
    
    if examples:
        builder.add_examples(examples)
    
    if prerequisites:
        builder.add_prerequisites(prerequisites)
    
    return builder.build()


def create_subcategory_help(
    icon: str,
    category: str,
    subcategory: str,
    description: str,
    features: List[str],
    actions: List[Dict[str, str]],
    examples: List[str],
    prerequisites: List[str]
) -> str:
    """Crée l'aide d'une sous-catégorie (ex: alexa timers countdown -h)."""
    builder = HelpBuilder()
    
    return (builder
        .add_header(icon, f"{category.upper()} {subcategory.upper()} - {description}")
        .add_features(features)
        .add_usage(category=category, subcategory=subcategory)
        .add_actions(actions)
        .add_examples(examples)
        .add_prerequisites(prerequisites)
        .build()
    )


def format_custom_global_options(options: List[Dict[str, str]]) -> str:
    """Formate la section des options globales avec options personnalisées."""
    if not options:
        return ""
    
    separator = "━" * 100
    title = f"{Colors.MAGENTA_BOLD}🔧 Options globales disponibles{Colors.RESET}"
    
    desc = (
        f"\n{Colors.GRAY_BOLD}  Options disponibles dans toutes les commandes pour modifier leur comportement.{Colors.RESET}\n"
    )
    
    content_lines = []
    for opt in options:
        flag = f"{Colors.MAGENTA_BOLD}{opt['flag']}{Colors.RESET}"
        padding = " " * (25 - len(opt['flag']))
        desc_text = opt['description']
        content_lines.append(f"  {flag}{padding}: {desc_text}")
    
    content = "\n".join(content_lines)
    
    return f"\n{separator}\n{title}\n{separator}{desc}\n{content}"


def format_usage_fields(category: str, actions: List[str], global_options: List[str], action_options_desc: str = "Options spécifiques à chaque action") -> str:
    """Formate une section détaillant les champs de la ligne d'usage."""
    if not actions:
        return ""
    
    separator = "━" * 100
    title = f"{Colors.CYAN_BOLD}🔍 Détail des champs de commande{Colors.RESET}"
    
    desc = (
        f"\n{Colors.GRAY_BOLD}  Analyse détaillée de chaque élément de la syntaxe de commande.{Colors.RESET}\n"
    )
    
    # Champ catégorie
    category_field = f"  {Colors.GREEN_BOLD}<{category.upper()}>{Colors.RESET}"
    category_desc = f"  {Colors.GRAY_BOLD}•{Colors.RESET} {category_field} {Colors.GRAY_BOLD}: Catégorie d'authentification Amazon Alexa{Colors.RESET}"
    
    # Champ actions
    actions_str = ", ".join([f"{Colors.ORANGE_BOLD}{action}{Colors.RESET}" for action in actions])
    actions_field = f"  {Colors.ORANGE_BOLD}<ACTION>{Colors.RESET}"
    actions_desc = f"  {Colors.GRAY_BOLD}•{Colors.RESET} {actions_field} {Colors.GRAY_BOLD}: Une des actions disponibles ({actions_str}){Colors.RESET}"
    
    # Champ options globales
    global_opts_str = ", ".join([f"{Colors.MAGENTA}{opt}{Colors.RESET}" for opt in global_options])
    global_field = f"  {Colors.MAGENTA}[OPTIONS_GLOBALES]{Colors.RESET}"
    global_desc = f"  {Colors.GRAY_BOLD}•{Colors.RESET} {global_field} {Colors.GRAY_BOLD}: Options applicables partout ({global_opts_str}){Colors.RESET}"
    
    # Champ options action
    action_opts_field = f"  {Colors.ORANGE}[OPTIONS_ACTION]{Colors.RESET}"
    action_opts_desc_formatted = f"  {Colors.GRAY_BOLD}•{Colors.RESET} {action_opts_field} {Colors.GRAY_BOLD}: {action_options_desc}{Colors.RESET}"
    
    content = "\n".join([
        category_desc,
        actions_desc,
        global_desc,
        action_opts_desc_formatted
    ])
    
    return f"\n{separator}\n{title}\n{separator}{desc}\n{content}"
