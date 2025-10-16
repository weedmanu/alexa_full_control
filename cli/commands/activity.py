"""Commande de consultation de l'historique d'activitÃ© Alexa.

Ce module fournit une interface CLI pour consulter l'historique :
- Voir les activitÃ©s rÃ©centes
- Filtrer par appareil
- Filtrer par type d'activitÃ©
- Afficher les dÃ©tails d'une activitÃ©
"""

import argparse

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter

# Constantes de description simplifiÃ©es
ACTIVITY_DESCRIPTION = "Consulter l'historique d'activitÃ© Alexa"
LIST_HELP = "Lister les activitÃ©s rÃ©centes"


class ActivityCommand(BaseCommand):
    """
    Commande pour consulter l'historique d'activitÃ© Alexa.

    L'historique permet de voir toutes les interactions vocales,
    commandes exÃ©cutÃ©es et Ã©vÃ©nements survenus sur vos appareils.

    Exemples:
        >>> # Voir les activitÃ©s rÃ©centes
        >>> alexa activity list

        >>> # Filtrer par appareil
        >>> alexa activity list -d "Salon Echo"

        >>> # Filtrer par type
        >>> alexa activity list --type voice

        >>> # Limiter le nombre de rÃ©sultats
        >>> alexa activity list --limit 20

        >>> # Voir les dÃ©tails d'une activitÃ©
        >>> alexa activity info --id "abc123"
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "activity"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "Consulter l'historique d'activitÃ©"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande activity.

        Args:
            parser: Parser Ã  configurer
        """
        # Utiliser le formatter universel pour l'ordre exact demandÃ©
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description centralisÃ©e
        parser.description = ACTIVITY_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action Ã  exÃ©cuter",
            required=True,
        )

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Lister activitÃ©s",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        list_parser.add_argument(
            "--type",
            type=str,
            choices=["voice", "music", "alarm", "timer", "reminder", "smart_home", "all"],
            default="all",
            help="Type d'activitÃ© Ã  filtrer",
        )
        list_parser.add_argument(
            "--limit",
            type=int,
            default=10,
            metavar="N",
            help="Nombre maximum d'activitÃ©s Ã  afficher (dÃ©faut: 10)",
        )

        # Action: lastdevice
        subparsers.add_parser(
            "lastdevice",
            help="Dernier appareil utilisÃ©",
            description="Affiche le nom du dernier appareil qui a eu une interaction avec Alexa",
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )

        # Action: lastcommand
        lastcommand_parser = subparsers.add_parser(
            "lastcommand",
            help="DerniÃ¨re commande vocale",
            description="Affiche la derniÃ¨re commande vocale prononcÃ©e",
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        lastcommand_parser.add_argument(
            "-d",
            "--device",
            metavar="DEVICE_NAME",
            help="Filtrer par nom d'appareil (optionnel)",
        )

        # Action: lastresponse
        lastresponse_parser = subparsers.add_parser(
            "lastresponse",
            help="DerniÃ¨re rÃ©ponse d'Alexa",
            description="Affiche la derniÃ¨re rÃ©ponse vocale d'Alexa",
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        lastresponse_parser.add_argument(
            "-d",
            "--device",
            metavar="DEVICE_NAME",
            help="Filtrer par nom d'appareil (optionnel)",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        ExÃ©cute la commande activity.

        Args:
            args: Arguments parsÃ©s

        Returns:
            True si succÃ¨s, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "list":
            return self._list_activities(args)
        elif args.action == "info":
            return self._show_activity_info(args)
        elif args.action == "lastdevice":
            return self._show_last_device(args)
        elif args.action == "lastcommand":
            return self._show_last_command(args)
        elif args.action == "lastresponse":
            return self._show_last_response(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _list_activities(self, args: argparse.Namespace) -> bool:
        """Lister les activitÃ©s."""
        try:
            device_name = getattr(args, "device", None)
            activity_type = getattr(args, "type", "all")
            limit = getattr(args, "limit", 10)
            verbose = getattr(args, "verbose", False)

            if device_name:
                self.info(f"ðŸ“Š RÃ©cupÃ©ration des activitÃ©s pour '{device_name}'...")
                serial = self.get_device_serial(device_name)
                if not serial:
                    return False
            else:
                self.info("ðŸ“Š RÃ©cupÃ©ration de toutes les activitÃ©s...")
                serial = None

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            # L'API Alexa ne filtre pas par serial ou type cÃ´tÃ© serveur
            # On rÃ©cupÃ¨re toutes les activitÃ©s puis on filtre localement
            activities = self.call_with_breaker(
                ctx.activity_mgr.get_activities,
                limit,
            )

            if not activities:
                self.warning("Aucune activitÃ© trouvÃ©e")
                return True

            # Filtrage local par appareil si spÃ©cifiÃ©
            if serial:
                activities = [a for a in activities if a.get("deviceSerialNumber") == serial]

            # Filtrage local par type si spÃ©cifiÃ©
            if activity_type and activity_type != "all":
                activities = [a for a in activities if a.get("activityType") == activity_type]

            # Afficher les activitÃ©s
            self._display_activities(activities, verbose)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration des activitÃ©s")
            self.error(f"Erreur: {e}")
            return False

    def _show_activity_info(self, args: argparse.Namespace) -> bool:
        """Afficher les dÃ©tails d'une activitÃ©."""
        try:
            self.info(f"â„¹ï¸  RÃ©cupÃ©ration activitÃ© '{args.id}'...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            activity = self.call_with_breaker(ctx.activity_mgr.get_activity, args.id)

            if activity:
                self._display_activity_details(activity)
                return True

            self.error(f"ActivitÃ© '{args.id}' non trouvÃ©e")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration de l'activitÃ©")
            self.error(f"Erreur: {e}")
            return False

    def _display_activities(self, activities: list, verbose: bool = False) -> None:
        """Affiche la liste des activitÃ©s de maniÃ¨re formatÃ©e."""
        print(f"\nðŸ“Š ActivitÃ©s ({len(activities)}):")
        print("=" * 80)
        for activity in activities:
            activity_id = activity.get("id", "N/A")
            activity_type = activity.get("type", "N/A")
            timestamp = activity.get("timestamp", "N/A")
            device_name = activity.get("deviceName", "N/A")
            description = activity.get("description", "N/A")

            # IcÃ´ne selon le type
            icon = self._get_activity_icon(activity_type)

            print(f"\n{icon} {description}")
            print(f"   Type: {activity_type} | Appareil: {device_name}")
            print(f"   Date: {timestamp}")

            if verbose:
                print(f"   ID: {activity_id}")

                # DÃ©tails supplÃ©mentaires selon le type
                if activity_type == "voice":
                    utterance = activity.get("utterance", "N/A")
                    alexa_response = activity.get("alexaResponse", "N/A")
                    print(f'   Commande vocale: "{utterance}"')
                    if alexa_response and alexa_response != "N/A":
                        print(f'   RÃ©ponse Alexa: "{alexa_response}"')

                elif activity_type == "music":
                    song = activity.get("song", "N/A")
                    artist = activity.get("artist", "N/A")
                    print(f"   Musique: {song} - {artist}")

                elif activity_type == "smart_home":
                    entity = activity.get("entity", "N/A")
                    action = activity.get("action", "N/A")
                    print(f"   Appareil: {entity} | Action: {action}")

    def _display_activity_details(self, activity: dict) -> None:
        """Affiche les dÃ©tails d'une activitÃ© de maniÃ¨re formatÃ©e."""
        activity_id = activity.get("id", "N/A")
        activity_type = activity.get("type", "N/A")
        timestamp = activity.get("timestamp", "N/A")
        device_name = activity.get("deviceName", "N/A")
        description = activity.get("description", "N/A")

        icon = self._get_activity_icon(activity_type)

        print(f"\n{icon} DÃ©tails de l'activitÃ©")
        print("=" * 80)
        print(f"ID: {activity_id}")
        print(f"Type: {activity_type}")
        print(f"Appareil: {device_name}")
        print(f"Date: {timestamp}")
        print(f"Description: {description}")

        # DÃ©tails spÃ©cifiques au type
        print("\nDÃ©tails:")

        if activity_type == "voice":
            utterance = activity.get("utterance", "N/A")
            intent = activity.get("intent", "N/A")
            print(f'  Commande vocale: "{utterance}"')
            print(f"  Intention: {intent}")

        elif activity_type == "music":
            song = activity.get("song", "N/A")
            artist = activity.get("artist", "N/A")
            album = activity.get("album", "N/A")
            provider = activity.get("provider", "N/A")
            print(f"  Titre: {song}")
            print(f"  Artiste: {artist}")
            print(f"  Album: {album}")
            print(f"  Service: {provider}")

        elif activity_type == "alarm":
            label = activity.get("label", "N/A")
            action = activity.get("action", "N/A")
            print(f"  Alarme: {label}")
            print(f"  Action: {action}")

        elif activity_type == "timer":
            label = activity.get("label", "N/A")
            duration = activity.get("duration", "N/A")
            action = activity.get("action", "N/A")
            print(f"  Timer: {label}")
            print(f"  DurÃ©e: {duration}")
            print(f"  Action: {action}")

        elif activity_type == "reminder":
            label = activity.get("label", "N/A")
            action = activity.get("action", "N/A")
            print(f"  Rappel: {label}")
            print(f"  Action: {action}")

        elif activity_type == "smart_home":
            entity = activity.get("entity", "N/A")
            action = activity.get("action", "N/A")
            value = activity.get("value", "N/A")
            print(f"  Appareil: {entity}")
            print(f"  Action: {action}")
            print(f"  Valeur: {value}")

    def _get_activity_icon(self, activity_type: str) -> str:
        """Retourne l'icÃ´ne correspondant au type d'activitÃ©."""
        icons = {
            "voice": "ðŸŽ¤",
            "music": "ðŸŽµ",
            "alarm": "â°",
            "timer": "â²ï¸",
            "reminder": "ðŸ“‹",
            "smart_home": "ðŸ ",
            "announcement": "ðŸ“¢",
            "routine": "ðŸ”„",
        }
        return icons.get(activity_type, "ðŸ“Š")

    def _show_last_device(self, args: argparse.Namespace) -> bool:
        """Affiche le dernier appareil utilisÃ©."""
        try:
            self.info("ðŸ”Š RÃ©cupÃ©ration du dernier appareil utilisÃ©...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            device_name = self.call_with_breaker(ctx.activity_mgr.get_last_device)

            if device_name:
                print(f"\nðŸ“± Dernier appareil utilisÃ© : {device_name}")
                return True
            else:
                self.warning("Aucun appareil trouvÃ© dans l'historique rÃ©cent")
                return True

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration du dernier appareil")
            self.error(f"Erreur: {e}")
            return False

    def _show_last_command(self, args: argparse.Namespace) -> bool:
        """Affiche la derniÃ¨re commande vocale."""
        try:
            device_filter = getattr(args, "device", None)

            if device_filter:
                self.info(f"ðŸ”Š RÃ©cupÃ©ration de la derniÃ¨re commande pour '{device_filter}'...")
            else:
                self.info("ðŸ”Š RÃ©cupÃ©ration de la derniÃ¨re commande...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            last_command = self.call_with_breaker(ctx.activity_mgr.get_last_command, device_filter)

            if last_command:
                if device_filter:
                    print(f"\nðŸŽ¤ DerniÃ¨re commande sur '{device_filter}' : \"{last_command}\"")
                else:
                    print(f'\nðŸŽ¤ DerniÃ¨re commande : "{last_command}"')
                return True
            else:
                if device_filter:
                    self.warning(f"Aucune commande trouvÃ©e pour l'appareil '{device_filter}'")
                else:
                    self.warning("Aucune commande trouvÃ©e dans l'historique rÃ©cent")
                return True

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration de la derniÃ¨re commande")
            self.error(f"Erreur: {e}")
            return False

    def _show_last_response(self, args: argparse.Namespace) -> bool:
        """Affiche la derniÃ¨re rÃ©ponse d'Alexa."""
        try:
            device_filter = getattr(args, "device", None)

            if device_filter:
                self.info(f"ðŸ”Š RÃ©cupÃ©ration de la derniÃ¨re rÃ©ponse Alexa pour '{device_filter}'...")
            else:
                self.info("ðŸ”Š RÃ©cupÃ©ration de la derniÃ¨re rÃ©ponse Alexa...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            last_response = self.call_with_breaker(ctx.activity_mgr.get_last_response, device_filter)

            if last_response:
                if device_filter:
                    print(f"\nðŸ—£ï¸  DerniÃ¨re rÃ©ponse Alexa sur '{device_filter}' : \"{last_response}\"")
                else:
                    print(f'\nðŸ—£ï¸  DerniÃ¨re rÃ©ponse Alexa : "{last_response}"')
                return True
            else:
                if device_filter:
                    self.warning(f"Aucune rÃ©ponse trouvÃ©e pour l'appareil '{device_filter}'")
                else:
                    self.warning("Aucune rÃ©ponse trouvÃ©e dans l'historique rÃ©cent")
                return True

        except Exception as e:
            self.logger.exception("Erreur lors de la rÃ©cupÃ©ration de la derniÃ¨re rÃ©ponse Alexa")
            self.error(f"Erreur: {e}")
            return False

