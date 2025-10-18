﻿"""
Commande CLI pour g�rer les listes (courses, t�ches) - Thread-safe.
"""

import argparse
from typing import Optional

from utils.cli.base_command import BaseCommand
from utils.cli.command_parser import UniversalHelpFormatter


class ListsCommand(BaseCommand):
    """
    Commande pour g�rer les listes de courses et t�ches.

    Permet d'ajouter, lister, compl�ter et supprimer des t�ches
    avec un syst�me de cache local pour la persistance.
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "lists"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "G�rer les listes de courses et t�ches"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande list.

        Args:
            parser: Parser � configurer
        """
        # Utiliser le formatter universel pour l'ordre exact demand�
        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description simplifi�e
        parser.description = "G�rer les listes de courses et t�ches"

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action � ex�cuter",
            required=True,
        )

        # Action: add
        add_parser = subparsers.add_parser(
            "add", help="Ajouter un �l�ment", description="Ajouter un nouvel �l�ment � une liste"
        )
        add_parser.add_argument("text", help="Texte de l'�l�ment � ajouter")
        add_parser.add_argument(
            "--list",
            choices=["shopping", "todo"],
            default="shopping",
            help="Type de liste (d�faut: shopping)",
        )
        add_parser.add_argument(
            "--device",
            metavar="DEVICE_NAME",
            help="Nom de l'appareil Alexa � utiliser (optionnel)",
        )
        add_parser.add_argument(
            "-p",
            "--priority",
            choices=["low", "medium", "high"],
            default="medium",
            help="Priorit� de la t�che (uniquement pour todo, d�faut: medium)",
        )
        add_parser.add_argument("-d", "--due-date", help="Date d'�ch�ance (uniquement pour todo, format: YYYY-MM-DD)")

        # Action: remove
        remove_parser = subparsers.add_parser(
            "remove", help="Supprimer un �l�ment", description="Supprimer un �l�ment de la liste"
        )
        remove_parser.add_argument("text", help="Texte de l'�l�ment � supprimer")
        remove_parser.add_argument(
            "--list",
            choices=["shopping", "todo"],
            default="shopping",
            help="Type de liste (d�faut: shopping)",
        )
        remove_parser.add_argument(
            "--device",
            metavar="DEVICE_NAME",
            help="Nom de l'appareil Alexa � utiliser (optionnel)",
        )

        # Action: clear
        clear_parser = subparsers.add_parser(
            "clear",
            help="Vider la liste",
            description="Vider compl�tement la liste ou supprimer uniquement les �l�ments compl�t�s",
        )
        clear_parser.add_argument(
            "--list",
            choices=["shopping", "todo"],
            default="shopping",
            help="Type de liste (d�faut: shopping)",
        )
        clear_parser.add_argument(
            "--device",
            metavar="DEVICE_NAME",
            help="Nom de l'appareil Alexa � utiliser (optionnel)",
        )
        clear_parser.add_argument(
            "--completed-only",
            action="store_true",
            help="Supprimer uniquement les �l�ments compl�t�s (uniquement pour todo)",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Ex�cute la commande list.

        Args:
            args: Arguments pars�s

        Returns:
            True si succ�s, False sinon
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
        """Ajoute un nouvel �l�ment."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # Validation du texte
            if not args.text or not args.text.strip():
                self.error("? Le texte de l'�l�ment ne peut pas �tre vide")
                return False

            text = args.text.strip()

            # Validation de la priorit� pour les t�ches
            if list_type == "todo" and args.priority not in ["low", "medium", "high"]:
                self.error(f"? Priorit� invalide '{args.priority}'. Valeurs possibles: low, medium, high")
                return False

            # Validation de la date d'�ch�ance pour les t�ches
            if list_type == "todo" and args.due_date:
                try:
                    from datetime import datetime

                    datetime.strptime(args.due_date, "%Y-%m-%d")
                except ValueError:
                    self.error(f"? Format de date invalide '{args.due_date}'. Utilisez le format YYYY-MM-DD")
                    return False

            # R�cup�rer le serial du device si sp�cifi�
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"? Appareil '{device_name}' non trouv�")
                    return False

            if list_type == "shopping":
                self.info(f"?? Ajout d'un �l�ment � la liste de courses: '{args.text}'")
            else:
                self.info(f"?? Ajout de la t�che: '{args.text}' (priorit�: {args.priority})")

            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                self.error("ListManager non disponible")
                return False

            # Utiliser les vraies commandes vocales
            success = bool(list_mgr.add_item(list_type, text, device_serial=device_serial))

            if success:
                if list_type == "shopping":
                    self.success(f"? �l�ment ajout� � la liste de courses: '{args.text}'")
                else:
                    self.success(f"? T�che ajout�e: '{args.text}'")
                return True
            else:
                if list_type == "shopping":
                    self.error(f"? �chec de l'ajout de l'�l�ment: '{args.text}'")
                else:
                    self.error(f"? �chec de l'ajout de la t�che: '{args.text}'")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'ajout de l'�l�ment")
            self.error(f"Erreur: {e}")
            return False

    def _remove_todo(self, args: argparse.Namespace) -> bool:
        """Supprime un �l�ment."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # Validation du texte
            if not args.text or not args.text.strip():
                self.error("? Le texte de l'�l�ment ne peut pas �tre vide")
                return False

            text = args.text.strip()

            # R�cup�rer le serial du device si sp�cifi�
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"? Appareil '{device_name}' non trouv�")
                    return False

            if list_type == "shopping":
                self.info(f"??? Suppression de l'�l�ment de courses: '{args.text}'")
            else:
                self.info(f"??? Suppression de la t�che: '{args.text}'")

            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                self.error("ListManager non disponible")
                return False

            # Utiliser les vraies commandes vocales
            success = bool(list_mgr.remove_item(list_type, text, device_serial=device_serial))

            if success:
                if list_type == "shopping":
                    self.success(f"? �l�ment de courses supprim�: '{args.text}'")
                else:
                    self.success(f"? T�che supprim�e: '{args.text}'")
                return True
            else:
                if list_type == "shopping":
                    self.error(f"? �chec de la suppression de l'�l�ment: '{args.text}'")
                else:
                    self.error(f"? �chec de la suppression de la t�che: '{args.text}'")
                return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression de l'�l�ment")
            self.error(f"Erreur: {e}")
            return False

    def _list_items(self, args: argparse.Namespace) -> bool:
        """Affiche le contenu d'une liste."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # R�cup�rer le serial du device si sp�cifi�
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"? Appareil '{device_name}' non trouv�")
                    return False

            if list_type == "shopping":
                self.info("?? Demande du contenu de la liste de courses...")
            else:
                self.info("?? Demande du contenu de la liste de t�ches...")

            ctx = self.require_context()
            voice = getattr(ctx, "voice_service", None)
            if not voice:
                self.error("VoiceCommandService non disponible")
                return False

            # Utiliser get_list_content pour r�cup�rer le contenu via commande vocale
            voice.get_list_content(list_type, device_serial, wait_seconds=5.0)

            # La commande vocale a �t� envoy�e, consid�rer cela comme un succ�s
            # m�me si on ne peut pas r�cup�rer la r�ponse textuelle
            if list_type == "shopping":
                self.success("? ?? Commande vocale envoy�e pour afficher la liste de courses")
                self.info("� V�rifiez votre appareil Alexa pour entendre le contenu de la liste")
            else:
                self.success("? � Commande vocale envoy�e pour afficher la liste de t�ches")
                self.info("� V�rifiez votre appareil Alexa pour entendre le contenu de la liste")
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de l'affichage du contenu de la liste")
            self.error(f"Erreur: {e}")
            return False

    def _clear_todos(self, args: argparse.Namespace) -> bool:
        """Vide la liste des �l�ments."""
        try:
            list_type = args.list
            device_name = getattr(args, "device", None)

            # R�cup�rer le serial du device si sp�cifi�
            device_serial = None
            if device_name:
                device_serial = self.get_device_serial(device_name)
                if not device_serial:
                    self.error(f"? Appareil '{device_name}' non trouv�")
                    return False

            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                self.error("ListManager non disponible")
                return False

            # Pour les listes d'achat, appliquer automatiquement la confirmation
            if list_type == "shopping" and not args.completed_only:
                # V�rifier d'abord si la liste contient des �l�ments
                list_is_empty = self._check_list_is_empty(list_type)
                if list_is_empty:
                    self.info("??? La liste de courses est d�j� vide")
                    self.success("? Liste de courses vid�e (�tait d�j� vide)")
                    return True
                self.info("??? Vidage de la liste de courses...")
                import sys

                sys.stdout.flush()
                self.info("?? Envoi de la commande de vidage...")
                sys.stdout.flush()

                # Utiliser les vraies commandes vocales pour vider la liste
                success = bool(
                    list_mgr.clear_list(list_type, completed_only=args.completed_only, device_serial=device_serial)
                )

                if success:
                    # Attendre 4 secondes pour que Alexa r�ponde (au lieu de 3)
                    import time

                    self.info("? Attente de confirmation...")
                    sys.stdout.flush()
                    time.sleep(4.0)

                    has_voice = hasattr(ctx, "voice_service")
                    voice_val = getattr(ctx, "voice_service", None)
                    self.logger.info(f"?? Voice service check: hasattr={has_voice}, value={voice_val}")
                    if hasattr(ctx, "voice_service") and ctx.voice_service:
                        # Puisque la liste n'est pas vide, on s'attend � une confirmation
                        # R�pondre automatiquement "oui" apr�s un d�lai raisonnable
                        self.info("?? R�ponse automatique (liste non vide)...")
                        sys.stdout.flush()
                        time.sleep(1.0)  # Attendre 1 seconde avant de r�pondre (au lieu de 2)
                        ctx.voice_service.speak("oui", device_serial)
                        time.sleep(1.0)
                        self.success("? Liste vid�e avec succ�s")
                        return True

                    # Si pas de voice service
                    self.success("? Liste vid�e")
                    return True
                else:
                    self.error("? �chec du vidage")
                    return False

            # Pour les t�ches ou si completed_only, pas de confirmation sp�ciale
            success = bool(
                list_mgr.clear_list(list_type, completed_only=args.completed_only, device_serial=device_serial)
            )
            if success:
                if list_type == "shopping":
                    self.success("? Liste de courses vid�e")
                else:
                    if args.completed_only:
                        self.success("? T�ches compl�t�es supprim�es")
                    else:
                        self.success("? Liste de t�ches vid�e")
            else:
                if list_type == "shopping":
                    self.error("? �chec du vidage")
                else:
                    self.error("? �chec du vidage")
            return success

        except Exception as e:
            self.logger.exception("Erreur lors du vidage de la liste")
            self.error(f"Erreur: {e}")
            return False

    def _check_html_confirmation(self, device_serial: Optional[str] = None) -> bool:
        """
        V�rifie si Alexa demande une confirmation en analysant la r�ponse HTML.

        Args:
            device_serial: Serial du device (optionnel)

        Returns:
            True si une confirmation est d�tect�e, False sinon
        """
        try:
            # R�cup�rer la page HTML de l'historique d'activit� ou de l'�tat des listes
            # On utilise la page d'activit� qui peut contenir des informations sur les interactions r�centes
            url = "https://www.amazon.fr/alexa-privacy/apd/activity?ref=activityHistory"

            ctx = self.require_context()
            auth = getattr(ctx, "auth", None)
            if not auth:
                self.logger.debug("Auth manquante pour r�cup�rer HTML")
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
                self.logger.debug("Client HTTP non disponible pour r�cup�rer HTML")
                return False

            response = client.get(url, headers={"csrf": getattr(client, "csrf", getattr(auth, "csrf", ""))}, timeout=5)

            if response.status_code != 200:
                self.logger.debug(f"Impossible de r�cup�rer la page HTML: {response.status_code}")
                return False

            html_content = response.text
            self.logger.debug(f"HTML r�cup�r� ({len(html_content)} caract�res)")

            # DEBUG: Afficher un extrait du HTML pour analyse
            if len(html_content) > 0:
                self.logger.debug(f"Extrait HTML (500 premiers caract�res): {html_content[:500]}")
                # Chercher des patterns sp�cifiques dans le HTML
                import re

                csrf_matches = re.findall(r'csrf[^"]*"([^"]+)"', html_content, re.IGNORECASE)
                if csrf_matches:
                    self.logger.debug(f"Tokens CSRF trouv�s: {csrf_matches[:3]}")

            html_lower = html_content.lower()

            # Mots-cl�s sp�cifiques indiquant une vraie demande de confirmation
            # Plus sp�cifiques que les mots-cl�s g�n�raux pour �viter les faux positifs
            confirmation_patterns = [
                "voulez-vous vraiment",
                "�tes-vous s�r",
                "sure you want",
                "cela supprimera",
                "this will delete",
                "confirmer la suppression",
                "confirm deletion",
                "tous les �l�ments",
                "all items",
                "liste n'est pas vide",
                "list is not empty",
            ]

            # V�rifier si le HTML contient des patterns sp�cifiques de confirmation
            html_lower = html_content.lower()
            for pattern in confirmation_patterns:
                if pattern in html_lower:
                    self.logger.debug(f"Confirmation sp�cifique d�tect�e via HTML: '{pattern}'")
                    return True

            # Fallback: chercher des mots-cl�s plus g�n�raux mais seulement s'ils sont
            # accompagn�s d'indicateurs de question - D�SACTIV� car trop de faux positifs
            # question_indicators = ["?", "oui", "non", "yes", "no", "d'accord", "ok"]
            # has_question = any(indicator in html_lower for indicator in question_indicators)

            # if has_question:
            #     general_keywords = ["vider", "supprimer", "effacer", "clear", "delete"]
            #     if any(keyword in html_lower for keyword in general_keywords):
            #         self.logger.debug("Confirmation g�n�rale d�tect�e (question + mot-cl�)")
            #         return True

            # Pour l'instant, ne d�tecter que les patterns tr�s sp�cifiques
            # La page d'activit� contient toujours des �l�ments qui d�clenchent des faux positifs

            self.logger.debug("Aucune confirmation d�tect�e dans le HTML")
            return False

        except Exception as e:
            self.logger.debug(f"Erreur lors de la v�rification HTML: {e}")
            return False

    def _check_list_is_empty(self, list_type: str) -> bool:
        """
        V�rifie si une liste est vide en utilisant les API REST.

        Args:
            list_type: Type de liste ('shopping', 'todo')

        Returns:
            True si la liste est vide ou si on ne peut pas d�terminer, False si elle contient des �l�ments
        """
        try:
            ctx = self.require_context()
            list_mgr = getattr(ctx, "list_mgr", None)
            if not list_mgr:
                return True  # Consid�rer comme vide si pas de manager

            # Essayer de r�cup�rer la liste via l'API
            list_data = list_mgr.get_list(list_type)
            if list_data:
                from typing import Any, Dict, List, cast

                items = list_data.get("items", [])
                if isinstance(items, list):
                    items_typed = cast(List[Dict[str, Any]], items)
                    is_empty = len(items_typed) == 0
                    self.logger.debug(f"Liste {list_type} contient {len(items_typed)} �l�ment(s)")
                    return is_empty
                else:
                    # Si items n'est pas une liste, consid�rer comme non vide par s�curit�
                    return False

            # Si on ne peut pas r�cup�rer la liste, utiliser une commande vocale pour v�rifier
            if hasattr(ctx, "voice_service") and ctx.voice_service:
                # Demander � Alexa de lire la liste et analyser la r�ponse
                response = ctx.voice_service.ask_and_get_response(
                    f"lis ma liste de {'courses' if list_type == 'shopping' else 't�ches'}",
                    wait_seconds=3.0,
                )

                if response:
                    response_lower = response.lower()
                    # Mots-cl�s indiquant que la liste est vide
                    empty_keywords = [
                        "vide",
                        "rien",
                        "aucun �l�ment",
                        "pas d'�l�ment",
                        "empty",
                        "no items",
                        "nothing",
                    ]

                    for keyword in empty_keywords:
                        if keyword in response_lower:
                            self.logger.debug(f"Liste {list_type} d�tect�e comme vide via r�ponse vocale")
                            return True

                    # Si la r�ponse contient des �l�ments sp�cifiques, la liste n'est pas vide
                    if any(word in response_lower for word in ["pain", "lait", "�uf", "farine", "beurre", "fromage"]):
                        self.logger.debug(f"Liste {list_type} contient des �l�ments")
                        return False

            # Par d�faut, consid�rer comme potentiellement non vide pour demander confirmation
            return False

        except Exception as e:
            self.logger.debug(f"Erreur lors de la v�rification si liste vide: {e}")
            return False  # Consid�rer comme non vide par s�curit�




