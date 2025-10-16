"""
Commandes de gestion des annonces Alexa.

Ce module gÃ¨re toutes les opÃ©rations liÃ©es aux annonces:
- send: Envoyer une annonce
- list: Lister les annonces
- clear: Supprimer les annonces
- read: Marquer comme lu

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import json
from typing import Any, Dict, List

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter


class AnnouncementCommand(BaseCommand):
    """
    Commande de gestion des annonces Alexa.

    GÃ¨re send, list, clear, read.

    Actions:
        - send: Envoyer une annonce Ã  un appareil
        - list: Lister toutes les annonces
        - clear: Supprimer les annonces
        - read: Marquer une annonce comme lue

    Example:
        >>> alexa announcement send -d "Salon" --message "Rappel: RÃ©union Ã  15h"
        >>> alexa announcement send -d "Salon" --message "Alerte" --title "Important"
        >>> alexa announcement list
        >>> alexa announcement clear --device "Salon"
        >>> alexa announcement read --id NOTIF_ID
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes announcement.

        Args:
            parser: Sous-parser pour la catÃ©gorie 'announcement'
        """
        # Utiliser le formatter universel pour l'ordre exact demandÃ©
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description simplifiÃ©e
        parser.description = "GÃ©rer les annonces audio sur les appareils Alexa"

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: send
        send_parser = subparsers.add_parser(
            "send",
            help="Envoyer une annonce",
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        send_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil cible",
        )
        send_parser.add_argument("--message", type=str, required=True, metavar="TEXT", help="Message de l'annonce")
        send_parser.add_argument("--title", type=str, metavar="TITLE", help="Titre de l'annonce (optionnel)")

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Lister les annonces",
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        list_parser.add_argument(
            "--limit",
            type=int,
            metavar="N",
            default=50,
            help="Nombre maximum d'annonces (dÃ©faut: 50)",
        )
        list_parser.add_argument("--device", type=str, metavar="DEVICE_NAME", help="Filtrer par appareil")

        # Action: clear
        clear_parser = subparsers.add_parser(
            "clear",
            help="Supprimer annonces",
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        clear_parser.add_argument("--device", type=str, required=True, metavar="DEVICE_NAME", help="Nom de l'appareil")
        clear_parser.add_argument("--all", action="store_true", help="Supprimer toutes les annonces")

        # Action: read
        read_parser = subparsers.add_parser(
            "read",
            help="Marquer comme lu",
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        read_parser.add_argument("--id", type=str, required=True, metavar="ANNOUNCEMENT_ID", help="ID de l'annonce")

    def execute(self, args: argparse.Namespace) -> bool:
        """
        ExÃ©cute la commande announcement.

        Args:
            args: Arguments parsÃ©s

        Returns:
            True si succÃ¨s, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "send":
            return self._send_announcement(args)
        elif args.action == "list":
            return self._list_announcements(args)
        elif args.action == "clear":
            return self._clear_announcements(args)
        elif args.action == "read":
            return self._mark_as_read(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _send_announcement(self, args: argparse.Namespace) -> bool:
        """Envoyer une annonce."""
        try:
            # RÃ©cupÃ©rer le serial de l'appareil
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            title = getattr(args, "title", None) or "Annonce"

            self.info(f"ï¿½ Envoi annonce Ã  '{args.device}'...")

            ctx = self.require_context()
            if not ctx.notification_mgr:
                self.error("Gestionnaire d'annonces non disponible")
                return False

            result = self.call_with_breaker(ctx.notification_mgr.send_notification, serial, args.message, title)

            if result:
                self.success(f"âœ… Annonce envoyÃ©e Ã  '{args.device}'")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'envoi d'annonce")
            self.error(f"Erreur: {e}")
            return False

    def _list_announcements(self, args: argparse.Namespace) -> bool:
        """Lister les annonces."""
        try:
            self.info("ï¿½ RÃ©cupÃ©ration des annonces...")

            ctx = self.require_context()
            if not ctx.notification_mgr:
                self.error("Gestionnaire d'annonces non disponible")
                return False

            # RÃ©cupÃ©rer toutes les annonces
            announcements = self.call_with_breaker(ctx.notification_mgr.list_notifications, args.limit)

            # Filtrer par appareil si spÃ©cifiÃ©
            if hasattr(args, "device") and args.device:
                device_serial = self.get_device_serial(args.device)
                if device_serial and announcements:
                    announcements = [n for n in announcements if n.get("deviceSerialNumber") == device_serial]

            if announcements:
                if hasattr(args, "json_output") and args.json_output:
                    print(json.dumps(announcements, indent=2, ensure_ascii=False))
                else:
                    self._display_announcements(announcements)

                return True

            self.warning("Aucune annonce trouvÃ©e")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration des annonces")
            self.error(f"Erreur: {e}")
            return False

    def _clear_announcements(self, args: argparse.Namespace) -> bool:
        """Supprimer les annonces."""
        try:
            # RÃ©cupÃ©rer le serial de l'appareil
            serial = self.get_device_serial(args.device)
            if not serial:
                return False

            self.info(f"ðŸ—‘ï¸  Suppression annonces de '{args.device}'...")

            ctx = self.require_context()
            if not ctx.notification_mgr:
                self.error("Gestionnaire d'annonces non disponible")
                return False

            result = self.call_with_breaker(ctx.notification_mgr.clear_notifications, serial)

            if result:
                self.success(f"âœ… Annonces supprimÃ©es de '{args.device}'")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression des annonces")
            self.error(f"Erreur: {e}")
            return False

    def _mark_as_read(self, args: argparse.Namespace) -> bool:
        """Marquer comme lu."""
        try:
            self.info(f"âœ“ Marquage annonce '{args.id}' comme lue...")

            ctx = self.require_context()
            if not ctx.notification_mgr:
                self.error("Gestionnaire d'annonces non disponible")
                return False

            result = self.call_with_breaker(ctx.notification_mgr.mark_as_read, args.id)

            if result:
                self.success("âœ… Annonce marquÃ©e comme lue")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors du marquage d'annonce")
            self.error(f"Erreur: {e}")
            return False

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _display_announcements(self, announcements: List[Dict[str, Any]]) -> None:
        """Affiche les annonces."""
        print(f"\nï¿½ {len(announcements)} annonce(s):\n")

        for announce in announcements:
            announce_id = announce.get("id", "N/A")
            title = announce.get("title", "Sans titre")
            message = announce.get("message", "")
            device = announce.get("device_name", "Unknown")
            timestamp = announce.get("timestamp", "N/A")
            read = announce.get("read", False)

            read_icon = "âœ“" if read else "â—"

            print(f"  {read_icon} {title}")
            print(f"     ID: {announce_id}")
            print(f"     Appareil: {device}")
            print(f"     Message: {message}")
            print(f"     Date: {timestamp}")
            print()

