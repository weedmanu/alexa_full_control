"""
Module de parsing des commandes CLI avec architecture modulaire à sous-commandes.

Ce module gère l'analyse des arguments de ligne de commande en utilisant
argparse avec des subparsers pour créer une architecture modulaire et extensible.

Architec            # Ajouter de la couleur au titre de l'architecture (bleu comme OPTIONS_GLOBALES)
            for i, line in enumerate(architecture_section):
                if '🏗️  Architecture modulaire:' in line or '🏗️  Architecture:' in line:
                    architecture_section[i] = '\033[1;34m🏗️  Architecture modulaire:\033[0m'
                    break
    python alexa_voice_control.py <CATEGORY> <ACTION> [OPTIONS]

Catégories supportées:
    - auth: Authentification (login, logout, status, refresh)
    - device: Gestion appareils (list, info, control, volume)
    - music: Contrôle musique (play, radio, control, queue)
    - timer: Gestion timers (create, list, cancel, pause, resume)
    - alarm: Gestion alarmes (create, list, delete, update)
    - reminder: Gestion rappels (create, list, delete)
    - smarthome: Contrôle appareils smart home (lock, unlock, state, lights, thermostats)
    - notification: Gestion notifications (list, delete, read)
    - dnd: Mode Ne Pas Déranger (status, enable, disable, schedule)
    - announcement: Annonces (send, dropin)
    - list: Listes courses/tâches (add, remove, clear)
    - activity: Historique activités (list, delete, voice-history)
    - audio: Paramètres audio (equalizer, bluetooth)
    - settings: Paramètres appareils (get, wake-word, timezone, locale)
    - routine: Routines (list, execute, info)
    - multiroom: Groupes multi-pièces (create, delete, list)

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import sys
from typing import Any, Dict, Iterable, List, Optional, Type

from loguru import logger

from cli.base_command import BaseCommand


class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter personnalisé pour les aides argparse avec couleurs et emojis.
    Contrôle l'ordre d'affichage : Titre → Usage → Options → Actions → Options d'action → Exemples
    """

    def _format_usage(
        self, usage: Optional[str], actions: Any, groups: Any, prefix: Optional[str]
    ) -> str:
        """Formatte la ligne d'usage avec couleurs."""
        if prefix is None:
            prefix = "\033[1;36mUsage:\033[0m "

        usage = super()._format_usage(usage, actions, groups, prefix)
        return usage

    def _format_action(self, action: argparse.Action) -> str:
        """Formate une action avec couleurs améliorées."""
        # Utiliser le formatage standard d'argparse
        result = super()._format_action(action)

        # Ajouter des couleurs aux sections spéciales
        result = result.replace("Actions sur", "\033[1;35mActions sur\033[0m")
        result = result.replace("Gérer", "\033[1;34mGérer\033[0m")
        result = result.replace("Action à exécuter", "\033[1;36mAction à exécuter\033[0m")

        # Pour les sous-commandes, améliorer légèrement le formatage
        if hasattr(action, "choices") and action.choices:
            # Ajouter un retour à la ligne après la description si nécessaire
            result = result.replace("}  Action à exécuter", "}\n    Action à exécuter")

        return result

    def _format_text(self, text: str) -> str:
        """Formate le texte avec couleurs pour les sections spéciales."""
        if not text:
            return text

        # Ajouter des couleurs aux sections spéciales
        text = text.replace("Actions sur", "\033[1;35mActions sur\033[0m")
        text = text.replace("Gérer", "\033[1;34mGérer\033[0m")
        text = text.replace("Action à exécuter", "\033[1;36mAction à exécuter\033[0m")

        return text

    def format_help(self) -> str:
        """Formate l'aide complète dans l'ordre personnalisé."""
        # Utiliser le formatage standard mais avec couleurs améliorées
        help_text = super().format_help()

        # Ajouter des couleurs aux sections principales
        help_text = help_text.replace("usage:", "\033[1;36mUsage:\033[0m")
        help_text = help_text.replace("options:", "\033[1;35mOptions:\033[0m")
        help_text = help_text.replace("positional arguments:", "\033[1;35mArguments positionnels:\033[0m")

        return help_text


class NoOptionsHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Formatter personnalisé qui masque la section 'options:' auto."""

    def add_usage(
        self,
        usage: Optional[str],
        actions: Iterable[argparse.Action],
        groups: Iterable[Any],
        prefix: Optional[str] = None,
    ) -> None:
        """Ne pas afficher la ligne usage: auto."""
        return

    def add_arguments(self, actions: Iterable[argparse.Action]) -> None:
        """Ne pas afficher la section options: auto."""
        # Ne rien faire pour les arguments individuels (-h, etc.)
        pass


class ActionHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter pour les actions qui masque la section 'options:' par défaut
    pour permettre un contrôle total via la chaîne de description.
    """

    def add_usage(
        self,
        usage: Optional[str],
        actions: Iterable[argparse.Action],
        groups: Iterable[Any],
        prefix: Optional[str] = None,
    ) -> None:
        """Neutralise la génération automatique de la ligne usage."""
        return

    def _format_action(self, action: argparse.Action) -> str:
        # Masquer la section 'options:'
        if action.option_strings:
            return ""
        return super()._format_action(action)

    def format_help(self) -> str:
        help_text = super().format_help()
        # Supprimer la section 'options:' vide
        cleaned = help_text.replace('options:\n', '').strip()
        return f"{cleaned}\n"


class UniversalHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter universel pour toutes les commandes CLI qui affiche dans l'ordre :
    Titre → Usage → Options globales → Actions → Options d'action → Exemples
    """

    def format_help(self) -> str:
        """Override pour contrôler l'ordre d'affichage selon la structure de l'usage."""
        # Utiliser le formatage standard mais réorganiser
        help_text = super().format_help()
        
        # Si la description contient déjà notre format modulaire (détecté par les séparateurs colorés),
        # supprimer les sections argparse automatiques et retourner
        if '\033[1;90m━━━━━━━' in help_text or '\033[1;32m━━━━━━━' in help_text:
            # Supprimer les sections "positional arguments" et "options" ajoutées par argparse
            lines = help_text.split('\n')
            filtered_lines = []
            skip_section = False
            
            for line in lines:
                # Détecter le début des sections argparse à ignorer
                if line.strip() in ['positional arguments:', 'options:', 'optional arguments:']:
                    skip_section = True
                    continue
                
                # Arrêter d'ignorer si on rencontre une ligne vide après la section
                if skip_section and not line.strip():
                    skip_section = False
                    continue
                
                # Ajouter la ligne si on n'est pas dans une section à ignorer
                if not skip_section:
                    filtered_lines.append(line)
            
            return '\n'.join(filtered_lines)

        # Diviser en lignes et réorganiser (ancien système)
        lines = help_text.split('\n')
        reordered_lines: List[str] = []

        # Variables pour stocker les sections
        title_section: List[str] = []
        description_section: List[str] = []
        architecture_section: List[str] = []
        usage_section: List[str] = []
        options_section: List[str] = []
        actions_section: List[str] = []
        action_options_section: List[str] = []
        examples_section: List[str] = []
        positionals_section: List[str] = []
        categories_section: List[str] = []
        subcategories_section: List[str] = []
        help_section: List[str] = []
        note_section: List[str] = []

        current_section: Optional[str] = None
        in_title = False

        for line in lines:
            line = line.rstrip()
            # NE PAS ignorer les lignes vides - elles font partie de l'espacement
            # if not line:
            #     continue

            # Ignorer complètement les lignes usage automatiques (non colorées)
            if line.startswith('usage:'):
                continue

            # Ignorer les lignes qui contiennent des arguments positionnels parasites
            if '[--config' in line or 'CATEGORY ...' in line:
                continue

            # Détecter le titre (entouré de caractères spéciaux)
            if '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' in line:
                if not in_title:
                    in_title = True
                    current_section = 'title'
                    title_section.append(line)
                else:
                    in_title = False
                    title_section.append(line)
                continue

            if in_title:
                title_section.append(line)
                continue

            # Détecter les autres sections
            if '\033[1;36mUsage:\033[0m' in line or ('Usage:' in line and 'alexa [OPTIONS_GLOBALES]' in line):
                current_section = 'usage'
                # Colorer les parties de la ligne usage comme dans l'aide principale
                line = line.replace('Usage:', '\033[1;36mUsage:\033[0m')
                line = line.replace('alexa', '\033[1;37malexa\033[0m')
                line = line.replace('[OPTIONS_GLOBALES]', '[\033[1;34mOPTIONS_GLOBALES\033[0m]')
                line = line.replace('auth', '\033[1;32mauth\033[0m')
                line = line.replace('[<ACTION>]', '[\033[1;33m<ACTION>\033[0m]')
                line = line.replace('[OPTIONS_ACTION]', '[\033[1;35mOPTIONS_ACTION\033[0m]')
                line = line.replace('<CATEGORY>', '\033[1;32m<CATEGORY>\033[0m')
                usage_section.append(line)
            elif line == '\033[1;35mOptions:\033[0m' or line == 'options:':
                current_section = 'options'
                options_section.append(line)
            elif line == '\033[1;35mArguments positionnels:\033[0m' or line == 'positional arguments:':
                current_section = 'positionals'
                positionals_section.append(line)
            elif '\033[1;32m🎯 Fonctionnalités principales:\033[0m' in line:
                current_section = 'description'
                description_section.append(line)
            elif '\033[1;34m🏗️  Architecture modulaire:\033[0m' in line:
                current_section = 'architecture'
                architecture_section.append(line)
            elif '🏗️  Architecture:' in line:
                current_section = 'architecture'
                # Ajouter la couleur à la section architecture
                line = '\033[1;34m' + line + '\033[0m'
                architecture_section.append(line)
            elif '\033[1;32m🎯 Catégories principales:\033[0m' in line:
                current_section = 'categories'
                categories_section.append(line)
            elif '\033[1;33m🎯 Catégories avec sous-catégories:\033[0m' in line:
                current_section = 'subcategories'
                subcategories_section.append(line)
            elif '\033[1;33m🎯 Actions par catégorie:\033[0m' in line or '\033[1;33m🎯 Actions disponibles:\033[0m' in line or '\033[1;34m🎯 Actions disponibles:\033[0m' in line:
                current_section = 'actions'
                actions_section.append(line)
            elif '\033[1;35m⚙️  Options d\'action:\033[0m' in line:
                current_section = 'action_options'
                action_options_section.append(line)
            elif '\033[1;36m💡 Exemples d\'utilisation:\033[0m' in line:
                current_section = 'examples'
                examples_section.append(line)
            elif '\033[1;37m💡 Pour plus d\'aide:\033[0m' in line:
                current_section = 'help'
                help_section.append(line)
            elif '\033[1;31m⚠️  Important:\033[0m' in line:
                current_section = 'note'
                note_section.append(line)
            elif current_section == 'usage':
                usage_section.append(line)
            elif current_section == 'options':
                options_section.append(line)
            elif current_section == 'positionals':
                positionals_section.append(line)
            elif current_section == 'description':
                description_section.append(line)
            elif current_section == 'architecture':
                architecture_section.append(line)
            elif current_section == 'categories':
                categories_section.append(line)
            elif current_section == 'subcategories':
                subcategories_section.append(line)
            elif current_section == 'action_options':
                action_options_section.append(line)
            elif current_section == 'examples':
                examples_section.append(line)
            elif current_section == 'help':
                help_section.append(line)
            elif current_section == 'note':
                note_section.append(line)
            elif current_section == 'actions':
                actions_section.append(line)
            else:
                # Si pas de section identifiée, mettre dans actions par défaut
                actions_section.append(line)

        # Nettoyer les sections : supprimer les \n mais PRESERVER les lignes vides pour l'espacement
        for _, section in [
            ('title', title_section),
            ('description', description_section),
            ('architecture', architecture_section),
            ('usage', usage_section),
            ('options', options_section),
            ('categories', categories_section),
            ('subcategories', subcategories_section),
            ('actions', actions_section),
            ('action_options', action_options_section),
            ('examples', examples_section),
            ('help', help_section),
            ('note', note_section),
        ]:
            section[:] = [line.rstrip('\n') for line in section]

        # Réorganiser dans l'ordre souhaité selon la structure de l'usage :
        # alexa [OPTIONS_GLOBALES] auth <ACTION> [OPTIONS_ACTION]
        # 1. Titre
        reordered_lines.extend(title_section)

        # 2. Description (Fonctionnalités + Architecture + Usage)
        if description_section:
            # Ajouter de la couleur au titre des fonctionnalités (vert comme <CATEGORY>)
            for i, line in enumerate(description_section):
                if '🎯 Fonctionnalités principales:' in line:
                    description_section[i] = '\033[1;32m🎯 Fonctionnalités principales:\033[0m'
                    break
            reordered_lines.extend(description_section)
            reordered_lines.append("")  # Ligne vide après les fonctionnalités

        # 2.5 Architecture
        if architecture_section:
            # Ajouter de la couleur au titre de l'architecture (bleu comme OPTIONS_GLOBALES)
            for i, line in enumerate(architecture_section):
                if '🏗️  ARCHITECTURE MODULAIRE:' in line or '🏗️  ARCHITECTURE:' in line:
                    architecture_section[i] = '\033[1;34m🏗️  ARCHITECTURE MODULAIRE:\033[0m'
                    break
            reordered_lines.extend(architecture_section)
            reordered_lines.append("")  # Ligne vide après l'architecture

        # 3. Usage
        if usage_section:
            reordered_lines.extend(usage_section)
            reordered_lines.append("")  # Ligne vide après l'usage

        # 4. Options globales (OPTIONS_GLOBALES)
        # Ne pas afficher les options globales argparse car on les a déjà dans le template personnalisé
        # reordered_lines.extend(options_section)
        # reordered_lines.append("")  # Ligne vide après les options globales

        # 3. Catégories disponibles
        if categories_section:
            # Compter le nombre de catégories listées (lignes non vides après le titre)
            category_count = sum(1 for line in categories_section[1:] if line.strip() and not line.startswith('\033['))
            # Si une seule catégorie, c'est une aide de catégorie spécifique
            title_text = '🎯 Catégorie actuelle:' if category_count == 1 else '🎯 Catégories disponibles:'
            # Ajouter de la couleur au titre des catégories (vert comme <CATEGORY>)
            for i, line in enumerate(categories_section):
                if '🎯 Catégories disponibles:' in line or '🎯 Catégorie:' in line or '🎯 Catégorie actuelle:' in line:
                    categories_section[i] = f'\033[1;32m{title_text}\033[0m'
                    break
            reordered_lines.extend(categories_section)
            reordered_lines.append("")  # Ligne vide après les catégories

        # 3.5 Catégories avec sous-catégories
        if subcategories_section:
            reordered_lines.extend(subcategories_section)
            reordered_lines.append("")  # Ligne vide après les sous-catégories

        # 4. Actions par catégorie
        if actions_section:
            # Ajouter de la couleur au titre des actions (bleu comme <ACTION>)
            for i, line in enumerate(actions_section):
                if '🎯 Actions par catégorie:' in line or '🎯 Actions disponibles:' in line:
                    actions_section[i] = '\033[1;34m🎯 Actions disponibles:\033[0m'
                    break
            reordered_lines.extend(actions_section)
            reordered_lines.append("")  # Ligne vide après les actions

        # 5. Options d'action ([OPTIONS_ACTION])
        if action_options_section:
            # Ajouter de la couleur au titre des options d'action (magenta comme OPTIONS_ACTION)
            for i, line in enumerate(action_options_section):
                if '⚙️  Options d\'action:' in line or '⚙️  Options d\'action:' in line:
                    action_options_section[i] = '\033[1;35m⚙️  Options d\'action:\033[0m'
                    break
            reordered_lines.extend(action_options_section)
            reordered_lines.append("")  # Ligne vide après les options d'action

        # 6. Exemples
        if examples_section:
            # Ajouter de la couleur au titre des exemples (cyan comme dans l'epilog)
            for i, line in enumerate(examples_section):
                if '💡 Exemples d\'utilisation:' in line or '💡 Exemples d\'utilisation:' in line:
                    examples_section[i] = '\033[1;36m💡 Exemples d\'utilisation:\033[0m'
                    break
            reordered_lines.extend(examples_section)
            reordered_lines.append("")  # Ligne vide après les exemples

        # 7. Pour plus d'aide
        if help_section:
            # Ajouter de la couleur au titre de l'aide (blanc comme dans l'epilog)
            for i, line in enumerate(help_section):
                if '💡 Pour plus d\'aide:' in line or '💡 Pour plus d\'aide:' in line:
                    help_section[i] = '\033[1;37m💡 Pour plus d\'aide:\033[0m'
                    break
            reordered_lines.extend(help_section)
            reordered_lines.append("")  # Ligne vide après l'aide

        # 8. Note
        if note_section:
            # Ajouter de la couleur au titre de la note (rouge pour les avertissements)
            for i, line in enumerate(note_section):
                if '⚠️  Important:' in line or '⚠️  Important:' in line:
                    note_section[i] = '\033[1;31m⚠️  Important:\033[0m'
                    break
            reordered_lines.extend(note_section)

        # 7. Arguments positionnels (SUPPRIMÉ - redondant avec notre section personnalisée)
        # Ne pas afficher la section "Arguments positionnels" car elle est redondante
        # if positionals_section:
        #     reordered_lines.extend(positionals_section)

        # Nettoyer les lignes vides en trop à la fin
        while reordered_lines and reordered_lines[-1] == "":
            reordered_lines.pop()

        return '\n'.join(reordered_lines) + '\n'


