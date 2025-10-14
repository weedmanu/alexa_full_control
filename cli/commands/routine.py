"""Commande de gestion des routines Alexa.

Ce module fournit une interface CLI pour gérer les routines Alexa :
- Lister les routines configurées
- Afficher les détails d'une routine
- Exécuter une routine
- Activer/désactiver des routines
"""

from cli.help_texts.routine_help import (
    ROUTINE_DESCRIPTION,
    LIST_HELP,
    INFO_HELP,
    EXECUTE_HELP,
    ENABLE_HELP,
    DISABLE_HELP,
)

import argparse

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter, ActionHelpFormatter


class RoutineCommand(BaseCommand):
    """
    Commande pour gérer les routines Alexa.

    Exemples:
        >>> # Lister toutes les routines
        >>> alexa routine list

        >>> # Afficher détails d'une routine
        >>> alexa routine info --id amzn1.alexa.routine.xxx

        >>> # Exécuter une routine
        >>> alexa routine execute --id amzn1.alexa.routine.xxx

        >>> # Activer une routine
        >>> alexa routine enable --id amzn1.alexa.routine.xxx

        >>> # Désactiver une routine
        >>> alexa routine disable --id amzn1.alexa.routine.xxx
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "routine"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "Gérer les routines Alexa"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande routine.

        Args:
            parser: Parser à configurer
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter
        
        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description centralisée
        parser.description = ROUTINE_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: list
        list_parser = subparsers.add_parser("list", help="Lister routines", description=LIST_HELP, formatter_class=ActionHelpFormatter, add_help=False)
        list_parser.add_argument(
            "--only-active", action="store_true", help="Afficher uniquement les routines activées"
        )

        # Action: info
        info_parser = subparsers.add_parser("info", help="Détails routine", description=INFO_HELP, formatter_class=ActionHelpFormatter, add_help=False)
        info_parser.add_argument(
            "--name", type=str, required=True, metavar="ROUTINE_NAME", help="Nom de la routine"
        )
        info_parser.add_argument(
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )

        # Action: execute
        exec_parser = subparsers.add_parser(
            "execute", help="Exécuter routine", description=EXECUTE_HELP, formatter_class=ActionHelpFormatter, add_help=False
        )
        exec_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="ROUTINE_NAME",
            help="Nom de la routine à exécuter",
        )
        exec_parser.add_argument(
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil sur lequel exécuter la routine",
        )

        # Action: enable
        enable_parser = subparsers.add_parser(
            "enable", help="Activer routine", description=ENABLE_HELP, formatter_class=ActionHelpFormatter, add_help=False
        )
        enable_parser.add_argument(
            "--name", type=str, required=True, metavar="ROUTINE_NAME", help="Nom de la routine à activer"
        )
        enable_parser.add_argument(
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )

        # Action: disable
        disable_parser = subparsers.add_parser(
            "disable", help="Désactiver routine", description=DISABLE_HELP, formatter_class=ActionHelpFormatter, add_help=False
        )
        disable_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="ROUTINE_NAME",
            help="Nom de la routine à désactiver",
        )
        disable_parser.add_argument(
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande routine.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "list":
            return self._list_routines(args)
        elif args.action == "info":
            return self._show_info(args)
        elif args.action == "execute":
            return self._execute_routine(args)
        elif args.action == "enable":
            return self._enable_routine(args)
        elif args.action == "disable":
            return self._disable_routine(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _list_routines(self, args: argparse.Namespace) -> bool:
        """Lister les routines."""
        try:
            only_active = getattr(args, "only_active", False)

            self.info("📋 Récupération des routines...")

            if not self.context.routine_mgr:
                self.error("RoutineManager non disponible")
                return False

            routines = self.call_with_breaker(self.context.routine_mgr.get_routines)

            if not routines:
                self.warning("Aucune routine trouvée")
                return True

            # Filtrer selon le statut (actif/inactif)
            if only_active:
                # Une routine est activée si status != "DISABLED"
                routines = [r for r in routines if r.get("status") != "DISABLED"]

            # Afficher les routines
            self._display_routines(routines)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération des routines")
            self.error(f"Erreur: {e}")
            return False

    def _show_info(self, args: argparse.Namespace) -> bool:
        """Afficher les détails d'une routine."""
        try:
            self.info(f"📋 Récupération détails routine '{args.name}'...")

            if not self.context.routine_mgr:
                self.error("RoutineManager non disponible")
                return False

            routine = self._find_routine_by_name(args.name)

            if not routine:
                self.error(f"Routine '{args.name}' non trouvée")
                return False

            # Afficher les détails
            self._display_routine_details(routine)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération des détails")
            self.error(f"Erreur: {e}")
            return False

    def _execute_routine(self, args: argparse.Namespace) -> bool:
        """Exécuter une routine."""
        try:
            self.info(f"▶️  Exécution routine '{args.name}'...")

            if not self.context.routine_mgr:
                self.error("RoutineManager non disponible")
                return False

            # Trouver la routine par nom
            routine = self._find_routine_by_name(args.name)
            if not routine:
                self.error(f"Routine '{args.name}' non trouvée")
                return False

            routine_id = routine.get("automationId")

            # Récupérer le device si spécifié via --device (depuis le global args)
            device_serial = None
            device_type = None

            # L'option --device est au niveau global du parser, pas au niveau routine
            if hasattr(args, "device") and args.device:
                # Utiliser le DeviceManager du contexte pour récupérer le device
                if self.context.device_mgr:
                    devices = self.call_with_breaker(self.context.device_mgr.get_devices) or []
                    device_name_lower = args.device.lower().strip()

                    for dev in devices:
                        if dev.get("accountName", "").lower().strip() == device_name_lower:
                            device_serial = dev.get("serialNumber")
                            device_type = dev.get("deviceType")
                            self.logger.debug(
                                f"Device cible: {dev.get('accountName')} (serial={device_serial}, type={device_type})"
                            )
                            break

                    if not device_serial:
                        self.logger.warning(
                            f"Device '{args.device}' introuvable, exécution sans device cible"
                        )

            result = self.call_with_breaker(
                self.context.routine_mgr.execute_routine,
                routine_id,
                device_serial=device_serial,
                device_type=device_type,
            )

            if result:
                self.success("✅ Routine exécutée avec succès")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'exécution de la routine")
            self.error(f"Erreur: {e}")
            return False

    def _enable_routine(self, args: argparse.Namespace) -> bool:
        """Activer une routine."""
        try:
            self.info(f"✓ Activation routine '{args.name}'...")

            if not self.context.routine_mgr:
                self.error("RoutineManager non disponible")
                return False

            # Trouver la routine par nom
            routine = self._find_routine_by_name(args.name)
            if not routine:
                self.error(f"Routine '{args.name}' non trouvée")
                return False

            routine_id = routine.get("automationId")

            result = self.call_with_breaker(
                self.context.routine_mgr.set_routine_enabled, routine_id, True
            )

            if result:
                self.success("✅ Routine activée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'activation de la routine")
            self.error(f"Erreur: {e}")
            return False

    def _disable_routine(self, args: argparse.Namespace) -> bool:
        """Désactiver une routine."""
        try:
            self.info(f"✗ Désactivation routine '{args.name}'...")

            if not self.context.routine_mgr:
                self.error("RoutineManager non disponible")
                return False

            # Trouver la routine par nom
            routine = self._find_routine_by_name(args.name)
            if not routine:
                self.error(f"Routine '{args.name}' non trouvée")
                return False

            routine_id = routine.get("automationId")

            result = self.call_with_breaker(
                self.context.routine_mgr.set_routine_enabled, routine_id, False
            )

            if result:
                self.success("✅ Routine désactivée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la désactivation de la routine")
            self.error(f"Erreur: {e}")
            return False

    def _find_routine_by_name(self, name: str) -> dict | None:
        """
        Trouve une routine par son nom.
        
        Args:
            name: Nom de la routine à chercher
            
        Returns:
            Dict de la routine ou None si non trouvée
        """
        try:
            routines = self.call_with_breaker(self.context.routine_mgr.get_routines)
            if not routines:
                return None
                
            # Recherche exacte (insensible à la casse)
            name_lower = name.lower().strip()
            for routine in routines:
                routine_name = routine.get("name", "").lower().strip()
                if routine_name == name_lower:
                    return routine
                    
            return None
            
        except Exception as e:
            self.logger.exception(f"Erreur lors de la recherche de la routine '{name}'")
            return None

    def _display_routines(self, routines: list) -> None:
        """Affiche la liste des routines de manière formatée."""
        if not routines:
            print("  Aucune routine trouvée")
            return

        self.info(f"📋 {len(routines)} routine(s) trouvée(s):\n")

        # Préparer les données pour le tableau
        table_data = []
        for routine in routines:
            name = routine.get("name", "Sans nom")
            routine_id = routine.get("automationId", "N/A")
            # Une routine est activée si status != "DISABLED"
            enabled = routine.get("status") != "DISABLED"
            
            status = "🟢 Activée" if enabled else "🔴 Désactivée"

            # Afficher trigger si disponible
            trigger = routine.get("trigger", {})
            trigger_type = trigger.get("type", "N/A")
            
            # Tronquer l'ID pour l'affichage
            short_id = routine_id.split(".")[-1][:20] if "." in routine_id else routine_id[:20]

            table_data.append([name, status, trigger_type, short_id])

        # Afficher le tableau
        table = self.format_table(table_data, ["Nom", "État", "Déclencheur", "ID"])
        print(table)

    def _display_routine_details(self, routine: dict) -> None:
        """Affiche les détails complets d'une routine."""
        name = routine.get("name", "Sans nom")
        routine_id = routine.get("automationId", "N/A")
        enabled = routine.get("status") != "DISABLED"

        print(f"\n📋 Routine: {name}")
        print(f"  ID: {routine_id}")
        print(f"  État: {'Activée ✓' if enabled else 'Désactivée ✗'}")

        # Déclencheur
        trigger = routine.get("trigger", {})
        if trigger:
            print("\n  🔔 Déclencheur:")
            trigger_type = trigger.get("type", "N/A")
            print(f"     Type: {trigger_type}")

            # Détails selon le type
            if trigger_type == "Schedule":
                schedule = trigger.get("schedule", {})
                print(f"     Horaire: {schedule.get('originalTime', 'N/A')}")
                days = schedule.get("recurrence", {}).get("freqValues", [])
                if days:
                    print(f"     Jours: {', '.join(days)}")
            elif trigger_type == "Voice":
                utterance = trigger.get("utterance", "N/A")
                print(f'     Phrase: "{utterance}"')

        # Actions
        actions = routine.get("sequence", {}).get("sequenceJson", [])
        if actions:
            print(f"\n  ▶️  Actions ({len(actions)}):")
            for i, action in enumerate(actions, 1):
                action_type = action.get("type", "N/A")
                print(f"     {i}. {action_type}")
