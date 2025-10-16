"""
Commandes de contrôle de lecture (playback) - Refactorisé.

Gère: play, pause, stop, control, shuffle, repeat

Chaque commande est une classe BaseCommand indépendante intégrant CommandAdapter pour DI.

Auteur: M@nu
Date: 16 octobre 2025
"""

import argparse
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.command_adapter import get_command_adapter


# ============================================================================
# PLAYBACK PLAY COMMAND
# ============================================================================


class PlaybackPlayCommand(BaseCommand):
    """Reprendre/démarrer la lecture musicale."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.playback_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Reprendre la lecture."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"▶️  Reprise sur '{args.device}'...")

            if not self.playback_mgr:
                self.playback_mgr = self.adapter.get_manager("PlaybackManager")
                if not self.playback_mgr:
                    self.error("PlaybackManager non disponible")
                    return False

            result = self.playback_mgr.play(serial, device_type)

            if result:
                self.success("✅ Lecture reprise")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur play")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# PLAYBACK PAUSE COMMAND
# ============================================================================


class PlaybackPauseCommand(BaseCommand):
    """Mettre en pause la lecture musicale."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.playback_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Mettre en pause la lecture."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"⏸️  Pause sur '{args.device}'...")

            if not self.playback_mgr:
                self.playback_mgr = self.adapter.get_manager("PlaybackManager")
                if not self.playback_mgr:
                    self.error("PlaybackManager non disponible")
                    return False

            result = self.playback_mgr.pause(serial, device_type)

            if result:
                self.success("✅ Lecture mise en pause")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur pause")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# PLAYBACK NEXT COMMAND
# ============================================================================


class PlaybackNextCommand(BaseCommand):
    """Passer au morceau suivant."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.playback_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Passer au morceau suivant."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"⏭️  Morceau suivant sur '{args.device}'...")

            if not self.playback_mgr:
                self.playback_mgr = self.adapter.get_manager("PlaybackManager")
                if not self.playback_mgr:
                    self.error("PlaybackManager non disponible")
                    return False

            result = self.playback_mgr.next_track(serial, device_type)

            if result:
                self.success("✅ Morceau suivant")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur next")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# PLAYBACK PREVIOUS COMMAND
# ============================================================================


class PlaybackPreviousCommand(BaseCommand):
    """Revenir au morceau précédent."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.playback_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Revenir au morceau précédent."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"⏮️  Morceau précédent sur '{args.device}'...")

            if not self.playback_mgr:
                self.playback_mgr = self.adapter.get_manager("PlaybackManager")
                if not self.playback_mgr:
                    self.error("PlaybackManager non disponible")
                    return False

            result = self.playback_mgr.previous_track(serial, device_type)

            if result:
                self.success("✅ Morceau précédent")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur previous")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# PLAYBACK STOP COMMAND
# ============================================================================


class PlaybackStopCommand(BaseCommand):
    """Arrêter la lecture musicale."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.playback_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Arrêter la lecture."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"⏹️  Arrêt sur '{args.device}'...")

            if not self.playback_mgr:
                self.playback_mgr = self.adapter.get_manager("PlaybackManager")
                if not self.playback_mgr:
                    self.error("PlaybackManager non disponible")
                    return False

            result = self.playback_mgr.stop(serial, device_type)

            if result:
                self.success("✅ Lecture arrêtée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur stop")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# PLAYBACK SHUFFLE COMMAND
# ============================================================================


class PlaybackShuffleCommand(BaseCommand):
    """Contrôler le mode aléatoire."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.playback_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Contrôler le mode aléatoire."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            enabled = args.mode in ["on", "enable"]
            mode_text = "activé" if enabled else "désactivé"

            self.info(f"🔀 Mode aléatoire {mode_text} sur '{args.device}'...")

            if not self.playback_mgr:
                self.playback_mgr = self.adapter.get_manager("PlaybackManager")
                if not self.playback_mgr:
                    self.error("PlaybackManager non disponible")
                    return False

            result = self.playback_mgr.set_shuffle(serial, device_type, enabled)

            if result:
                self.success(f"✅ Mode aléatoire {mode_text}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur shuffle")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# PLAYBACK REPEAT COMMAND
# ============================================================================


class PlaybackRepeatCommand(BaseCommand):
    """Contrôler le mode répétition."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.playback_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Contrôler le mode répétition."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            mode_text = {
                "off": "désactivé",
                "one": "répéter 1 morceau",
                "all": "répéter tout",
            }

            self.info(
                f"🔁 Mode répétition: {mode_text.get(args.mode, args.mode)} sur '{args.device}'..."
            )

            if not self.playback_mgr:
                self.playback_mgr = self.adapter.get_manager("PlaybackManager")
                if not self.playback_mgr:
                    self.error("PlaybackManager non disponible")
                    return False

            result = self.playback_mgr.set_repeat(serial, device_type, args.mode.upper())

            if result:
                self.success(f"✅ Mode répétition: {mode_text.get(args.mode, args.mode)}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur repeat")
            self.error(f"Erreur: {e}")
            return False
