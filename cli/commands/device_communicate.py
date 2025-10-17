"""
Commandes de communication d'appareil Alexa.

Regroupe toutes les formes de communication:
- send: Envoyer un message/annonce
- announce: Annonce officielle
- sound: Jouer un son
- textcommand: Exécuter une commande texte

Auteur: M@nu
Date: 17 octobre 2025
"""

import argparse

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter


class CommunicationEffects:
    """Sons disponibles pour device.sound"""

    SOUNDS = {
        "airhorn": "amzn1.ask.skillId.airhorn",
        "knock": "amzn1.ask.skillId.knock",
        "bell": "amzn1.ask.skillId.bell",
        "cash_register": "amzn1.ask.skillId.cash_register",
        "bicycle_bell": "amzn1.ask.skillId.bicycle_bell",
        "gong": "amzn1.ask.skillId.gong",
        "ding_dong": "amzn1.ask.skillId.ding_dong",
        "glass_chime": "amzn1.ask.skillId.glass_chime",
        "wind_chimes": "amzn1.ask.skillId.wind_chimes",
        "clock_alarm": "amzn1.ask.skillId.clock_alarm",
        "trumpet": "amzn1.ask.skillId.trumpet",
        "violin": "amzn1.ask.skillId.violin",
        "police_siren": "amzn1.ask.skillId.police_siren",
        "fire_alarm": "amzn1.ask.skillId.fire_alarm",
    }


