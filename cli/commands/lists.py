"""
Commande CLI pour gérer les listes (courses, tâches) - Thread-safe.
"""

import argparse
from typing import Optional

from cli.base_command import BaseCommand
from cli.command_parser import UniversalHelpFormatter
from cli.help_texts.lists_help import LISTS_DESCRIPTION


class ListsCommand(BaseCommand):
    """
    Commande pour gérer les listes de courses et tâches.

    Permet d'ajouter, lister, compléter et supprimer des tâches
    avec un système de cache local pour la persistance.
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "lists"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "Gérer les listes de courses et tâches"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande list.

        Args:
            parser: Parser à configurer
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description centralisée
        parser.description = LISTS_DESCRIPTION

        # Option globale pour le type de liste
        parser.add_argument(
            "--list",
            choices=["shopping", "todo"],
            default="shopping",
            help="Type de liste (défaut: shopping)",
        )

        # Option pour spécifier l'appareil Alexa
        parser.add_argument(
            "--device",
            metavar="DEVICE_NAME",
            help="Nom de l'appareil Alexa à utiliser (optionnel, utilise un Echo par défaut)",
        )

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: add
        add_parser = subparsers.add_parser(
            "add", help="Ajouter un élément", description="Ajouter un nouvel élément à une liste"
        )
        add_parser.add_argument("text", help="Texte de l'élément à ajouter")
        add_parser.add_argument(
            "-p",
            "--priority",
            choices=["low", "medium", "high"],
            default="medium",
            help="Priorité de la tâche (uniquement pour todo, défaut: medium)",
        )
        add_parser.add_argument("-d", "--due-date", help="Date d'échéance (uniquement pour todo, format: YYYY-MM-DD)")

        # Action: remove
        remove_parser = subparsers.add_parser(
            "remove", help="Supprimer un élément", description="Supprimer un élément de la liste"
        )
        remove_parser.add_argument("text", help="Texte de l'élément à supprimer")

        # Action: clear
        clear_parser = subparsers.add_parser(
            "clear",
            help="Vider la liste",
            description="Vider complètement la liste ou supprimer uniquement les éléments complétés",
        )
        clear_parser.add_argument(
            "--completed-only",
            action="store_true",
            help="Supprimer uniquement les éléments complétés (uniquement pour todo)",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande list.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "add":
            return self._add_todo(args)
        elif args.action == "remove":
            return self._remove_todo(args)
        elif args.action == "clear":
            return self._clear_todos(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _add_todo(self, args: argparse.Namespace) -> bool:
        """Ajoute un nouvel élément."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # Validation du texte
            if not args.text or not args.text.strip():
                self.error("❌ Le texte de l'élément ne peut pas être vide")
                return False

            text = args.text.strip()

            # Validation de la priorité pour les tâches
            if list_type == "todo" and args.priority not in ["low", "medium", "high"]:
                self.error(f"❌ Priorité invalide '{args.priority}'. Valeurs possibles: low, medium, high")
                return False

            # Validation de la date d'échéance pour les tâches
            if list_type == "todo" and args.due_date:
                try:
                    from datetime import datetime

                    datetime.strptime(args.due_date, "%Y-%m-%d")
                except ValueError:
                    self.error(f"❌ Format de date invalide '{args.due_date}'. Utilisez le format YYYY-MM-DD")
                    return False

            # Récupérer le serial du device si spécifié
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"❌ Appareil '{device_name}' non trouvé")
                    return False

            if list_type == "shopping":
                self.info(f"🛒 Ajout d'un élément à la liste de courses: '{args.text}'")
            else:
                self.info(f"📝 Ajout de la tâche: '{args.text}' (priorité: {args.priority})")

            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                self.error("ListManager non disponible")
                return False

            # Utiliser les vraies commandes vocales
            success = list_mgr.add_item(list_type, text, device_serial=device_serial)

            if success:
                if list_type == "shopping":
                    self.success(f"✅ Élément ajouté à la liste de courses: '{args.text}'")
                else:
                    self.success(f"✅ Tâche ajoutée: '{args.text}'")
                return True
            else:
                if list_type == "shopping":
                    self.error(f"❌ Échec de l'ajout de l'élément: '{args.text}'")
                else:
                    self.error(f"❌ Échec de l'ajout de la tâche: '{args.text}'")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'ajout de l'élément")
            self.error(f"Erreur: {e}")
            return False

    def _remove_todo(self, args: argparse.Namespace) -> bool:
        """Supprime un élément."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # Validation du texte
            if not args.text or not args.text.strip():
                self.error("❌ Le texte de l'élément ne peut pas être vide")
                return False

            text = args.text.strip()

            # Récupérer le serial du device si spécifié
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"❌ Appareil '{device_name}' non trouvé")
                    return False

            if list_type == "shopping":
                self.info(f"🗑️ Suppression de l'élément de courses: '{args.text}'")
            else:
                self.info(f"🗑️ Suppression de la tâche: '{args.text}'")

            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                self.error("ListManager non disponible")
                return False

            # Utiliser les vraies commandes vocales
            success = list_mgr.remove_item(list_type, text, device_serial=device_serial)

            if success:
                if list_type == "shopping":
                    self.success(f"✅ Élément de courses supprimé: '{args.text}'")
                else:
                    self.success(f"✅ Tâche supprimée: '{args.text}'")
                return True
            else:
                if list_type == "shopping":
                    self.error(f"❌ Échec de la suppression de l'élément: '{args.text}'")
                else:
                    self.error(f"❌ Échec de la suppression de la tâche: '{args.text}'")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression de l'élément")
            self.error(f"Erreur: {e}")
            return False

    def _list_items(self, args: argparse.Namespace) -> bool:
        """Affiche le contenu d'une liste."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # Récupérer le serial du device si spécifié
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"❌ Appareil '{device_name}' non trouvé")
                    return False

            if list_type == "shopping":
                self.info("🛒 Demande du contenu de la liste de courses...")
            else:
                self.info("📝 Demande du contenu de la liste de tâches...")

            ctx = self.require_context()
            voice = getattr(ctx, "voice_service", None)
            if not voice:
                self.error("VoiceCommandService non disponible")
                return False

            # Utiliser get_list_content pour récupérer le contenu via commande vocale
            voice.get_list_content(list_type, device_serial, wait_seconds=5.0)

            # La commande vocale a été envoyée, considérer cela comme un succès
            # même si on ne peut pas récupérer la réponse textuelle
            if list_type == "shopping":
                self.success("✅ 📋 Commande vocale envoyée pour afficher la liste de courses")
                self.info("� Vérifiez votre appareil Alexa pour entendre le contenu de la liste")
            else:
                self.success("✅ � Commande vocale envoyée pour afficher la liste de tâches")
                self.info("� Vérifiez votre appareil Alexa pour entendre le contenu de la liste")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de l'affichage du contenu de la liste")
            self.error(f"Erreur: {e}")
            return False

    def _clear_todos(self, args: argparse.Namespace) -> bool:
        """Vide la liste des éléments."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # Récupérer le serial du device si spécifié
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"❌ Appareil '{device_name}' non trouvé")
                    return False

            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                self.error("ListManager non disponible")
                return False

            # Pour les listes d'achat, appliquer automatiquement la confirmation
            if list_type == "shopping" and not args.completed_only:
                # Vérifier d'abord si la liste contient des éléments
                list_is_empty = self._check_list_is_empty(list_type)
                if list_is_empty:
                    self.info("🗑️ La liste de courses est déjà vide")
                    self.success("✅ Liste de courses vidée (était déjà vide)")
                    return True
                self.info("🗑️ Vidage de la liste de courses...")
                import sys

                sys.stdout.flush()
                self.info("📝 Envoi de la commande de vidage...")
                sys.stdout.flush()

                # Utiliser les vraies commandes vocales pour vider la liste
                success = list_mgr.clear_list(
                    list_type, completed_only=args.completed_only, device_serial=device_serial
                )

                if success:
                    # Attendre 4 secondes pour que Alexa réponde (au lieu de 3)
                    import time

                    self.info("⏳ Attente de confirmation...")
                    sys.stdout.flush()
                    time.sleep(4.0)

                    has_voice = hasattr(ctx, "voice_service")
                    voice_val = getattr(ctx, "voice_service", None)
                    self.logger.info(f"🔍 Voice service check: hasattr={has_voice}, value={voice_val}")
                    if hasattr(ctx, "voice_service") and ctx.voice_service:
                        # Puisque la liste n'est pas vide, on s'attend à une confirmation
                        # Répondre automatiquement "oui" après un délai raisonnable
                        self.info("🤖 Réponse automatique (liste non vide)...")
                        sys.stdout.flush()
                        time.sleep(1.0)  # Attendre 1 seconde avant de répondre (au lieu de 2)
                        ctx.voice_service.speak("oui", device_serial)
                        time.sleep(1.0)
                        self.success("✅ Liste vidée avec succès")
                        return True

                    # Si pas de voice service
                    self.success("✅ Liste vidée")
                    return True
                else:
                    self.error("❌ Échec du vidage")
                    return False

            # Pour les tâches ou si completed_only, pas de confirmation spéciale
            success = list_mgr.clear_list(list_type, completed_only=args.completed_only, device_serial=device_serial)
            if success:
                if list_type == "shopping":
                    self.success("✅ Liste de courses vidée")
                else:
                    if args.completed_only:
                        self.success("✅ Tâches complétées supprimées")
                    else:
                        self.success("✅ Liste de tâches vidée")
            else:
                if list_type == "shopping":
                    self.error("❌ Échec du vidage")
                else:
                    self.error("❌ Échec du vidage")
            return success

        except Exception as e:
            self.logger.exception("Erreur lors du vidage de la liste")
            self.error(f"Erreur: {e}")
            return False

    def _check_html_confirmation(self, device_serial: Optional[str] = None) -> bool:
        """
        Vérifie si Alexa demande une confirmation en analysant la réponse HTML.

        Args:
            device_serial: Serial du device (optionnel)

        Returns:
            True si une confirmation est détectée, False sinon
        """
        try:
            # Récupérer la page HTML de l'historique d'activité ou de l'état des listes
            # On utilise la page d'activité qui peut contenir des informations sur les interactions récentes
            url = "https://www.amazon.fr/alexa-privacy/apd/activity?ref=activityHistory"

            ctx = self.require_context()
            auth = getattr(ctx, "auth", None)
            if not auth:
                self.logger.debug("Auth manquante pour récupérer HTML")
                return False

            # Use the compatibility factory to obtain an http_client from legacy auth
            try:
                from core.base_manager import create_http_client_from_auth

                client = create_http_client_from_auth(auth)
            except Exception:
                # Conservative fallback: keep legacy behavior if factory import fails
                # Do not access legacy `session` attribute here; use the auth object
                # directly as a last-resort HTTP client (adapter exists elsewhere).
                client = auth

            if not client:
                self.logger.debug("Client HTTP non disponible pour récupérer HTML")
                return False

            response = client.get(url, headers={"csrf": getattr(client, "csrf", getattr(auth, "csrf", ""))}, timeout=5)

            if response.status_code != 200:
                self.logger.debug(f"Impossible de récupérer la page HTML: {response.status_code}")
                return False

            html_content = response.text
            self.logger.debug(f"HTML récupéré ({len(html_content)} caractères)")

            # DEBUG: Afficher un extrait du HTML pour analyse
            if len(html_content) > 0:
                self.logger.debug(f"Extrait HTML (500 premiers caractères): {html_content[:500]}")
                # Chercher des patterns spécifiques dans le HTML
                import re

                csrf_matches = re.findall(r'csrf[^"]*"([^"]+)"', html_content, re.IGNORECASE)
                if csrf_matches:
                    self.logger.debug(f"Tokens CSRF trouvés: {csrf_matches[:3]}")

            html_lower = html_content.lower()

            # Mots-clés spécifiques indiquant une vraie demande de confirmation
            # Plus spécifiques que les mots-clés généraux pour éviter les faux positifs
            confirmation_patterns = [
                "voulez-vous vraiment",
                "êtes-vous sûr",
                "sure you want",
                "cela supprimera",
                "this will delete",
                "confirmer la suppression",
                "confirm deletion",
                "tous les éléments",
                "all items",
                "liste n'est pas vide",
                "list is not empty",
            ]

            # Vérifier si le HTML contient des patterns spécifiques de confirmation
            html_lower = html_content.lower()
            for pattern in confirmation_patterns:
                if pattern in html_lower:
                    self.logger.debug(f"Confirmation spécifique détectée via HTML: '{pattern}'")
                    return True

            # Fallback: chercher des mots-clés plus généraux mais seulement s'ils sont
            # accompagnés d'indicateurs de question - DÉSACTIVÉ car trop de faux positifs
            # question_indicators = ["?", "oui", "non", "yes", "no", "d'accord", "ok"]
            # has_question = any(indicator in html_lower for indicator in question_indicators)

            # if has_question:
            #     general_keywords = ["vider", "supprimer", "effacer", "clear", "delete"]
            #     if any(keyword in html_lower for keyword in general_keywords):
            #         self.logger.debug("Confirmation générale détectée (question + mot-clé)")
            #         return True

            # Pour l'instant, ne détecter que les patterns très spécifiques
            # La page d'activité contient toujours des éléments qui déclenchent des faux positifs

            self.logger.debug("Aucune confirmation détectée dans le HTML")
            return False

        except Exception as e:
            self.logger.debug(f"Erreur lors de la vérification HTML: {e}")
            return False

    def _check_list_is_empty(self, list_type: str) -> bool:
        """
        Vérifie si une liste est vide en utilisant les API REST.

        Args:
            list_type: Type de liste ('shopping', 'todo')

        Returns:
            True si la liste est vide ou si on ne peut pas déterminer, False si elle contient des éléments
        """
        try:
            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                return True  # Considérer comme vide si pas de manager

            # Essayer de récupérer la liste via l'API
            list_data = list_mgr.get_list(list_type)
            if list_data:
                items = list_data.get("items", [])
                if isinstance(items, list):
                    is_empty = len(items) == 0
                    self.logger.debug(f"Liste {list_type} contient {len(items)} élément(s)")
                    return is_empty
                else:
                    # Si items n'est pas une liste, considérer comme non vide par sécurité
                    return False

            # Si on ne peut pas récupérer la liste, utiliser une commande vocale pour vérifier
            if hasattr(ctx, "voice_service") and ctx.voice_service:
                # Demander à Alexa de lire la liste et analyser la réponse
                response = ctx.voice_service.ask_and_get_response(
                    f"lis ma liste de {'courses' if list_type == 'shopping' else 'tâches'}",
                    wait_seconds=3.0,
                )

                if response:
                    response_lower = response.lower()
                    # Mots-clés indiquant que la liste est vide
                    empty_keywords = [
                        "vide",
                        "rien",
                        "aucun élément",
                        "pas d'élément",
                        "empty",
                        "no items",
                        "nothing",
                    ]

                    for keyword in empty_keywords:
                        if keyword in response_lower:
                            self.logger.debug(f"Liste {list_type} détectée comme vide via réponse vocale")
                            return True

                    # Si la réponse contient des éléments spécifiques, la liste n'est pas vide
                    if any(word in response_lower for word in ["pain", "lait", "œuf", "farine", "beurre", "fromage"]):
                        self.logger.debug(f"Liste {list_type} contient des éléments")
                        return False

            # Par défaut, considérer comme potentiellement non vide pour demander confirmation
            return False

        except Exception as e:
            self.logger.debug(f"Erreur lors de la vérification si liste vide: {e}")
            return False  # Considérer comme non vide par sécurité
