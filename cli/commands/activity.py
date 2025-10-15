"""Commande de consultation de l'historique d'activité Alexa.

Ce module fournit une interface CLI pour consulter l'historique :
- Voir les activités récentes
- Filtrer par appareil
- Filtrer par type d'activité
- Afficher les détails d'une activité
"""

import argparse
from typing import Any, Dict, List

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter
from cli.help_texts.activity_help import (
    ACTIVITY_DESCRIPTION,
    LIST_HELP,
)


class ActivityCommand(BaseCommand):
    """
    Commande pour consulter l'historique d'activité Alexa.

    L'historique permet de voir toutes les interactions vocales,
    commandes exécutées et événements survenus sur vos appareils.

    Exemples:
        >>> # Voir les activités récentes
        >>> alexa activity list

        >>> # Filtrer par appareil
        >>> alexa activity list -d "Salon Echo"

        >>> # Filtrer par type
        >>> alexa activity list --type voice

        >>> # Limiter le nombre de résultats
        >>> alexa activity list --limit 20

        >>> # Voir les détails d'une activité
        >>> alexa activity info --id "abc123"
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "activity"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "Consulter l'historique d'activité"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande activity.

        Args:
            parser: Parser à configurer
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description centralisée
        parser.description = ACTIVITY_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: list
        list_parser = subparsers.add_parser(
            "list",
            help="Lister activités",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        list_parser.add_argument(
            "--type",
            type=str,
            choices=["voice", "music", "alarm", "timer", "reminder", "smart_home", "all"],
            default="all",
            help="Type d'activité à filtrer",
        )
        list_parser.add_argument(
            "--limit",
            type=int,
            default=10,
            metavar="N",
            help="Nombre maximum d'activités à afficher (défaut: 10)",
        )

        # Action: lastdevice
        lastdevice_parser = subparsers.add_parser(
            "lastdevice",
            help="Dernier appareil utilisé",
            description="Affiche le nom du dernier appareil qui a eu une interaction avec Alexa",
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # Action: lastcommand
        lastcommand_parser = subparsers.add_parser(
            "lastcommand",
            help="Dernière commande vocale",
            description="Affiche la dernière commande vocale prononcée",
            formatter_class=ActionHelpFormatter,
            add_help=False,
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
            help="Dernière réponse d'Alexa",
            description="Affiche la dernière réponse vocale d'Alexa",
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        lastresponse_parser.add_argument(
            "-d",
            "--device",
            metavar="DEVICE_NAME",
            help="Filtrer par nom d'appareil (optionnel)",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande activity.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
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
        """Lister les activités."""
        try:
            device_name = getattr(args, "device", None)
            activity_type = getattr(args, "type", "all")
            limit = getattr(args, "limit", 10)
            verbose = getattr(args, "verbose", False)

            if device_name:
                self.info(f"📊 Récupération des activités pour '{device_name}'...")
                serial = self.get_device_serial(device_name)
                if not serial:
                    return False
            else:
                self.info("📊 Récupération de toutes les activités...")
                serial = None

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            # L'API Alexa ne filtre pas par serial ou type côté serveur
            # On récupère toutes les activités puis on filtre localement
            activities = self.call_with_breaker(
                ctx.activity_mgr.get_activities,
                limit,
            )

            if not activities:
                self.warning("Aucune activité trouvée")
                return True

            # Filtrage local par appareil si spécifié
            if serial:
                activities = [a for a in activities if a.get("deviceSerialNumber") == serial]

            # Filtrage local par type si spécifié
            if activity_type and activity_type != "all":
                activities = [a for a in activities if a.get("activityType") == activity_type]

            # Afficher les activités
            self._display_activities(activities, verbose)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération des activités")
            self.error(f"Erreur: {e}")
            return False

    def _show_activity_info(self, args: argparse.Namespace) -> bool:
        """Afficher les détails d'une activité."""
        try:
            self.info(f"ℹ️  Récupération activité '{args.id}'...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            activity = self.call_with_breaker(ctx.activity_mgr.get_activity, args.id)

            if activity:
                self._display_activity_details(activity)
                return True

            self.error(f"Activité '{args.id}' non trouvée")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération de l'activité")
            self.error(f"Erreur: {e}")
            return False

    def _display_activities(self, activities: list, verbose: bool = False) -> None:
        """Affiche la liste des activités de manière formatée."""
        print(f"\n📊 Activités ({len(activities)}):")
        print("=" * 80)
        for activity in activities:
            activity_id = activity.get("id", "N/A")
            activity_type = activity.get("type", "N/A")
            timestamp = activity.get("timestamp", "N/A")
            device_name = activity.get("deviceName", "N/A")
            description = activity.get("description", "N/A")

            # Icône selon le type
            icon = self._get_activity_icon(activity_type)

            print(f"\n{icon} {description}")
            print(f"   Type: {activity_type} | Appareil: {device_name}")
            print(f"   Date: {timestamp}")

            if verbose:
                print(f"   ID: {activity_id}")

                # Détails supplémentaires selon le type
                if activity_type == "voice":
                    utterance = activity.get("utterance", "N/A")
                    alexa_response = activity.get("alexaResponse", "N/A")
                    print(f'   Commande vocale: "{utterance}"')
                    if alexa_response and alexa_response != "N/A":
                        print(f'   Réponse Alexa: "{alexa_response}"')

                elif activity_type == "music":
                    song = activity.get("song", "N/A")
                    artist = activity.get("artist", "N/A")
                    print(f"   Musique: {song} - {artist}")

                elif activity_type == "smart_home":
                    entity = activity.get("entity", "N/A")
                    action = activity.get("action", "N/A")
                    print(f"   Appareil: {entity} | Action: {action}")

    def _display_activity_details(self, activity: dict) -> None:
        """Affiche les détails d'une activité de manière formatée."""
        activity_id = activity.get("id", "N/A")
        activity_type = activity.get("type", "N/A")
        timestamp = activity.get("timestamp", "N/A")
        device_name = activity.get("deviceName", "N/A")
        description = activity.get("description", "N/A")

        icon = self._get_activity_icon(activity_type)

        print(f"\n{icon} Détails de l'activité")
        print("=" * 80)
        print(f"ID: {activity_id}")
        print(f"Type: {activity_type}")
        print(f"Appareil: {device_name}")
        print(f"Date: {timestamp}")
        print(f"Description: {description}")

        # Détails spécifiques au type
        print("\nDétails:")

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
            print(f"  Durée: {duration}")
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
        """Retourne l'icône correspondant au type d'activité."""
        icons = {
            "voice": "🎤",
            "music": "🎵",
            "alarm": "⏰",
            "timer": "⏲️",
            "reminder": "📋",
            "smart_home": "🏠",
            "announcement": "📢",
            "routine": "🔄",
        }
        return icons.get(activity_type, "📊")

    def _show_last_device(self, args: argparse.Namespace) -> bool:
        """Affiche le dernier appareil utilisé."""
        try:
            self.info("🔊 Récupération du dernier appareil utilisé...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            device_name = self.call_with_breaker(ctx.activity_mgr.get_last_device)

            if device_name:
                print(f"\n📱 Dernier appareil utilisé : {device_name}")
                return True
            else:
                self.warning("Aucun appareil trouvé dans l'historique récent")
                return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération du dernier appareil")
            self.error(f"Erreur: {e}")
            return False

    def _show_last_command(self, args: argparse.Namespace) -> bool:
        """Affiche la dernière commande vocale."""
        try:
            device_filter = getattr(args, "device", None)

            if device_filter:
                self.info(f"🔊 Récupération de la dernière commande pour '{device_filter}'...")
            else:
                self.info("🔊 Récupération de la dernière commande...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            last_command = self.call_with_breaker(
                ctx.activity_mgr.get_last_command, device_filter
            )

            if last_command:
                if device_filter:
                    print(f"\n🎤 Dernière commande sur '{device_filter}' : \"{last_command}\"")
                else:
                    print(f'\n🎤 Dernière commande : "{last_command}"')
                return True
            else:
                if device_filter:
                    self.warning(f"Aucune commande trouvée pour l'appareil '{device_filter}'")
                else:
                    self.warning("Aucune commande trouvée dans l'historique récent")
                return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération de la dernière commande")
            self.error(f"Erreur: {e}")
            return False

    def _show_last_response(self, args: argparse.Namespace) -> bool:
        """Affiche la dernière réponse d'Alexa."""
        try:
            device_filter = getattr(args, "device", None)

            if device_filter:
                self.info(f"🔊 Récupération de la dernière réponse Alexa pour '{device_filter}'...")
            else:
                self.info("🔊 Récupération de la dernière réponse Alexa...")

            ctx = self.require_context()
            if not ctx.activity_mgr:
                self.error("ActivityManager non disponible")
                return False

            last_response = self.call_with_breaker(
                ctx.activity_mgr.get_last_response, device_filter
            )

            if last_response:
                if device_filter:
                    print(
                        f"\n🗣️  Dernière réponse Alexa sur '{device_filter}' : \"{last_response}\""
                    )
                else:
                    print(f'\n🗣️  Dernière réponse Alexa : "{last_response}"')
                return True
            else:
                if device_filter:
                    self.warning(f"Aucune réponse trouvée pour l'appareil '{device_filter}'")
                else:
                    self.warning("Aucune réponse trouvée dans l'historique récent")
                return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération de la dernière réponse Alexa")
            self.error(f"Erreur: {e}")
            return False
