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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from loguru import logger

if TYPE_CHECKING:
    from cli.base_command import BaseCommand


class UniversalHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter d'aide compact : affiche la description et les positionnels seulement.
    """

    def format_help(self):
        # Build the full help using the base implementation, then extract
        # only the 'usage:' block and the 'positional arguments' section.
        full = super().format_help()
        lines = full.splitlines()

        # Find usage block
        usage_start = None
        for i, ln in enumerate(lines):
            if ln.strip().lower().startswith("usage:"):
                usage_start = i
                break

        if usage_start is None:
            # Aucun usage auto généré (ex: parser.usage = argparse.SUPPRESS).
            # Construire une ligne usage minimale basée sur le nom du programme
            prog = getattr(self, "prog", None) or getattr(self, "_prog", None) or "alexa"
            usage_block = [f"usage: {prog} ACTION"]
        else:
            # Trouver la fin du bloc usage (première ligne vide après usage_start)
            usage_end = usage_start + 1
            while usage_end < len(lines) and lines[usage_end].strip() != "":
                usage_end += 1

            usage_block = lines[usage_start:usage_end]

        # Normaliser pour éviter la duplication 'usage: usage: ...'
        # Choisir la première ligne significative qui contient le texte d'usage.
        usage_line = None
        for ln in usage_block:
            s = ln.strip()
            if s == "":
                continue
            # Ignorer les lignes qui sont juste 'usage:'
            if s.lower() == "usage:":
                continue
            usage_line = s
            break
        if usage_line is None:
            # fallback
            usage_line = usage_block[0].strip() if usage_block else "usage: alexa ACTION"
        # Normaliser pour n'avoir qu'un seul préfixe 'usage:' même si
        # parser.usage contenait déjà 'usage: ...' (évite 'usage: usage: ...').
        u = usage_line
        # Retirer tous les préfixes 'usage:' successifs
        while u.lower().startswith("usage:"):
            u = u[len("usage:"):].strip()
        usage_line = f"usage: {u}"
        usage_block = [usage_line]

        # (usage_block est déjà construit ci-dessus selon que usage_start existe)
        # Find 'positional arguments' heading
        pos_start = None
        for i, ln in enumerate(lines):
            if ln.strip().lower().startswith("positional arguments"):
                pos_start = i
                break

        positional_block = []
        if pos_start is not None:
            # include heading line and subsequent indented lines until a blank line
            i = pos_start
            while i < len(lines) and lines[i].strip() != "":
                positional_block.append(lines[i])
                i += 1

        # Find 'options' / 'optional arguments' heading (argparse uses
        # 'optional arguments' but in some localisations or custom formatters
        # it may appear as 'options'). Accept both.
        opt_start = None
        for i, ln in enumerate(lines):
            low = ln.strip().lower()
            if low.startswith("optional arguments") or low.startswith("options"):
                opt_start = i
                break

        options_block = []
        if opt_start is not None:
            j = opt_start
            while j < len(lines) and lines[j].strip() != "":
                options_block.append(lines[j])
                j += 1

        # Construct output: usage, blank line, positional_block
        out = []
        out.extend(usage_block)
        if positional_block:
            out.append("")
            out.extend(positional_block)

        if options_block:
            out.append("")
            out.extend(options_block)

        return "\n".join(out) + "\n"


# ActionHelpFormatter a été supprimé: on utilise UniversalHelpFormatter partout.


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
        # Désactiver le help automatique pour pouvoir fournir un texte d'aide
        # en français (-h/--help) de manière cohérente sur tous les parsers.
        parser = argparse.ArgumentParser(
            prog="alexa",
            description="",
            epilog="Utilisez 'alexa CATEGORY --help' pour l'aide d'une catégorie spécifique.",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )

        # Ajouter explicitement -h/--help avec libellé en français
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            help="Afficher ce message d'aide et quitter",
        )

        # Version
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}", help="Afficher la version et quitter")

        # Arguments globaux
        parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")
        parser.add_argument("--debug", action="store_true", help="Mode debug")
        parser.add_argument("--json", action="store_true", help="Sortie au format JSON")

        # Définit une usage minimale pour la page principale
        try:
            prog = parser.prog
        except Exception:
            prog = "alexa"
        parser.usage = f"{prog} [OPTIONS] CATEGORY ACTION"

        return parser

    def register_command(self, name: str, command_class: "Type[BaseCommand]") -> None:
        """
        Enregistre une commande dans le parser.

        Args:
            name: Nom de la catégorie (ex: 'device', 'music')
            command_class: Classe de commande héritant de BaseCommand
        """
        # Créer le sous-parser pour cette catégorie
        # Créer le sous-parser sans l'aide automatique pour injecter
        # un libellé d'aide en français.
        category_parser = self.subparsers.add_parser(
            name,
            help=f"Commandes {name}",
            description="",
            formatter_class=UniversalHelpFormatter,
            add_help=False,
        )

        # Ajouter -h/--help local en français pour la catégorie
        category_parser.add_argument(
            "-h",
            "--help",
            action="help",
            help="Afficher ce message d'aide et quitter",
        )

        # Définir une ligne d'usage standard incluant les options globales
        try:
            prog = self.parser.prog
        except Exception:
            prog = "alexa"
        category_parser.usage = f"{prog} [OPTIONS] {name} ACTION"

        # Stocker la classe de commande
        self.commands[name] = command_class

        # Configurer le parser pour la commande:
        # - Si la classe expose une méthode de classe `setup_parser`, l'utiliser
        #   (cela permet d'éviter d'instancier la commande pour l'enregistrement)
        # - Sinon, retomber sur l'instance temporaire (comportement historique)
        setup_done = False
        try:
            setup = getattr(command_class, "setup_parser", None)
            if setup and callable(setup):
                # Certains setup_parser sont des méthodes d'instance et d'autres
                # des fonctions de classe. Pour satisfaire mypy, on force un
                # cast en Any lors de l'appel - le runtime accepte les deux.
                try:
                    # Appel en tant que méthode de classe (cast pour mypy)
                    cast_any: Any = command_class
                    cast_any.setup_parser(category_parser)
                    setup_done = True
                except TypeError:
                    setup = None

        except Exception:
            setup = None

        if not setup_done:
            # Fallback historique: instancier et appeler setup_parser.
            # Certaines classes de commande n'acceptent pas 'context' en
            # argument du constructeur; on tente plusieurs variantes.
            temp_instance = None
            try:
                temp_instance = command_class(context=None)
            except TypeError:
                try:
                    temp_instance = command_class()
                except Exception as e:
                    logger.debug(f"Impossible d'instancier {command_class}: {e}")

            if temp_instance is not None:
                try:
                    temp_instance.setup_parser(category_parser)
                except Exception as e:
                    logger.debug(f"Erreur dans setup_parser pour {command_class}: {e}")

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
