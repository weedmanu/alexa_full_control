﻿"""Commande de gestion des sc�narios/macros Alexa.

Ce module fournit une interface CLI pour cr�er et g�rer des s�quences de commandes:
- Cr�er un nouveau sc�nario
- Ex�cuter un sc�nario
- Lister les sc�narios existants
- Supprimer un sc�nario
- Voir d�tails d'un sc�nario
- �diter un sc�nario
"""

import argparse
import json

from utils.cli.base_command import BaseCommand
from utils.cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter

# Constantes de description simplifi�es
DESCRIPTION = "G�rer les sc�narios/macros Alexa"

# Descriptions des actions
CREATE_HELP = "Cr�er un nouveau sc�nario"
DELETE_HELP = "Supprimer un sc�nario existant"
EDIT_HELP = "�diter les actions d'un sc�nario"
INFO_HELP = "Afficher les d�tails d'un sc�nario"
LIST_HELP = "Lister tous les sc�narios"
RUN_HELP = "Ex�cuter un sc�nario"

# Description principale
SCENARIO_DESCRIPTION = "Gestion des sc�narios/macros Alexa"


class ScenarioCommand(BaseCommand):
    """
    Commande pour g�rer les sc�narios/macros (s�quences de commandes) Alexa.

    Les sc�narios permettent de cr�er des s�quences de commandes r�utilisables
    avec gestion des d�lais entre les actions.

    Exemples:
        >>> # Lister tous les sc�narios
        >>> alexa scenario list

        >>> # Cr�er un sc�nario
        >>> alexa scenario create --name "Ambiance Salon" \\
        ...   --actions '[{"device": "Salon Echo", "action": "volume", "params": {"level": 50}}]'

        >>> # Ex�cuter un sc�nario
        >>> alexa scenario run --name "Ambiance Salon"

        >>> # Voir d�tails d'un sc�nario
        >>> alexa scenario show --name "Ambiance Salon"

        >>> # Supprimer un sc�nario
        >>> alexa scenario delete --name "Ambiance Salon"
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "scenario"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "G�rer les sc�narios/macros (s�quences de commandes)"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande scenario.

        Args:
            parser: Parser � configurer
        """
        # Utiliser le formatter universel
        parser.formatter_class = UniversalHelpFormatter
        parser.description = SCENARIO_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action � ex�cuter",
            required=True,
        )

        # Action: list
        subparsers.add_parser(
            "list",
            help="Lister sc�narios",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="Cr�er sc�nario",
            description=CREATE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        create_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du sc�nario",
        )
        create_parser.add_argument(
            "--actions",
            type=str,
            required=True,
            metavar="JSON",
            help='Actions en JSON: \'[{"device": "Device", "action": "...", "params": {...}, "delay": 0}]\'',
        )

        # Action: run
        run_parser = subparsers.add_parser(
            "run",
            help="Ex�cuter sc�nario",
            description=RUN_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        run_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du sc�nario � ex�cuter",
        )

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Supprimer sc�nario",
            description=DELETE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        delete_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du sc�nario � supprimer",
        )
        delete_parser.add_argument(
            "--force",
            action="store_true",
            help="Confirmer la suppression sans demander",
        )

        # Action: show
        show_parser = subparsers.add_parser(
            "show",
            help="Voir d�tails",
            description=INFO_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        show_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du sc�nario",
        )

        # Action: edit
        edit_parser = subparsers.add_parser(
            "edit",
            help="�diter sc�nario",
            description=EDIT_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        edit_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du sc�nario",
        )
        edit_parser.add_argument(
            "--actions",
            type=str,
            required=True,
            metavar="JSON",
            help="Nouvelles actions en JSON",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Ex�cute la commande scenario.

        Args:
            args: Arguments pars�s

        Returns:
            True si succ�s, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "list":
            return self._list_scenarios(args)
        elif args.action == "create":
            return self._create_scenario(args)
        elif args.action == "run":
            return self._run_scenario(args)
        elif args.action == "delete":
            return self._delete_scenario(args)
        elif args.action == "show":
            return self._show_scenario_info(args)
        elif args.action == "edit":
            return self._edit_scenario(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _list_scenarios(self, args: argparse.Namespace) -> bool:
        """Lister tous les sc�narios."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            scenarios = ctx.scenario_mgr.get_scenarios()

            if not scenarios:
                self.warning("Aucun sc�nario trouv�")
                return True

            self._display_scenarios(list(scenarios.values()))
            return True

        except Exception as e:
            self.logger.exception("Erreur lors du listage")
            self.error(f"Erreur: {e}")
            return False

    def _create_scenario(self, args: argparse.Namespace) -> bool:
        """Cr�er un nouveau sc�nario."""
        try:
            # Parser les actions JSON
            try:
                actions = json.loads(args.actions)
                if not isinstance(actions, list):
                    self.error("Les actions doivent �tre une liste JSON")
                    return False
            except json.JSONDecodeError as e:
                self.error(f"JSON invalide: {e}")
                return False

            self.info(f"?? Cr�ation sc�nario '{args.name}' avec {len(actions)} action(s)...")

            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            result = self.call_with_breaker(ctx.scenario_mgr.create_scenario, args.name, actions)

            if result:
                self.success(f"? Sc�nario '{args.name}' cr�� avec succ�s")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la cr�ation")
            self.error(f"Erreur: {e}")
            return False

    def _run_scenario(self, args: argparse.Namespace) -> bool:
        """Ex�cuter un sc�nario."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            self.info(f"??  Ex�cution du sc�nario '{args.name}'...")

            result = self.call_with_breaker(ctx.scenario_mgr.run_scenario, args.name, ctx.auth)

            if result:
                self.success(f"? Sc�nario '{args.name}' ex�cut� avec succ�s")
                return True

            self.warning(f"??  Sc�nario '{args.name}' non trouv� ou erreur d'ex�cution")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'ex�cution")
            self.error(f"Erreur: {e}")
            return False

    def _delete_scenario(self, args: argparse.Namespace) -> bool:
        """Supprimer un sc�nario."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            # Demander confirmation sauf si --force
            if not args.force:
                response = input(f"�tes-vous s�r de vouloir supprimer '{args.name}'? (y/n): ")
                if response.lower() not in ["y", "yes", "oui", "o"]:
                    self.warning("Suppression annul�e")
                    return True

            result = self.call_with_breaker(ctx.scenario_mgr.delete_scenario, args.name)

            if result:
                self.success(f"? Sc�nario '{args.name}' supprim� avec succ�s")
                return True

            self.warning(f"??  Sc�nario '{args.name}' non trouv�")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression")
            self.error(f"Erreur: {e}")
            return False

    def _show_scenario_info(self, args: argparse.Namespace) -> bool:
        """Afficher les informations d'un sc�nario."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            scenario = ctx.scenario_mgr.get_scenario(args.name)

            if not scenario:
                self.error(f"Sc�nario '{args.name}' non trouv�")
                return False

            self._display_scenario_details(scenario)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de l'affichage")
            self.error(f"Erreur: {e}")
            return False

    def _edit_scenario(self, args: argparse.Namespace) -> bool:
        """�diter les actions d'un sc�nario."""
        try:
            # Parser les nouvelles actions JSON
            try:
                new_actions = json.loads(args.actions)
                if not isinstance(new_actions, list):
                    self.error("Les actions doivent �tre une liste JSON")
                    return False
            except json.JSONDecodeError as e:
                self.error(f"JSON invalide: {e}")
                return False

            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            self.info(f"??  �dition sc�nario '{args.name}' avec {len(new_actions)} action(s)...")

            result = self.call_with_breaker(ctx.scenario_mgr.edit_scenario, args.name, new_actions)

            if result:
                self.success(f"? Sc�nario '{args.name}' �dit� avec succ�s")
                return True

            self.warning(f"??  Sc�nario '{args.name}' non trouv�")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'�dition")
            self.error(f"Erreur: {e}")
            return False

    def _display_scenarios(self, scenarios: list) -> None:
        """Affiche la liste des sc�narios de mani�re format�e."""
        print(f"\n?? Sc�narios ({len(scenarios)}):")
        print("=" * 80)

        for scenario in scenarios:
            name = scenario.get("name", "N/A")
            actions = scenario.get("actions", [])
            created = scenario.get("created", "N/A")

            print(f"\n?? {name} ({len(actions)} action(s))")
            print(f"   Cr��: {created}")

            if actions:
                print("   Actions:")
                for i, action in enumerate(actions, 1):
                    device = action.get("device", "?")
                    act = action.get("action", "?")
                    delay = action.get("delay", 0)
                    delay_str = f" (+{delay}s d�lai)" if delay > 0 else ""
                    print(f"     {i}. {act} sur {device}{delay_str}")

    def _display_scenario_details(self, scenario: dict) -> None:
        """Affiche les d�tails d'un sc�nario de mani�re format�e."""
        name = scenario.get("name", "N/A")
        actions = scenario.get("actions", [])
        created = scenario.get("created", "N/A")
        modified = scenario.get("modified", "N/A")

        print(f"\n?? Sc�nario: {name}")
        print("=" * 80)
        print(f"Cr��: {created}")
        print(f"Modifi�: {modified}")
        print(f"Total: {len(actions)} action(s)")

        if actions:
            print("\n?? D�tail des actions:")
            total_delay = 0
            for i, action in enumerate(actions, 1):
                device = action.get("device", "?")
                act = action.get("action", "?")
                params = action.get("params", {})
                delay = action.get("delay", 0)
                total_delay += delay

                print(f"\n  Action {i}:")
                print(f"    - Appareil: {device}")
                print(f"    - Commande: {act}")
                if params:
                    print(f"    - Param�tres: {params}")
                if delay > 0:
                    print(f"    - D�lai avant: {delay}s")

            if total_delay > 0:
                print(f"\n??  Dur�e totale estim�e: {total_delay}s")




