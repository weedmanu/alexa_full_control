"""
Commandes de gestion du mode Ne Pas DÃ©ranger (DND).

Ce module gÃ¨re toutes les opÃ©rations liÃ©es au DND:
- status: Statut DND d'un appareil
- enable: Activer le DND
- disable: DÃ©sactiver le DND
- schedule: Programmer le DND

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import json

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter

# Constantes de description simplifiÃ©es
DND_DESCRIPTION = "GÃ©rer le mode Ne Pas DÃ©ranger"
DISABLE_HELP = "DÃ©sactiver le DND"
ENABLE_HELP = "Activer le DND"
SCHEDULE_HELP = "Programmer le DND"
STATUS_HELP = "Statut DND d'un appareil"


class DNDCommand(BaseCommand):
    """
    Commande de gestion du mode Ne Pas DÃ©ranger.

    GÃ¨re status, enable, disable, schedule.

    Actions:
        - status: VÃ©rifier le statut DND
        - enable: Activer le mode DND
        - disable: DÃ©sactiver le mode DND
        - schedule: Programmer des horaires DND

    Example:
        >>> alexa dnd status -d "Salon Echo"
        >>> alexa dnd enable -d "Salon Echo"
        >>> alexa dnd disable -d "Salon Echo"
        >>> alexa dnd schedule -d "Salon Echo" --start 22:00 --end 07:00
        >>> alexa dnd schedule -d "Salon Echo" --start 22:00 --end 07:00 --days Mon,Tue,Wed,Thu,Fri
    """

    # Jours de la semaine
    DAYS = {
        "Mon": "Lundi",
        "Tue": "Mardi",
        "Wed": "Mercredi",
        "Thu": "Jeudi",
        "Fri": "Vendredi",
        "Sat": "Samedi",
        "Sun": "Dimanche",
    }

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes dnd.

        Args:
            parser: Sous-parser pour la catÃ©gorie 'dnd'
        """
        # Utiliser le formatter universel pour l'ordre exact demandÃ©
        parser.formatter_class = UniversalHelpFormatter

        # DÃ©finir un usage plus dÃ©taillÃ©
        parser.usage = "alexa [OPTIONS_GLOBALES] dnd <ACTION> [OPTIONS_ACTION]"

        # Description centralisÃ©e
        parser.description = DND_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: status
        status_parser = subparsers.add_parser(
            "status",
            help="Statut DND",
            description=STATUS_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        status_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )

        # Action: enable
        enable_parser = subparsers.add_parser(
            "enable",
            help="Activer DND",
            description=ENABLE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        enable_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )

        # Action: disable
        disable_parser = subparsers.add_parser(
            "disable",
            help="DÃ©sactiver DND",
            description=DISABLE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        disable_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )

        # Action: schedule
        schedule_parser = subparsers.add_parser(
            "schedule",
            help="Programmer DND",
            description=SCHEDULE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        schedule_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        schedule_parser.add_argument(
            "--start",
            type=str,
            required=True,
            metavar="HH:MM",
            help="Heure de dÃ©but (format 24h: HH:MM)",
        )
        schedule_parser.add_argument(
            "--end",
            type=str,
            required=True,
            metavar="HH:MM",
            help="Heure de fin (format 24h: HH:MM)",
        )
        schedule_parser.add_argument(
            "--days", type=str, metavar="DAYS", help="Jours (ex: Mon,Tue,Wed,Thu,Fri pour semaine)"
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        ExÃ©cute la commande dnd.

        Args:
            args: Arguments parsÃ©s

        Returns:
            True si succÃ¨s, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "status":
            return self._check_status(args)
        elif args.action == "enable":
            return self._enable_dnd(args)
        elif args.action == "disable":
            return self._disable_dnd(args)
        elif args.action == "schedule":
            return self._schedule_dnd(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _check_status(self, args: argparse.Namespace) -> bool:
        """VÃ©rifier le statut DND."""
        try:
            # RÃ©cupÃ©rer le serial de l'appareil
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"ðŸ”• Statut DND de '{args.device}'...")

            ctx = self.require_context()
            if not ctx.dnd_mgr:
                self.error("DNDManager non disponible")
                return False

            status = self.call_with_breaker(ctx.dnd_mgr.get_dnd_status, serial)

            if status is not None:
                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(status, indent=2, ensure_ascii=False))
                else:
                    self._display_status(args.device, status)

                return True
            else:
                self.warning(f"Aucun statut DND trouvÃ© pour '{args.device}' (serial: {serial})")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la vÃ©rification du statut DND")
            self.error(f"Erreur: {e}")
            return False

    def _enable_dnd(self, args: argparse.Namespace) -> bool:
        """Activer le DND."""
        try:
            # RÃ©cupÃ©rer le serial de l'appareil
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            device_type = self._get_device_type(args.device)
            self.info(f"ðŸ”• Activation DND sur '{args.device}'...")

            ctx = self.require_context()
            if not ctx.dnd_mgr:
                self.error("DNDManager non disponible")
                return False

            result = self.call_with_breaker(ctx.dnd_mgr.enable_dnd, serial, device_type)

            if result:
                self.success(f"âœ… DND activÃ© sur '{args.device}'")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'activation DND")
            self.error(f"Erreur: {e}")
            return False

    def _disable_dnd(self, args: argparse.Namespace) -> bool:
        """DÃ©sactiver le DND."""
        try:
            # RÃ©cupÃ©rer le serial de l'appareil
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            device_type = self._get_device_type(args.device)
            self.info(f"ðŸ”” DÃ©sactivation DND sur '{args.device}'...")

            ctx = self.require_context()
            if not ctx.dnd_mgr:
                self.error("DNDManager non disponible")
                return False

            result = self.call_with_breaker(ctx.dnd_mgr.disable_dnd, serial, device_type)

            if result:
                self.success(f"âœ… DND dÃ©sactivÃ© sur '{args.device}'")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la dÃ©sactivation DND")
            self.error(f"Erreur: {e}")
            return False

    def _schedule_dnd(self, args: argparse.Namespace) -> bool:
        """Programmer le DND."""
        try:
            # Validation des heures
            if not self._validate_time(args.start):
                self.error(f"Heure de dÃ©but invalide: {args.start} (format: HH:MM)")
                return False

            if not self._validate_time(args.end):
                self.error(f"Heure de fin invalide: {args.end} (format: HH:MM)")
                return False

            # Parser les jours si spÃ©cifiÃ©s
            days = None
            if hasattr(args, "days") and args.days:
                days = [d.strip() for d in args.days.split(",")]
                for day in days:
                    if day not in self.DAYS:
                        self.error(f"Jour invalide: {day} (valeurs: {', '.join(self.DAYS.keys())})")
                        return False

            # RÃ©cupÃ©rer le serial de l'appareil
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            days_text = f" ({', '.join(days)})" if days else " (tous les jours)"
            self.info(f"ðŸ“… Programmation DND sur '{args.device}': {args.start}-{args.end}{days_text}...")

            ctx = self.require_context()
            if not ctx.dnd_mgr:
                self.error("DNDManager non disponible")
                return False

            result = self.call_with_breaker(ctx.dnd_mgr.set_dnd_schedule, serial, args.start, args.end, days)

            if result:
                self.success(f"âœ… Programmation DND configurÃ©e sur '{args.device}'")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la programmation DND")
            self.error(f"Erreur: {e}")
            return False

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _validate_time(self, time_str: str) -> bool:
        """
        Valide un format d'heure HH:MM.

        Args:
            time_str: ChaÃ®ne au format HH:MM

        Returns:
            True si valide, False sinon
        """
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False

            hour = int(parts[0])
            minute = int(parts[1])

            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False

    def _display_status(self, device_name: str, status: dict) -> None:
        """Affiche le statut DND."""
        print(f"\nðŸ”• Statut DND de '{device_name}':\n")

        enabled = status.get("enabled", False)
        status_icon = "ðŸ”•" if enabled else "ðŸ””"
        status_text = "ActivÃ©" if enabled else "DÃ©sactivÃ©"

        print(f"  {status_icon} Ã‰tat: {status_text}")

        # Afficher la programmation si elle existe
        if "schedule" in status and status["schedule"]:
            schedule = status["schedule"]
            start = schedule.get("start", "N/A")
            end = schedule.get("end", "N/A")
            days = schedule.get("days", [])

            print("\n  ðŸ“… Programmation:")
            print(f"     Horaires: {start} - {end}")

            if days:
                days_text = ", ".join([self.DAYS.get(d, d) for d in days])
                print(f"     Jours: {days_text}")
            else:
                print("     Jours: Tous les jours")
        else:
            print("\n  ðŸ“… Aucune programmation configurÃ©e")

    def _get_device_type(self, device_name: str) -> str:
        """RÃ©cupÃ¨re le type d'appareil (placeholder)."""
        # TODO: RÃ©cupÃ©rer depuis device_mgr
        return "ECHO_DEVICE"

