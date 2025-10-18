﻿"""
Commandes de gestion du calendrier Alexa.

Ce module g�re toutes les op�rations li�es aux �v�nements du calendrier:
- list: Lister les �v�nements � venir
- add: Ajouter un nouvel �v�nement
- delete: Supprimer un �v�nement
- info: Afficher les d�tails d'un �v�nement

Auteur: M@nu
Date: 12 octobre 2025
"""

import argparse
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils.cli.base_command import BaseCommand
from utils.cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter

# Constantes de description simplifi�es
CALENDAR_DESCRIPTION = "G�rer le calendrier Alexa"
ADD_HELP = "Ajouter un nouvel �v�nement"
DELETE_HELP = "Supprimer un �v�nement"
INFO_HELP = "Afficher les d�tails d'un �v�nement"
LIST_HELP = "Lister les �v�nements � venir"


class CalendarCommand(BaseCommand):
    """
    Commande de gestion du calendrier Alexa.

    G�re list, add, delete et info pour les �v�nements du calendrier.

    Actions:
        - list: Lister les �v�nements � venir
        - add: Ajouter un nouvel �v�nement
        - delete: Supprimer un �v�nement
        - info: Afficher les d�tails d'un �v�nement

    Example:
        >>> python alexa calendar list
        >>> python alexa calendar add --title "R�union" --start "2025-10-15 14:00"
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes calendar.

        Args:
            parser: Sous-parser pour la cat�gorie 'calendar'
        """
        parser.formatter_class = UniversalHelpFormatter
        parser.usage = argparse.SUPPRESS
        parser.description = CALENDAR_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action � ex�cuter",
            required=True,
        )

        # Action: test (test Privacy API endpoints)
        test_parser = subparsers.add_parser(
            "test",
            help="Tester les endpoints Privacy API pour le calendrier",
            add_help=False,
        )
        test_parser.add_argument(
            "--network",
            action="store_true",
            help="Scanner �galement le r�seau local pour trouver les API locales",
        )

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Consulter les �v�nements (commande vocale)",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        list_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=False,
            metavar="DEVICE",
            help="Appareil sur lequel ex�cuter la commande",
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
            help="Ajouter un �v�nement au calendrier",
            description=ADD_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        add_parser.add_argument(
            "--title",
            type=str,
            required=True,
            metavar="TEXT",
            help="Titre de l'�v�nement",
        )
        add_parser.add_argument(
            "--start",
            type=str,
            required=True,
            metavar="DATETIME",
            help="Date/heure de d�but (format: YYYY-MM-DD HH:MM)",
        )
        add_parser.add_argument(
            "--end",
            type=str,
            metavar="DATETIME",
            help="Date/heure de fin (d�faut: +1h)",
        )
        add_parser.add_argument(
            "--location",
            type=str,
            metavar="TEXT",
            help="Lieu de l'�v�nement",
        )
        add_parser.add_argument(
            "--description",
            type=str,
            metavar="TEXT",
            help="Description de l'�v�nement",
        )

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Supprimer un �v�nement",
            description=DELETE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        delete_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="EVENT_ID",
            help="ID de l'�v�nement � supprimer",
        )

        # Action: info
        info_parser = subparsers.add_parser(
            "info",
            help="Afficher les d�tails d'un �v�nement",
            description=INFO_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        info_parser.add_argument(
            "--id",
            type=str,
            required=True,
            metavar="EVENT_ID",
            help="ID de l'�v�nement",
        )
        info_parser.add_argument(
            "--json",
            dest="json_output",
            action="store_true",
            help="Afficher au format JSON",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Ex�cute la commande calendar selon l'action.

        Args:
            args: Arguments pars�s

        Returns:
            True si succ�s, False sinon
        """
        ctx = self.require_context()
        # V�rifier l'authentification
        if not ctx.auth:
            self.error("Authentification requise. Ex�cutez 'alexa auth create' d'abord.")
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
            True si succ�s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            self.info("?? Test des endpoints Privacy API pour le calendrier...")

            results = self.call_with_breaker(ctx.calendar_manager.test_privacy_api_endpoints)

            if not results:
                self.error("Aucun r�sultat")
                return False

            # Afficher les r�sultats
            self.info("\n?? R�sultats des tests Cloud API:")
            for endpoint, data in results.items():
                if "error" in data:
                    self.error(f"  ? {endpoint}: {data['error']}")
                else:
                    status = data.get("status", "?")
                    size = data.get("size", 0)

                    if status == 200:
                        self.success(f"  ? {endpoint}: {status} ({size} bytes)")
                    elif status == 404:
                        self.warning(f"  ?? {endpoint}: {status} (Not Found)")
                    elif status == 403:
                        self.warning(f"  ?? {endpoint}: {status} (Forbidden - Token manquant)")
                    else:
                        self.warning(f"  ?? {endpoint}: {status}")

            # Test r�seau local si demand�
            if hasattr(args, "network") and args.network:
                self.info("\n?? Scan du r�seau local...")
                self._test_local_network()

            return True

        except Exception as e:
            self.logger.exception("Erreur lors du test Privacy API")
            self.error(f"Erreur: {e}")
            return False

    def _test_local_network(self) -> None:
        """Teste la d�couverte r�seau locale des appareils Alexa."""
        try:
            from utils.network_discovery import AlexaNetworkDiscovery

            discovery = AlexaNetworkDiscovery()

            # D�couverte UPnP/SSDP
            self.info("  ?? D�couverte UPnP/SSDP...")
            devices = discovery.discover_upnp(timeout=5)

            if devices:
                self.success(f"  ? {len(devices)} appareil(s) d�couvert(s):")
                for device in devices:
                    ip = device.get("ip", "?")
                    server = device.get("server", "Unknown")
                    self.info(f"    ?? {ip} - {server}")

                    # Scanner les ports du premier appareil
                    if device == devices[0]:
                        self.info(f"\n  ?? Scan des ports sur {ip}...")
                        open_ports = discovery.scan_device_ports(ip)
                        ports_ouverts = [p for p, o in open_ports.items() if o]

                        if ports_ouverts:
                            self.success(f"    ? Ports ouverts: {ports_ouverts}")

                            # Tester l'API locale sur les ports HTTP
                            for port in [80, 8080, 443, 8443]:
                                if port in ports_ouverts:
                                    self.info(f"\n  ?? Test API locale sur {ip}:{port}...")
                                    api_results = discovery.test_local_api(ip, port)

                                    for endpoint, data in api_results.items():
                                        if "error" not in data and data.get("status") == 200:
                                            self.success(f"    ? {endpoint}: {data['status']}")
                                        elif "error" not in data:
                                            self.warning(f"    ?? {endpoint}: {data.get('status', '?')}")
                        else:
                            self.warning("    ?? Aucun port HTTP/HTTPS ouvert")
            else:
                self.warning("  ?? Aucun appareil Alexa d�couvert via UPnP")

        except ImportError:
            self.error("  ? Module network_discovery non disponible")
        except Exception as e:
            self.logger.exception("Erreur scan r�seau local")
            self.error(f"  ? Erreur: {e}")

    def _list_events(self, args: argparse.Namespace) -> bool:
        """
        Liste les �v�nements du calendrier via TextCommand.

        Args:
            args: Arguments (days, device)

        Returns:
            True si succ�s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            # D�terminer la p�riode
            if args.days == 1:
                timeframe = "aujourd'hui"
            elif args.days == 2:
                timeframe = "demain"
            elif args.days <= 7:
                timeframe = "cette semaine"
            else:
                timeframe = "ce mois"

            self.info(f"?? Consultation des �v�nements {timeframe}...")

            # Appel via TextCommand
            result = self.call_with_breaker(
                ctx.calendar_manager.query_events,
                timeframe=timeframe,
                device_name=args.device,
            )

            if result:
                self.success(f"? {result}")
                self.info("?? Alexa �nonce vocalement vos �v�nements sur l'appareil")
                return True
            else:
                self.error("Impossible de consulter les �v�nements")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la consultation calendrier")
            self.error(f"Erreur: {e}")
            return False

    def _display_events_table(self, events: List[Dict[str, Any]]) -> None:
        """
        Affiche les �v�nements sous forme de tableau.

        Args:
            events: Liste des �v�nements
        """
        self.success(f"? {len(events)} �v�nement(s) trouv�(s):\n")

        # Pr�parer les donn�es
        table_data = []
        for event in events:
            event_id = event.get("id", "N/A")[:12] + "..."
            title = event.get("title", "Sans titre")

            # Format de la date
            start_ms = event.get("startTime", 0)
            start_dt = datetime.fromtimestamp(start_ms / 1000) if start_ms else None
            start_str = start_dt.strftime("%d/%m/%Y %H:%M") if start_dt else "N/A"

            location = event.get("location", "-")
            status = "?? Actif" if event.get("status") == "active" else "? Inactif"

            table_data.append([event_id, title[:30], start_str, location[:20], status])

        # Afficher le tableau
        table = self.format_table(table_data, ["ID", "Titre", "D�but", "Lieu", "Statut"])
        print(table)

    def _add_event(self, args: argparse.Namespace) -> bool:
        """
        Ajoute un �v�nement au calendrier.

        Args:
            args: Arguments (title, start, end, location, description)

        Returns:
            True si succ�s
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
                self.info("Formats accept�s: YYYY-MM-DD HH:MM ou DD/MM/YYYY HH:MM")
                return False

            end_time = None
            if args.end:
                end_time = self._parse_datetime(args.end)
                if not end_time:
                    self.error(f"Format de date invalide: {args.end}")
                    return False

            self.info(f"? Ajout de l'�v�nement '{args.title}'...")

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
                self.success(f"? �v�nement '{args.title}' cr�� avec succ�s!")
                self.info(f"ID: {event.get('id', 'N/A')}")
                return True
            else:
                self.error("�chec de la cr�ation de l'�v�nement")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'ajout de l'�v�nement")
            self.error(f"Erreur: {e}")
            return False

    def _delete_event(self, args: argparse.Namespace) -> bool:
        """
        Supprime un �v�nement du calendrier.

        Args:
            args: Arguments (id)

        Returns:
            True si succ�s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            self.info(f"??? Suppression de l'�v�nement {args.id}...")

            success = self.call_with_breaker(ctx.calendar_manager.delete_event, event_id=args.id)

            if success:
                self.success("? �v�nement supprim� avec succ�s!")
                return True
            else:
                self.error("�chec de la suppression")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression de l'�v�nement")
            self.error(f"Erreur: {e}")
            return False

    def _event_info(self, args: argparse.Namespace) -> bool:
        """
        Affiche les d�tails d'un �v�nement.

        Args:
            args: Arguments (id, json_output)

        Returns:
            True si succ�s
        """
        try:
            ctx = self.require_context()
            if not ctx.calendar_manager:
                self.error("CalendarManager non disponible")
                return False

            self.info(f"?? R�cup�ration de l'�v�nement {args.id}...")

            event = self.call_with_breaker(ctx.calendar_manager.get_event_details, event_id=args.id)

            if not event:
                self.error("�v�nement non trouv�")
                return False

            # Affichage
            if hasattr(args, "json_output") and args.json_output:
                print(json.dumps(event, indent=2, ensure_ascii=False))
            else:
                self._display_event_details(event)

            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la r�cup�ration des d�tails")
            self.error(f"Erreur: {e}")
            return False

    def _display_event_details(self, event: Dict[str, Any]) -> None:
        """
        Affiche les d�tails d'un �v�nement de mani�re format�e.

        Args:
            event: Donn�es de l'�v�nement
        """
        self.success("?? D�tails de l'�v�nement:\n")

        print(f"  ID:          {event.get('id', 'N/A')}")
        print(f"  Titre:       {event.get('title', 'Sans titre')}")

        # Dates
        start_ms = event.get("startTime", 0)
        start_dt = datetime.fromtimestamp(start_ms / 1000) if start_ms else None
        print(f"  D�but:       {start_dt.strftime('%d/%m/%Y %H:%M') if start_dt else 'N/A'}")

        end_ms = event.get("endTime", 0)
        end_dt = datetime.fromtimestamp(end_ms / 1000) if end_ms else None
        print(f"  Fin:         {end_dt.strftime('%d/%m/%Y %H:%M') if end_dt else 'N/A'}")

        # Autres infos
        print(f"  Lieu:        {event.get('location', '-')}")
        print(f"  Description: {event.get('description', '-')}")
        print(f"  Statut:      {event.get('status', 'N/A')}")

    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """
        Parse une cha�ne de date/heure.

        Args:
            date_str: Cha�ne au format YYYY-MM-DD HH:MM ou DD/MM/YYYY HH:MM

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




