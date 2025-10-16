"""
Commandes restantes - Tier 4 (Timers, Auth, Cache) - Refactorisé.

Timers: add, list, delete
Auth: login, logout, status
Cache: clear, update

Chaque commande est une classe BaseCommand indépendante avec CommandAdapter DI.

Auteur: M@nu
Date: 16 octobre 2025
"""

import argparse
from typing import Any, Optional

from cli.base_command import BaseCommand
from cli.command_adapter import get_command_adapter


# ============================================================================
# TIMER COMMANDS
# ============================================================================


class TimerAddCommand(BaseCommand):
    """Créer un minuteur."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.timer_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Créer un minuteur."""
        try:
            if not hasattr(args, "device") or not args.device:
                self.error("Paramètre requis: --device")
                return False

            if not hasattr(args, "duration") or not args.duration:
                self.error("Paramètre requis: --duration (en secondes)")
                return False

            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            label = getattr(args, "label", "Minuteur")

            self.info(f"⏲️  Création d'un minuteur sur '{args.device}'...")

            if not self.timer_mgr:
                self.timer_mgr = self.adapter.get_manager("TimerManager")
                if not self.timer_mgr:
                    self.error("TimerManager non disponible")
                    return False

            result = self.timer_mgr.create_timer(
                serial, device_type, args.duration, label
            )

            if result:
                self.success(f"✅ Minuteur créé: {label}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur add")
            self.error(f"Erreur: {e}")
            return False


class TimerListCommand(BaseCommand):
    """Lister les minuteurs."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.timer_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Lister les minuteurs."""
        try:
            device_info = self.get_device_serial_and_type(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"⏲️  Récupération des minuteurs...")

            if not self.timer_mgr:
                self.timer_mgr = self.adapter.get_manager("TimerManager")
                if not self.timer_mgr:
                    self.error("TimerManager non disponible")
                    return False

            timers = self.timer_mgr.get_timers(serial, device_type)

            if not timers:
                self.warning("Aucun minuteur trouvé")
                return True

            if hasattr(args, "json") and args.json:
                self.output(timers, json_mode=True)
            else:
                table_data = [
                    [
                        t.get("label", "N/A"),
                        t.get("remaining", "N/A"),
                        "⏲️  Active" if t.get("active") else "⏸️  Paused",
                    ]
                    for t in timers
                ]
                table = self.format_table(table_data, ["Label", "Temps restant", "État"])
                print(table)

            self.success(f"✅ {len(timers)} minuteur(s) trouvé(s)")
            return True

        except Exception as e:
            self.logger.exception("Erreur list")
            self.error(f"Erreur: {e}")
            return False


class TimerDeleteCommand(BaseCommand):
    """Supprimer un minuteur."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.timer_mgr: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Supprimer un minuteur."""
        try:
            if not hasattr(args, "timer_id") or not args.timer_id:
                self.error("Paramètre requis: timer_id")
                return False

            self.info(f"⏲️  Suppression du minuteur...")

            if not self.timer_mgr:
                self.timer_mgr = self.adapter.get_manager("TimerManager")
                if not self.timer_mgr:
                    self.error("TimerManager non disponible")
                    return False

            result = self.timer_mgr.delete_timer(args.timer_id)

            if result:
                self.success(f"✅ Minuteur supprimé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur delete")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# AUTH COMMANDS
# ============================================================================


class AuthLoginCommand(BaseCommand):
    """Se connecter à Alexa."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.auth_service: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Se connecter."""
        try:
            self.info("🔐 Connexion à Alexa...")

            if not self.auth_service:
                self.auth_service = self.adapter.get_manager("AuthService")
                if not self.auth_service:
                    self.error("AuthService non disponible")
                    return False

            result = self.auth_service.login()

            if result:
                self.success(f"✅ Connexion réussie")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur login")
            self.error(f"Erreur: {e}")
            return False


class AuthLogoutCommand(BaseCommand):
    """Se déconnecter d'Alexa."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.auth_service: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Se déconnecter."""
        try:
            self.info("🔐 Déconnexion d'Alexa...")

            if not self.auth_service:
                self.auth_service = self.adapter.get_manager("AuthService")
                if not self.auth_service:
                    self.error("AuthService non disponible")
                    return False

            result = self.auth_service.logout()

            if result:
                self.success(f"✅ Déconnexion réussie")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur logout")
            self.error(f"Erreur: {e}")
            return False


class AuthStatusCommand(BaseCommand):
    """Vérifier le statut de connexion."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.auth_service: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Vérifier le statut."""
        try:
            self.info("🔐 Vérification du statut...")

            if not self.auth_service:
                self.auth_service = self.adapter.get_manager("AuthService")
                if not self.auth_service:
                    self.error("AuthService non disponible")
                    return False

            status = self.auth_service.get_status()

            if status:
                if hasattr(args, "json") and args.json:
                    self.output(status, json_mode=True)
                else:
                    for key, value in status.items():
                        print(f"  {key:.<30} {value}")

                self.success("✅ Statut affiché")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur status")
            self.error(f"Erreur: {e}")
            return False


# ============================================================================
# CACHE COMMANDS
# ============================================================================


class CacheClearCommand(BaseCommand):
    """Vider le cache."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.cache_service: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Vider le cache."""
        try:
            cache_type = getattr(args, "type", "all")

            self.info(f"🗑️  Vidage du cache ({cache_type})...")

            if not self.cache_service:
                self.cache_service = self.adapter.get_manager("CacheService")
                if not self.cache_service:
                    self.error("CacheService non disponible")
                    return False

            result = self.cache_service.clear_cache(cache_type)

            if result:
                self.success(f"✅ Cache vidé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur clear")
            self.error(f"Erreur: {e}")
            return False


class CacheUpdateCommand(BaseCommand):
    """Mettre à jour le cache."""

    def __init__(self, context: Optional[Any] = None) -> None:
        """Initialise la commande."""
        super().__init__(context)
        self.cache_service: Optional[Any] = None
        self.adapter = get_command_adapter()

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure le parser (non utilisé pour les commandes individuelles)."""
        pass

    def execute(self, args: argparse.Namespace) -> bool:
        """Mettre à jour le cache."""
        try:
            cache_type = getattr(args, "type", "all")

            self.info(f"🔄 Mise à jour du cache ({cache_type})...")

            if not self.cache_service:
                self.cache_service = self.adapter.get_manager("CacheService")
                if not self.cache_service:
                    self.error("CacheService non disponible")
                    return False

            result = self.cache_service.update_cache(cache_type)

            if result:
                self.success(f"✅ Cache mis à jour")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur update")
            self.error(f"Erreur: {e}")
            return False