class CommandParser:
    """
    Parser principal pour la CLI Alexa Voice Control.

    Gère la création du parser argparse avec sous-commandes modulaires,
    les arguments globaux, et la validation des entrées.

    Attributes:
        parser (argparse.ArgumentParser): Parser principal
        subparsers (argparse._SubParsersAction): Conteneur des sous-parsers
        commands (dict): Dictionnaire des commandes enregistrées
        subcategory_commands (set): Ensemble des commandes qui utilisent des sous-catégories
    """

    def __init__(self, version: str = "2.0.0"):
        """
        Initialise le parser de commandes.

        Args:
            version: Version de la CLI
        """
        self.version = version
        self.parser = self._create_main_parser()
        self.subparsers = self.parser.add_subparsers(
            dest="category",
            metavar="CATEGORY",
            help="Catégorie de commande à exécuter",
        )
        self.commands: Dict[str, Type[BaseCommand]] = {}
        self.subcategory_commands: set[str] = set()  # Commandes avec sous-catégories

        logger.debug(f"CommandParser initialisé (version {version})")

    def _get_main_help_description(self) -> str:
        """
        Retourne la description principale de l'aide en utilisant le template personnalisé.
        
        Returns:
            Description formatée avec le template principal
        """
        from cli.help_texts.alexa_help import get_main_help
        return get_main_help()

    def _get_main_help_epilog(self) -> str:
        """
        Retourne l'epilog de l'aide principale.
        
        Returns:
            Epilog vide car tout est dans la description
        """
        # L'epilog est vide car tout le contenu est maintenant dans la description
        return ""

    def _create_main_parser(self) -> argparse.ArgumentParser:
        """
        Crée le parser principal avec arguments globaux.

        Returns:
            Parser argparse configuré
        """
        parser = argparse.ArgumentParser(
            prog="alexa",
            usage=None,  # Supprimer la ligne usage automatique pour utiliser notre version colorée
            description=self._get_main_help_description(),
            epilog=self._get_main_help_epilog(),
            formatter_class=NoOptionsHelpFormatter,  # Utiliser le formatter qui masque les options
            add_help=False,  # Désactiver l'aide automatique d'argparse
        )

        # Version
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        # Arguments globaux (mais sans -h/--help automatique)
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Mode verbeux (affiche logs détaillés)"
        )

        parser.add_argument(
            "--debug",
            action="store_true",
            help="Mode debug (affiche tous les logs y compris debug)",
        )

        parser.add_argument(
            "--json",
            action="store_true",
            dest="json_output",
            help="Sortie au format JSON (pour scripts)",
        )

        # Ajouter manuellement l'option help
        parser.add_argument(
            "-h", "--help", action="help", help="Afficher l'aide contextuelle"
        )

        return parser

    def register_command(self, name: str, command_class: Type[BaseCommand]) -> None:
        """
        Enregistre une commande dans le parser.

        Cette méthode crée un sous-parser pour la catégorie et appelle
        la méthode setup_parser() de la commande pour configurer les actions.

        Args:
            name: Nom de la catégorie (ex: 'device', 'music')
            command_class: Classe de commande héritant de BaseCommand

        Example:
            >>> from cli.commands.device import DeviceCommand
            >>> parser.register_command('device', DeviceCommand)
        """
        # Pas de parser parent nécessaire - argparse gère les globaux du parser principal
        # automatiquement pour tous les subparsers

        # Créer le sous-parser pour cette catégorie
        category_parser = self.subparsers.add_parser(
            name, help=f"Commandes {name}"
        )

        # Stocker la classe de commande
        self.commands[name] = command_class

        # Créer une instance temporaire pour analyser la structure du parser
        temp_instance = command_class(context=None)
        temp_instance.setup_parser(category_parser)

        # Détecter automatiquement si cette commande utilise des sous-catégories
        # en vérifiant si le parser a un sous-parser avec dest="subcategory"
        if hasattr(category_parser, '_subparsers') and category_parser._subparsers:
            for action in category_parser._actions:
                if hasattr(action, 'dest') and action.dest == 'subcategory':
                    self.subcategory_commands.add(name)
                    logger.debug(f"Commande '{name}' détectée comme utilisant des sous-catégories")
                    break

        logger.debug(f"Commande '{name}' enregistrée")

    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parse les arguments de ligne de commande.

        Args:
            args: Liste d'arguments (None = sys.argv)

        Returns:
            Namespace avec arguments parsés

        Raises:
            SystemExit: Si erreur de parsing ou --help
        """
        actual_args = args if args is not None else sys.argv[1:]
        
        # Vérifier si --help ou -h est demandé - dans ce cas, laisser argparse gérer normalement
        if '--help' in actual_args or '-h' in actual_args:
            # argparse va afficher l'aide et faire sys.exit, c'est normal
            return self.parser.parse_args(args)
        
        try:
            parsed_args = self.parser.parse_args(args)
        except SystemExit as e:
            # Si erreur de parsing (pas --help), afficher l'aide appropriée après l'erreur
            # Utiliser e pour éviter l'erreur de lint
            _ = e

            # Essayer de déterminer la catégorie depuis les args
            category = None
            if actual_args and len(actual_args) > 0:
                potential_category = actual_args[0]
                if potential_category in self.commands:
                    category = potential_category

            if category:
                # Afficher directement l'aide complète de la catégorie
                print(file=sys.stderr)  # Ligne vide pour séparer l'erreur de l'aide
                # Récupérer le parser de la catégorie et afficher son aide
                for action in self.parser._subparsers._actions:
                    if isinstance(action, argparse._SubParsersAction):
                        if category in action.choices:
                            action.choices[category].print_help(sys.stderr)
                            break
            else:
                # Pas de catégorie valide, afficher l'aide générale
                print(f"\n💡 Pour voir toutes les catégories disponibles:", file=sys.stderr)
                self.print_help()
            # Re-lever l'exception pour terminer le programme
            raise

        # Validation: une catégorie doit être spécifiée
        if not parsed_args.category:
            self.parser.print_help()
            logger.error("Aucune catégorie spécifiée")
            sys.exit(1)

        logger.debug(f"Arguments parsés: {parsed_args}")
        return parsed_args

    def get_command_class(self, category: str) -> Optional[Type[BaseCommand]]:
        """
        Récupère la classe de commande pour une catégorie.

        Args:
            category: Nom de la catégorie

        Returns:
            Classe de commande ou None si non trouvée
        """
        return self.commands.get(category)

    def print_help(self) -> None:
        """Affiche l'aide complète."""
        self.parser.print_help()

    def print_category_help(self, category: str) -> None:
        """
        Affiche l'aide pour une catégorie spécifique.

        Args:
            category: Nom de la catégorie
        """
        if category in self.commands:
            # Vérifier si cette commande utilise des sous-catégories
            if category in self.subcategory_commands:
                # Pour les commandes avec sous-catégories, afficher l'aide de la catégorie
                # qui montrera les sous-catégories disponibles
                try:
                    self.parser.parse_args([category, "--help"])
                except SystemExit:
                    pass  # --help fait un sys.exit(), c'est normal
            else:
                # Pour les commandes normales, afficher l'aide de la catégorie
                try:
                    self.parser.parse_args([category, "--help"])
                except SystemExit:
                    pass  # --help fait un sys.exit(), c'est normal
        else:
            logger.error(f"Catégorie '{category}' inconnue")
            self.print_help()


def create_parser(version: str = "2.0.0") -> CommandParser:
    """
    Factory function pour créer un parser de commandes.

    Args:
        version: Version de la CLI

    Returns:
        CommandParser configuré

    Example:
        >>> parser = create_parser()
        >>> parser.register_command('device', DeviceCommand)
        >>> args = parser.parse_args(['device', 'list'])
    """
    return CommandParser(version=version)


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test du parser
    parser = create_parser()

    print("✅ CommandParser créé avec succès")
    print(f"✅ Version: {parser.version}")
    print(f"✅ Catégories enregistrées: {len(parser.commands)}")

    # Afficher l'aide
    parser.print_help()
