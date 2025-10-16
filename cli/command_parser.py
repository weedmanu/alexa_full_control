"""cli.command_parser
=================================

Parser principal pour la CLI avec subparsers modulaires.

Principales remarques:
- Ce module utilise argparse standard pour une aide simple et cohérente.
- La CLI supporte les options globales standard (--help, --version, etc.).

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from loguru import logger

if TYPE_CHECKING:
    from cli.base_command import BaseCommand


class UniversalHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter d'aide simple pour argparse standard.
    """

    pass


class ActionHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter d'aide pour les actions, simple et standard.
    """

    pass


class CommandParser:
    """
    Parser principal pour la CLI Alexa Voice Control.

    Utilise argparse standard pour une aide simple et cohérente.

    Attributes:
        parser (argparse.ArgumentParser): Parser principal
        subparsers (argparse._SubParsersAction): Conteneur des sous-parsers
        commands (dict): Dictionnaire des commandes enregistrées
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

        logger.debug(f"CommandParser initialisé (version {version})")

    def _create_main_parser(self) -> argparse.ArgumentParser:
        """
        Crée le parser principal avec arguments globaux.

        Returns:
            Parser argparse configuré
        """
        parser = argparse.ArgumentParser(
            prog="alexa",
            description="Contrôle des appareils Amazon Alexa",
            epilog="Utilisez 'alexa CATEGORY --help' pour l'aide d'une catégorie spécifique.",
        )

        # Version
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        # Arguments globaux
        parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")
        parser.add_argument("--debug", action="store_true", help="Mode debug")
        parser.add_argument("--json", action="store_true", help="Sortie au format JSON")

        return parser

    def register_command(self, name: str, command_class: "Type[BaseCommand]") -> None:
        """
        Enregistre une commande dans le parser.

        Args:
            name: Nom de la catégorie (ex: 'device', 'music')
            command_class: Classe de commande héritant de BaseCommand
        """
        # Créer le sous-parser pour cette catégorie
        category_parser = self.subparsers.add_parser(
            name, help=f"Commandes {name}", description=f"Gestion des fonctionnalités {name}"
        )

        # Stocker la classe de commande
        self.commands[name] = command_class

        # Créer une instance temporaire pour configurer le parser
        temp_instance = command_class(context=None)
        temp_instance.setup_parser(category_parser)

        logger.debug(f"Commande '{name}' enregistrée")

    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parse les arguments de ligne de commande.

        Args:
            args: Liste d'arguments (None = sys.argv)

        Returns:
            Namespace avec arguments parsés
        """
        return self.parser.parse_args(args)

    def get_command_class(self, category: str) -> Optional["Type[BaseCommand]"]:
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
