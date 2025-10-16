"""
Commandes de gestion du calendrier Alexa.

Ce module gÃ¨re toutes les opÃ©rations liÃ©es aux Ã©vÃ©nements du calendrier:
- list: Lister les Ã©vÃ©nements Ã  venir
- add: Ajouter un nouvel Ã©vÃ©nement
- delete: Supprimer un Ã©vÃ©nement
- info: Afficher les dÃ©tails d'un Ã©vÃ©nement

Auteur: M@nu
Date: 12 octobre 2025
"""

import argparse
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter

# Constantes de description simplifiÃ©es
CALENDAR_DESCRIPTION = "GÃ©rer le calendrier Alexa"
ADD_HELP = "Ajouter un nouvel Ã©vÃ©nement"
DELETE_HELP = "Supprimer un Ã©vÃ©nement"
INFO_HELP = "Afficher les dÃ©tails d'un Ã©vÃ©nement"
LIST_HELP = "Lister les Ã©vÃ©nements Ã  venir"


class CalendarCommand(BaseCommand):
    """
    Commande de gestion du calendrier Alexa.

    GÃ¨re list, add, delete et info pour les Ã©vÃ©nements du calendrier.

    Actions:
        - list: Lister les Ã©vÃ©nements Ã  venir
        - add: Ajouter un nouvel Ã©vÃ©nement
        - delete: Supprimer un Ã©vÃ©nement
        - info: Afficher les dÃ©tails d'un Ã©vÃ©nement

    Example:
        >>> python alexa calendar list
        >>> python alexa calendar add --title "RÃ©union" --start "2025-10-15 14:00"
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes calendar.

        Args:
            parser: Sous-parser pour la catÃ©gorie 'calendar'
        """
        parser.formatter_class = UniversalHelpFormatter
        parser.usage = argparse.SUPPRESS
        parser.description = CALENDAR_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: test (test Privacy API endpoints)
        test_parser = subparsers.add_parser(
            "test",
            help="Tester les endpoints Privacy API pour le calendrier",
            add_help=True,
        )
        test_parser.add_argument(
            "--network",
            action="store_true",
            help="Scanner Ã©galement le rÃ©seau local pour trouver les API locales",
        )

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Consulter les Ã©vÃ©nements (commande vocale)",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=False,
            metavar="DEVICE",
            help="Appareil sur lequel exÃ©cuter la commande",
        )
        list_parser.add_argument(
            "--days",
            type=int,
            default=1,
            metavar="N",
            help="Nombre de jours (1=aujourd'hui, 2=demain, 7=semaine)",
        )

        # Action: add
        add_parser = subparsers.add_parser(
            "add",
            help="Ajouter un Ã©vÃ©nement au calendrier",
            description=ADD_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        add_parser.add_argument(
            "--title",
            type=str,
            required=True,
            metavar="TEXT",
            help="Titre de l'Ã©vÃ©nement",
        )
        add_parser.add_argument(
            "--start",
            type=str,
            required=True,
            metavar="DATETIME",
            help="Date/heure de dÃ©but (format: YYYY-MM-DD HH:MM)",
        )
        add_parser.add_argument(
            "--end",
            type=str,
            metavar="DATETIME",
            help="Date/heure de fin (dÃ©faut: +1h)",
        )
        add_parser.add_argument(
            "--location",
            type=str,
            metavar="TEXT",
            help="Lieu de l'Ã©vÃ©nement",
        )
        add_parser.add_argument(
            "--description",
            type=str,
            metavar="TEXT",
            help="Description de l'Ã©vÃ©nement",
        )

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Supprimer un Ã©vÃ©nement",
            description=DELETE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        delete_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="EVENT_ID",
            help="ID de l'Ã©vÃ©nement Ã  supprimer",
        )

        # Action: info
        info_parser = subparsers.add_parser(
            "info",
            help="Afficher les dÃ©tails d'un Ã©vÃ©nement",
            description=INFO_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        info_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="EVENT_ID",
            help="ID de l'Ã©vÃ©nement",
        )
        info_parser.add_argument(
            "--json",
            dest="json_output",
            action="store_true",
            help="Afficher au format JSON",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        ExÃ©cute la commande calendar selon l'action.

        Args:
            args: Arguments parsÃ©s

        Returns:
            True si succÃ¨s, False sinon
        """
        ctx = self.require_context()
        # VÃ©rifier l'authentification
        if not ctx.auth:
            self.error("Authentification requise. ExÃ©cutez 'alexa auth create' d'abord.")
            return False

        # Router vers la bonne action
        if args.action == "test":
            return self._test_privacy_api(args)
        elif args.action == "list":
            return self._list_events(args)
        elif args.action == "add":
            return self._add_event(args)
        elif args.action == "delete":
            return self._delete_event(args)
        elif args.action == "info":
            return self._event_info(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _test_privacy_api(self, args: argparse.Namespace) -> bool:
        """
        Teste les endpoints Privacy API pour trouver l'API calendrier.

        Args:
            args: Arguments

        Returns:
            True si succÃ¨s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            self.info("ðŸ” Test des endpoints Privacy API pour le calendrier...")

            results = self.call_with_breaker(ctx.calendar_manager.test_privacy_api_endpoints)

            if not results:
                self.error("Aucun rÃ©sultat")
                return False

            # Afficher les rÃ©sultats
            self.info("\nðŸ“Š RÃ©sultats des tests Cloud API:")
            for endpoint, data in results.items():
                if "error" in data:
                    self.error(f"  âŒ {endpoint}: {data['error']}")
                else:
                    status = data.get("status", "?")
                    size = data.get("size", 0)

                    if status == 200:
                        self.success(f"  âœ… {endpoint}: {status} ({size} bytes)")
                    elif status == 404:
                        self.warning(f"  âš ï¸ {endpoint}: {status} (Not Found)")
                    elif status == 403:
                        self.warning(f"  âš ï¸ {endpoint}: {status} (Forbidden - Token manquant)")
                    else:
                        self.warning(f"  âš ï¸ {endpoint}: {status}")

            # Test rÃ©seau local si demandÃ©
            if hasattr(args, "network") and args.network:
                self.info("\nðŸŒ Scan du rÃ©seau local...")
                self._test_local_network()

            return True

        except Exception as e:
            self.logger.exception("Erreur lors du test Privacy API")
            self.error(f"Erreur: {e}")
            return False

    def _test_local_network(self) -> None:
        """Teste la dÃ©couverte rÃ©seau locale des appareils Alexa."""
        try:
            from utils.network_discovery import AlexaNetworkDiscovery

            discovery = AlexaNetworkDiscovery()

            # DÃ©couverte UPnP/SSDP
            self.info("  ðŸ” DÃ©couverte UPnP/SSDP...")
            devices = discovery.discover_upnp(timeout=5)

            if devices:
                self.success(f"  âœ… {len(devices)} appareil(s) dÃ©couvert(s):")
                for device in devices:
                    ip = device.get("ip", "?")
                    server = device.get("server", "Unknown")
                    self.info(f"    ðŸ“± {ip} - {server}")

                    # Scanner les ports du premier appareil
                    if device == devices[0]:
                        self.info(f"\n  ðŸ” Scan des ports sur {ip}...")
                        open_ports = discovery.scan_device_ports(ip)
                        ports_ouverts = [p for p, o in open_ports.items() if o]

                        if ports_ouverts:
                            self.success(f"    âœ… Ports ouverts: {ports_ouverts}")

                            # Tester l'API locale sur les ports HTTP
                            for port in [80, 8080, 443, 8443]:
                                if port in ports_ouverts:
                                    self.info(f"\n  ðŸ” Test API locale sur {ip}:{port}...")
                                    api_results = discovery.test_local_api(ip, port)

                                    for endpoint, data in api_results.items():
                                        if "error" not in data and data.get("status") == 200:
                                            self.success(f"    âœ… {endpoint}: {data['status']}")
                                        elif "error" not in data:
                                            self.warning(f"    âš ï¸ {endpoint}: {data.get('status', '?')}")
                        else:
                            self.warning("    âš ï¸ Aucun port HTTP/HTTPS ouvert")
            else:
                self.warning("  âš ï¸ Aucun appareil Alexa dÃ©couvert via UPnP")

        except ImportError:
            self.error("  âŒ Module network_discovery non disponible")
        except Exception as e:
            self.logger.exception("Erreur scan rÃ©seau local")
            self.error(f"  âŒ Erreur: {e}")

    def _list_events(self, args: argparse.Namespace) -> bool:
        """
        Liste les Ã©vÃ©nements du calendrier via TextCommand.

        Args:
            args: Arguments (days, device)

        Returns:
            True si succÃ¨s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            # DÃ©terminer la pÃ©riode
            if args.days == 1:
                timeframe = "aujourd'hui"
            elif args.days == 2:
                timeframe = "demain"
            elif args.days <= 7:
                timeframe = "cette semaine"
            else:
                timeframe = "ce mois"

            self.info(f"ðŸ“… Consultation des Ã©vÃ©nements {timeframe}...")

            # Appel via TextCommand
            result = self.call_with_breaker(
                ctx.calendar_manager.query_events,
                timeframe=timeframe,
                device_name=args.device,
            )

            if result:
                self.success(f"âœ… {result}")
                self.info("ðŸ’¡ Alexa Ã©nonce vocalement vos Ã©vÃ©nements sur l'appareil")
                return True
            else:
                self.error("Impossible de consulter les Ã©vÃ©nements")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la consultation calendrier")
            self.error(f"Erreur: {e}")
            return False

    def _display_events_table(self, events: List[Dict[str, Any]]) -> None:
        """
        Affiche les Ã©vÃ©nements sous forme de tableau.

        Args:
            events: Liste des Ã©vÃ©nements
        """
        self.success(f"âœ… {len(events)} Ã©vÃ©nement(s) trouvÃ©(s):\n")

        # PrÃ©parer les donnÃ©es
        table_data = []
        for event in events:
            event_id = event.get("id", "N/A")[:12] + "..."
            title = event.get("title", "Sans titre")

            # Format de la date
            start_ms = event.get("startTime", 0)
            start_dt = datetime.fromtimestamp(start_ms / 1000) if start_ms else None
            start_str = start_dt.strftime("%d/%m/%Y %H:%M") if start_dt else "N/A"

            location = event.get("location", "-")
            status = "ðŸŸ¢ Actif" if event.get("status") == "active" else "âšª Inactif"

            table_data.append([event_id, title[:30], start_str, location[:20], status])

        # Afficher le tableau
        table = self.format_table(table_data, ["ID", "Titre", "DÃ©but", "Lieu", "Statut"])
        print(table)

    def _add_event(self, args: argparse.Namespace) -> bool:
        """
        Ajoute un Ã©vÃ©nement au calendrier.

        Args:
            args: Arguments (title, start, end, location, description)

        Returns:
            True si succÃ¨s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            # Parser les dates
            start_time = self._parse_datetime(args.start)
            if not start_time:
                self.error(f"Format de date invalide: {args.start}")
                self.info("Formats acceptÃ©s: YYYY-MM-DD HH:MM ou DD/MM/YYYY HH:MM")
                return False

            end_time = None
            if args.end:
                end_time = self._parse_datetime(args.end)
                if not end_time:
                    self.error(f"Format de date invalide: {args.end}")
                    return False

            self.info(f"âž• Ajout de l'Ã©vÃ©nement '{args.title}'...")

            # Appel API
            event = self.call_with_breaker(
                ctx.calendar_manager.add_event,
                title=args.title,
                start_time=start_time,
                end_time=end_time,
                location=args.location,
                description=args.description,
            )

            if event:
                self.success(f"âœ… Ã‰vÃ©nement '{args.title}' crÃ©Ã© avec succÃ¨s!")
                self.info(f"ID: {event.get('id', 'N/A')}")
                return True
            else:
                self.error("Ã‰chec de la crÃ©ation de l'Ã©vÃ©nement")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'ajout de l'Ã©vÃ©nement")
            self.error(f"Erreur: {e}")
            return False

    def _delete_event(self, args: argparse.Namespace) -> bool:
        """
        Supprime un Ã©vÃ©nement du calendrier.

        Args:
            args: Arguments (id)

        Returns:
            True si succÃ¨s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            self.info(f"ðŸ—‘ï¸ Suppression de l'Ã©vÃ©nement {args.id}...")

            success = self.call_with_breaker(ctx.calendar_manager.delete_event, event_id=args.id)

            if success:
                self.success("âœ… Ã‰vÃ©nement supprimÃ© avec succÃ¨s!")
                return True
            else:
                self.error("Ã‰chec de la suppression")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression de l'Ã©vÃ©nement")
            self.error(f"Erreur: {e}")
            return False

    def _event_info(self, args: argparse.Namespace) -> bool:
        """
        Affiche les dÃ©tails d'un Ã©vÃ©nement.

        Args:
            args: Arguments (id, json_output)

        Returns:
            True si succÃ¨s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            self.info(f"â„¹ï¸ RÃ©cupÃ©ration de l'Ã©vÃ©nement {args.id}...")

            event = self.call_with_breaker(ctx.calendar_manager.get_event_details, event_id=args.id)

            if not event:
                self.error("Ã‰vÃ©nement non trouvÃ©")
                return False

            # Affichage
            if hasattr(args, "json_output") and args.json_output:
                print(json.dumps(event, indent=2, ensure_ascii=False))
            else:
                self._display_event_details(event)

            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration des dÃ©tails")
            self.error(f"Erreur: {e}")
            return False

    def _display_event_details(self, event: Dict[str, Any]) -> None:
        """
        Affiche les dÃ©tails d'un Ã©vÃ©nement de maniÃ¨re formatÃ©e.

        Args:
            event: DonnÃ©es de l'Ã©vÃ©nement
        """
        self.success("â„¹ï¸ DÃ©tails de l'Ã©vÃ©nement:\n")

        print(f"  ID:          {event.get('id', 'N/A')}")
        print(f"  Titre:       {event.get('title', 'Sans titre')}")

        # Dates
        start_ms = event.get("startTime", 0)
        start_dt = datetime.fromtimestamp(start_ms / 1000) if start_ms else None
        print(f"  DÃ©but:       {start_dt.strftime('%d/%m/%Y %H:%M') if start_dt else 'N/A'}")

        end_ms = event.get("endTime", 0)
        end_dt = datetime.fromtimestamp(end_ms / 1000) if end_ms else None
        print(f"  Fin:         {end_dt.strftime('%d/%m/%Y %H:%M') if end_dt else 'N/A'}")

        # Autres infos
        print(f"  Lieu:        {event.get('location', '-')}")
        print(f"  Description: {event.get('description', '-')}")
        print(f"  Statut:      {event.get('status', 'N/A')}")

    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """
        Parse une chaÃ®ne de date/heure.

        Args:
            date_str: ChaÃ®ne au format YYYY-MM-DD HH:MM ou DD/MM/YYYY HH:MM

        Returns:
            Objet datetime ou None si invalide
        """
        formats = [
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