class DeviceCommunicateCommand(BaseCommand):
    """
    Commande de communication avec appareils Alexa.

    Regroupe les actions de communication:
    - send: Message/annonce
    - announce: Annonce officielle
    - sound: Jouer un son
    - textcommand: Exécuter une commande texte

    Example:
        >>> python alexa device communicate send -d "Salon" --message "Bonjour"
        >>> python alexa device communicate announce -d "Salon" --message "Annonce!"
        >>> python alexa device communicate sound -d "Salon" --effect "airhorn"
        >>> python alexa device communicate textcommand -d "Salon" --text "allume les lumières"
    """

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour les commandes de communication.

        Args:
            parser: Sous-parser pour la catégorie 'communicate'
        """
        parser.formatter_class = UniversalHelpFormatter
        parser.usage = argparse.SUPPRESS
        parser.description = "Communiquer avec les appareils Alexa"

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action de communication à exécuter",
            required=True,
        )

        # Action: send (message simple)
        send_parser = subparsers.add_parser(
            "send",
            help="Envoyer un message simple",
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        send_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil destinataire",
        )
        send_parser.add_argument(
            "--message",
            type=str,
            required=True,
            metavar="TEXT",
            help="Message à envoyer",
        )
        send_parser.add_argument(
            "--title",
            type=str,
            metavar="TITLE",
            help="Titre du message (optionnel)",
        )

        # Action: announce (annonce officielle avec effet)
        announce_parser = subparsers.add_parser(
            "announce",
            help="Faire une annonce officielle",
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        announce_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        announce_parser.add_argument(
            "--message",
            type=str,
            required=True,
            metavar="TEXT",
            help="Texte de l'annonce",
        )
        announce_parser.add_argument(
            "--volume",
            type=int,
            metavar="LEVEL",
            help="Volume pour l'annonce (0-100, optionnel)",
        )
        announce_parser.add_argument(
            "--ssml",
            action="store_true",
            help="Interpréter le message comme SSML",
        )

        # Action: sound (jouer un son)
        sound_parser = subparsers.add_parser(
            "sound",
            help="Jouer un son d'effet",
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        sound_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        sound_parser.add_argument(
            "--effect",
            type=str,
            required=True,
            metavar="EFFECT",
            help="Nom de l'effet sonore (voir: --list)",
        )
        sound_parser.add_argument(
            "--volume",
            type=int,
            metavar="LEVEL",
            help="Volume du son (0-100, optionnel)",
        )
        sound_parser.add_argument(
            "--list",
            action="store_true",
            help="Lister les effets sonores disponibles",
        )

        # Action: textcommand (commande texte comme si c'était une commande vocale)
        textcommand_parser = subparsers.add_parser(
            "textcommand",
            help="Exécuter une commande texte",
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        textcommand_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        textcommand_parser.add_argument(
            "--text",
            type=str,
            required=True,
            metavar="COMMAND",
            help="Commande texte (ex: 'allume les lumières du salon')",
        )

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande de communication.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        if not self.validate_connection():
            return False

        if args.action == "send":
            return self._send_message(args)
        elif args.action == "announce":
            return self._announce(args)
        elif args.action == "sound":
            return self._play_sound(args)
        elif args.action == "textcommand":
            return self._execute_textcommand(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _send_message(self, args: argparse.Namespace) -> bool:
        """
        Envoie un message simple.

        Args:
            args: Arguments (device, message, title)

        Returns:
            True si succès
        """
        try:
            device = args.device
            message = args.message
            title = getattr(args, "title", None)

            if not message or not message.strip():
                self.error("Le message ne peut pas être vide")
                return False

            if len(message) > 4096:
                self.error("Le message est trop long (max 4096 caractères)")
                return False

            # Vérifier que l'appareil existe
            devices = self.device_mgr.get_devices()
            if not any(d.get("accountName") == device for d in devices):
                self.error(f"Appareil '{device}' non trouvé")
                return False

            # Envoyer le message via VoiceCommandService
            result = self.call_with_breaker(self.voice_svc.speak_as_voice, device, message)

            if result:
                self.success(f"✅ Message envoyé à '{device}'")
                if title:
                    self.info(f"Titre: {title}")
            else:
                self.error("❌ Impossible d'envoyer le message")

            return result

        except Exception as e:
            self.logger.exception("Erreur lors de l'envoi du message")
            self.error(f"Erreur: {e}")
            return False

    def _announce(self, args: argparse.Namespace) -> bool:
        """
        Fait une annonce officielle.

        Args:
            args: Arguments (device, message, volume, ssml)

        Returns:
            True si succès
        """
        try:
            device = args.device
            message = args.message
            volume = getattr(args, "volume", None)
            is_ssml = getattr(args, "ssml", False)

            if not message or not message.strip():
                self.error("L'annonce ne peut pas être vide")
                return False

            # Vérifier que l'appareil existe
            devices = self.device_mgr.get_devices()
            if not any(d.get("accountName") == device for d in devices):
                self.error(f"Appareil '{device}' non trouvé")
                return False

            # Changer volume si spécifié
            old_volume = None
            if volume is not None:
                if not (0 <= volume <= 100):
                    self.error("Le volume doit être entre 0 et 100")
                    return False
                old_volume = self.device_mgr.get_volume(device)
                self.device_mgr.set_volume(device, volume)
                self.info(f"Volume temporaire: {volume}%")

            # Préparer le message
            announcement = message

            # Envoyer l'annonce
            result = self.call_with_breaker(self.voice_svc.speak_as_voice, device, announcement)

            # Restaurer volume si changé
            if old_volume is not None:
                self.device_mgr.set_volume(device, old_volume)
                self.info(f"Volume restauré: {old_volume}%")

            if result:
                self.success(f"🔊 Annonce envoyée à '{device}'")
                if is_ssml:
                    self.info("Format: SSML")
            else:
                self.error("❌ Impossible d'envoyer l'annonce")

            return result

        except Exception as e:
            self.logger.exception("Erreur lors de l'annonce")
            self.error(f"Erreur: {e}")
            return False

    def _play_sound(self, args: argparse.Namespace) -> bool:
        """
        Joue un son d'effet.

        Args:
            args: Arguments (device, effect, volume, list)

        Returns:
            True si succès
        """
        try:
            # Si --list, afficher les sons disponibles
            if getattr(args, "list", False):
                self.info("🔊 Effets sonores disponibles:")
                self.info("")
                for i, (name, _) in enumerate(CommunicationEffects.SOUNDS.items(), 1):
                    print(f"  {i:2d}. {name}")
                return True

            device = args.device
            effect = args.effect

            if effect not in CommunicationEffects.SOUNDS:
                self.error(f"Effet '{effect}' non reconnu")
                self.info("Utilisez: python alexa device communicate sound --list")
                return False

            # Vérifier que l'appareil existe
            devices = self.device_mgr.get_devices()
            if not any(d.get("accountName") == device for d in devices):
                self.error(f"Appareil '{device}' non trouvé")
                return False

            # Changer volume si spécifié
            old_volume = None
            volume = getattr(args, "volume", None)
            if volume is not None:
                if not (0 <= volume <= 100):
                    self.error("Le volume doit être entre 0 et 100")
                    return False
                old_volume = self.device_mgr.get_volume(device)
                self.device_mgr.set_volume(device, volume)
                self.info(f"Volume temporaire: {volume}%")

            # Jouer le son
            sound_id = CommunicationEffects.SOUNDS[effect]
            result = self.call_with_breaker(self.voice_svc.play_sound, device, sound_id)

            # Restaurer volume si changé
            if old_volume is not None:
                self.device_mgr.set_volume(device, old_volume)
                self.info(f"Volume restauré: {old_volume}%")

            if result:
                self.success(f"🔊 Son '{effect}' joué sur '{device}'")
            else:
                self.error("❌ Impossible de jouer le son")

            return result

        except Exception as e:
            self.logger.exception("Erreur lors de la lecture du son")
            self.error(f"Erreur: {e}")
            return False

    def _execute_textcommand(self, args: argparse.Namespace) -> bool:
        """
        Exécute une commande texte (comme une commande vocale).

        Args:
            args: Arguments (device, text)

        Returns:
            True si succès
        """
        try:
            device = args.device
            text = args.text

            if not text or not text.strip():
                self.error("La commande ne peut pas être vide")
                return False

            # Vérifier que l'appareil existe
            devices = self.device_mgr.get_devices()
            if not any(d.get("accountName") == device for d in devices):
                self.error(f"Appareil '{device}' non trouvé")
                return False

            # Exécuter la commande texte
            result = self.call_with_breaker(self.voice_svc.execute_text_command, device, text)

            if result:
                self.success(f"✅ Commande exécutée sur '{device}'")
                self.info(f"Commande: '{text}'")
            else:
                self.error("❌ Impossible d'exécuter la commande")

            return result

        except Exception as e:
            self.logger.exception("Erreur lors de l'exécution de la commande")
            self.error(f"Erreur: {e}")
            return False
