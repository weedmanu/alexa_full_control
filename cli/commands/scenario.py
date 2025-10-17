"""Commande de gestion des scénarios/macros Alexa.

Ce module fournit une interface CLI pour créer et gérer des séquences de commandes:
- Créer un nouveau scénario
- Exécuter un scénario
- Lister les scénarios existants
- Supprimer un scénario
- Voir détails d'un scénario
- Éditer un scénario
"""

import argparse
import json
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter
from cli.help_texts.scenario_help import CREATE_HELP, DELETE_HELP, EDIT_HELP, INFO_HELP, LIST_HELP, RUN_HELP, SCENARIO_DESCRIPTION

# Constantes de description simplifiées
DESCRIPTION = "Gérer les scénarios/macros Alexa"


class ScenarioCommand(BaseCommand):
    """
    Commande pour gérer les scénarios/macros (séquences de commandes) Alexa.

    Les scénarios permettent de créer des séquences de commandes réutilisables
    avec gestion des délais entre les actions.

    Exemples:
        >>> # Lister tous les scénarios
        >>> alexa scenario list

        >>> # Créer un scénario
        >>> alexa scenario create --name "Ambiance Salon" \\
        ...   --actions '[{"device": "Salon Echo", "action": "volume", "params": {"level": 50}}]'

        >>> # Exécuter un scénario
        >>> alexa scenario run --name "Ambiance Salon"

        >>> # Voir détails d'un scénario
        >>> alexa scenario show --name "Ambiance Salon"

        >>> # Supprimer un scénario
        >>> alexa scenario delete --name "Ambiance Salon"
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "scenario"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "Gérer les scénarios/macros (séquences de commandes)"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande scenario.

        Args:
            parser: Parser à configurer
        """
        # Utiliser le formatter universel
        parser.formatter_class = UniversalHelpFormatter
        parser.description = SCENARIO_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: list
        subparsers.add_parser(
            "list",
            help="Lister scénarios",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="Créer scénario",
            description=CREATE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        create_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du scénario",
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
            help="Exécuter scénario",
            description=RUN_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        run_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du scénario à exécuter",
        )

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Supprimer scénario",
            description=DELETE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        delete_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du scénario à supprimer",
        )
        delete_parser.add_argument(
            "--force",
            action="store_true",
            help="Confirmer la suppression sans demander",
        )

        # Action: show
        show_parser = subparsers.add_parser(
            "show",
            help="Voir détails",
            description=INFO_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        show_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du scénario",
        )

        # Action: edit
        edit_parser = subparsers.add_parser(
            "edit",
            help="Éditer scénario",
            description=EDIT_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        edit_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="NAME",
            help="Nom du scénario",
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
        Exécute la commande scenario.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
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
        """Lister tous les scénarios."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            scenarios = ctx.scenario_mgr.get_scenarios()

            if not scenarios:
                self.warning("Aucun scénario trouvé")
                return True

            self._display_scenarios(list(scenarios.values()))
            return True

        except Exception as e:
            self.logger.exception("Erreur lors du listage")
            self.error(f"Erreur: {e}")
            return False

    def _create_scenario(self, args: argparse.Namespace) -> bool:
        """Créer un nouveau scénario."""
        try:
            # Parser les actions JSON
            try:
                actions = json.loads(args.actions)
                if not isinstance(actions, list):
                    self.error("Les actions doivent être une liste JSON")
                    return False
            except json.JSONDecodeError as e:
                self.error(f"JSON invalide: {e}")
                return False

            self.info(f"🔄 Création scénario '{args.name}' avec {len(actions)} action(s)...")

            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            result = self.call_with_breaker(ctx.scenario_mgr.create_scenario, args.name, actions)

            if result:
                self.success(f"✅ Scénario '{args.name}' créé avec succès")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la création")
            self.error(f"Erreur: {e}")
            return False

    def _run_scenario(self, args: argparse.Namespace) -> bool:
        """Exécuter un scénario."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            self.info(f"▶️  Exécution du scénario '{args.name}'...")

            result = self.call_with_breaker(ctx.scenario_mgr.run_scenario, args.name, ctx.auth)

            if result:
                self.success(f"✅ Scénario '{args.name}' exécuté avec succès")
                return True

            self.warning(f"⚠️  Scénario '{args.name}' non trouvé ou erreur d'exécution")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'exécution")
            self.error(f"Erreur: {e}")
            return False

    def _delete_scenario(self, args: argparse.Namespace) -> bool:
        """Supprimer un scénario."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            # Demander confirmation sauf si --force
            if not args.force:
                response = input(f"Êtes-vous sûr de vouloir supprimer '{args.name}'? (y/n): ")
                if response.lower() not in ["y", "yes", "oui", "o"]:
                    self.warning("Suppression annulée")
                    return True

            result = self.call_with_breaker(ctx.scenario_mgr.delete_scenario, args.name)

            if result:
                self.success(f"✅ Scénario '{args.name}' supprimé avec succès")
                return True

            self.warning(f"⚠️  Scénario '{args.name}' non trouvé")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression")
            self.error(f"Erreur: {e}")
            return False

    def _show_scenario_info(self, args: argparse.Namespace) -> bool:
        """Afficher les informations d'un scénario."""
        try:
            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            scenario = ctx.scenario_mgr.get_scenario(args.name)

            if not scenario:
                self.error(f"Scénario '{args.name}' non trouvé")
                return False

            self._display_scenario_details(scenario)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de l'affichage")
            self.error(f"Erreur: {e}")
            return False

    def _edit_scenario(self, args: argparse.Namespace) -> bool:
        """Éditer les actions d'un scénario."""
        try:
            # Parser les nouvelles actions JSON
            try:
                new_actions = json.loads(args.actions)
                if not isinstance(new_actions, list):
                    self.error("Les actions doivent être une liste JSON")
                    return False
            except json.JSONDecodeError as e:
                self.error(f"JSON invalide: {e}")
                return False

            ctx = self.require_context()
            if not ctx.scenario_mgr:
                self.error("ScenarioManager non disponible")
                return False

            self.info(f"✏️  Édition scénario '{args.name}' avec {len(new_actions)} action(s)...")

            result = self.call_with_breaker(ctx.scenario_mgr.edit_scenario, args.name, new_actions)

            if result:
                self.success(f"✅ Scénario '{args.name}' édité avec succès")
                return True

            self.warning(f"⚠️  Scénario '{args.name}' non trouvé")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'édition")
            self.error(f"Erreur: {e}")
            return False

    def _display_scenarios(self, scenarios: list) -> None:
        """Affiche la liste des scénarios de manière formatée."""
        print(f"\n📋 Scénarios ({len(scenarios)}):")
        print("=" * 80)

        for scenario in scenarios:
            name = scenario.get("name", "N/A")
            actions = scenario.get("actions", [])
            created = scenario.get("created", "N/A")

            print(f"\n🎬 {name} ({len(actions)} action(s))")
            print(f"   Créé: {created}")

            if actions:
                print("   Actions:")
                for i, action in enumerate(actions, 1):
                    device = action.get("device", "?")
                    act = action.get("action", "?")
                    delay = action.get("delay", 0)
                    delay_str = f" (+{delay}s délai)" if delay > 0 else ""
                    print(f"     {i}. {act} sur {device}{delay_str}")

    def _display_scenario_details(self, scenario: dict) -> None:
        """Affiche les détails d'un scénario de manière formatée."""
        name = scenario.get("name", "N/A")
        actions = scenario.get("actions", [])
        created = scenario.get("created", "N/A")
        modified = scenario.get("modified", "N/A")

        print(f"\n🎬 Scénario: {name}")
        print("=" * 80)
        print(f"Créé: {created}")
        print(f"Modifié: {modified}")
        print(f"Total: {len(actions)} action(s)")

        if actions:
            print("\n📝 Détail des actions:")
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
                    print(f"    - Paramètres: {params}")
                if delay > 0:
                    print(f"    - Délai avant: {delay}s")

            if total_delay > 0:
                print(f"\n⏱️  Durée totale estimée: {total_delay}s")
