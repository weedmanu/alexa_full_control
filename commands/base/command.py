"""
Classe de base abstraite pour toutes les commandes CLI.

Ce module d�finit le contrat que toutes les commandes doivent respecter,
fournit des utilitaires communs, et encapsule la logique partag�e.

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from loguru import logger

from utils.logger import SharedIcons


@runtime_checkable
class SubParsersActionProtocol(Protocol):
    """Minimal protocol for argparse subparsers used by commands.

    We only expose add_parser which is the part callers rely on.
    """

    def add_parser(self, name: str, *args: Any, **kwargs: Any) -> argparse.ArgumentParser:  # pragma: no cover - simple protocol
        ...


class BaseCommand(ABC):
    """
    Classe abstraite de base pour toutes les commandes CLI.

    Toutes les commandes sp�cifiques (DeviceCommand, MusicCommand, etc.)
    doivent h�riter de cette classe et impl�menter les m�thodes abstraites.

    Architecture:
        - setup_parser(): Configure le sous-parser argparse pour la commande
        - execute(): Ex�cute la logique de la commande

    Attributes:
        context: Contexte partag� (auth, config, state_machine, managers)
        logger: Logger loguru pour cette commande

    Example:
        >>> class DeviceCommand(BaseCommand):
        ...     def setup_parser(self, parser):
        ...         subparsers = parser.add_subparsers(dest='action')
        ...         list_parser = subparsers.add_parser('list')
        ...
        ...     def execute(self, args):
        ...         if args.action == 'list':
        ...             return self._list_devices()
    """

    def __init__(self, context: Optional[Any] = None):
        """
        Initialise la commande avec le contexte.

        Args:
            context: Objet Context contenant auth, config, state_machine, etc.
                    Peut �tre None lors de l'initialisation temporaire pour setup_parser()
        """
        # store private reference to the shared context
        self._context = context
        self.logger = logger.bind(command=self.__class__.__name__)

        # Note: instead of copying attributes from context (which causes
        # mypy Protocol/settable conflicts when the concrete Context exposes
        # properties), we keep only the reference to context and expose
        # accessors as properties below.
        # This preserves runtime behaviour and is friendlier to static typing.
        #
        # Access via self.auth, self.device_mgr, etc. will delegate to
        # self.context when available.
        #
        # Keep a typed reference for mypy

    @abstractmethod
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser argparse pour cette commande.

        Cette m�thode doit cr�er les sous-parsers (actions) et d�finir
        tous les arguments sp�cifiques � cette cat�gorie de commandes.

        Args:
            parser: Sous-parser argparse pour cette cat�gorie

        Example:
            >>> def setup_parser(self, parser):
            ...     subparsers = parser.add_subparsers(dest='action', required=True)
            ...
            ...     # Action 'list'
            ...     list_parser = subparsers.add_parser('list', help='Lister les appareils')
            ...     list_parser.add_argument('--filter', help='Filtrer par nom')
            ...
            ...     # Action 'info'
            ...     info_parser = subparsers.add_parser('info', help='Info appareil')
            ...     info_parser.add_argument('-d', '--device', required=True)
        """
        pass

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> bool:
        """
        Ex�cute la commande avec les arguments pars�s.

        Cette m�thode doit:
        1. V�rifier l'�tat de connexion (state_machine)
        2. Router vers la bonne action selon args.action
        3. Appeler les managers appropri�s
        4. G�rer les erreurs proprement
        5. Retourner True si succ�s, False sinon

        Args:
            args: Arguments pars�s par argparse

        Returns:
            True si la commande a r�ussi, False sinon

        Example:
            >>> def execute(self, args):
            ...     if not self.validate_connection():
            ...         return False
            ...
            ...     if args.action == 'list':
            ...         return self._list_devices(args)
            ...     elif args.action == 'info':
            ...         return self._device_info(args)
            ...
            ...     return False
        """
        pass

    # ========================================================================
    # M�THODES UTILITAIRES COMMUNES
    # ========================================================================

    def setup_common_parser_config(
        self, parser: argparse.ArgumentParser, description: str
    ) -> "SubParsersActionProtocol":
        """
        Configure les param�tres communs du parser pour une cat�gorie de commandes.

        Args:
            parser: Parser de la cat�gorie
            description: Description de la cat�gorie

        Returns:
            Sous-parsers action pour ajouter les actions sp�cifiques
        """
        # Utiliser le formatter universel pour l'ordre exact demand�
        from utils.cli.command_parser import UniversalHelpFormatter

        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description
        parser.description = description

        # Cr�er les sous-parsers
        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action � ex�cuter",
            required=True,
        )
        # Return the subparsers object. We expose a small Protocol type
        # so that callers can use the returned object without importing
        # argparse internals (and to avoid mypy warnings about returning Any).
        return subparsers

    def add_device_argument(self, parser: argparse.ArgumentParser, required: bool = True) -> None:
        """
        Ajoute l'argument --device/-d � un parser.

        Args:
            parser: Parser auquel ajouter l'argument
            required: Si l'argument est requis
        """
        parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=required,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )

    def add_json_argument(self, parser: argparse.ArgumentParser) -> None:
        """
        Ajoute l'argument --json � un parser.
        """
        parser.add_argument(
            "--json",
            action="store_true",
            help="Afficher les donn�es au format JSON",
        )

    def add_refresh_argument(self, parser: argparse.ArgumentParser) -> None:
        """
        Ajoute l'argument --refresh � un parser.
        """
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Forcer la resynchronisation avant d'afficher",
        )

    def add_filter_argument(self, parser: argparse.ArgumentParser) -> None:
        """
        Ajoute l'argument --filter � un parser.
        """
        parser.add_argument(
            "--filter",
            type=str,
            metavar="PATTERN",
            help="Filtrer par nom (recherche partielle)",
        )

    def create_action_parser(
        self,
        subparsers: "SubParsersActionProtocol",
        action_name: str,
        help_text: str,
        description: str = "",
        add_help: bool = False,
    ) -> argparse.ArgumentParser:
        """
        Cr�e un parser d'action standardis�.

        Args:
            subparsers: Sous-parsers action
            action_name: Nom de l'action
            help_text: Texte d'aide court
            description: Description d�taill�e
            add_help: Si ajouter l'aide automatique

        Returns:
            Parser configur� pour l'action
        """
        from utils.cli.command_parser import ActionHelpFormatter

        return subparsers.add_parser(
            action_name,
            help=help_text,
            description=description,
            formatter_class=ActionHelpFormatter,
            add_help=add_help,
        )

    def validate_device_arg(self, args: argparse.Namespace) -> Optional[tuple[str, str]]:
        """
        Valide et r�sout l'argument device.

        Args:
            args: Arguments pars�s contenant device

        Returns:
            Tuple (serial, device_type) ou None si erreur
        """
        if not hasattr(args, "device") or not args.device:
            self.error("Nom d'appareil requis")
            return None

        device_info = self.get_device_serial_and_type(args.device)
        if not device_info:
            return None

        return device_info

    def call_manager_method(self, manager_name: str, method_name: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        """
        Appelle une m�thode sur un manager avec gestion d'erreur centralis�e.

        Args:
            manager_name: Nom du manager (ex: 'alarm_mgr', 'device_mgr')
            method_name: Nom de la m�thode � appeler
            *args: Arguments positionnels
            **kwargs: Arguments nomm�s

        Returns:
            R�sultat de la m�thode ou None si erreur

        Example:
            >>> result = self.call_manager_method('alarm_mgr', 'create_alarm',
            ...                                   device_serial, device_type, time_str)
        """
        # Obtenir le manager depuis le contexte
        manager = getattr(self.context, manager_name, None) if self.context else None

        if not manager:
            self.error(f"Manager '{manager_name}' non disponible")
            return None

        # Obtenir la m�thode
        method = getattr(manager, method_name, None)
        if not method:
            self.error(f"M�thode '{method_name}' non trouv�e sur {manager_name}")
            return None

        # Appeler la m�thode avec gestion d'erreur
        try:
            result = method(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Erreur lors de l'appel {manager_name}.{method_name}: {e}")
            self.error(f"Erreur {manager_name}: {e}")
            return None

    def validate_connection(self) -> bool:
        """
        V�rifie que la connexion � l'API Alexa est �tablie.

        Utilise la state machine pour valider l'�tat de connexion.
        Affiche un message d'erreur si non connect�.

        Returns:
            True si connect�, False sinon
        """
        if not self.state_machine:
            self.logger.error("State machine non initialise")
            self.error("Erreur interne: state machine manquante")
            return False

        if not self.state_machine.can_execute_commands:
            self.logger.warning("Tentative d'excution sans connexion tablie")
            self.error("Authentification non initialis�e. Utilisez 'alexa auth create' pour vous connecter.")
            return False

        return True

    # ------------------------------------------------------------------
    # Convenience properties that delegate to the underlying context
    # ------------------------------------------------------------------
    @property
    def context(self) -> Optional[Any]:
        return self._context

    @property
    def auth(self) -> Optional[Any]:
        return self._context.auth if self._context else None

    @property
    def config(self) -> Optional[Any]:
        return self._context.config if self._context else None

    @property
    def state_machine(self) -> Optional[Any]:
        return self._context.state_machine if self._context else None

    @property
    def device_mgr(self) -> Optional[Any]:
        return self._context.device_mgr if self._context else None

    @property
    def breaker(self) -> Optional[Any]:
        return self._context.breaker if self._context else None

    def require_context(self) -> Any:
        """Return the context or raise RuntimeError.

        Use this in command implementations when the context must be present
        (for example after authentication). This helps mypy narrow Optional
        types in command methods.
        """
        if not self._context:
            raise RuntimeError("Context is required for this operation")
        return self._context

    def call_with_breaker(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Optional[Any]:
        """
        Ex�cute une fonction avec protection du circuit breaker.

        Encapsule l'appel dans le circuit breaker pour �viter les cascades
        d'erreurs en cas de probl�me API.

        Args:
            func: Fonction � appeler
            *args: Arguments positionnels
            **kwargs: Arguments nomm�s

        Returns:
            R�sultat de func() ou None si erreur

        Example:
            >>> result = self.call_with_breaker(
            ...     self.auth.get,
            ...     '/api/devices'
            ... )
        """
        if not self.breaker:
            self.logger.warning("Circuit breaker non disponible, appel direct")
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Erreur lors de l'appel: {e}")
                return None

        try:
            return self.breaker.call(func, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Erreur circuit breaker: {e}")
            self.error(f"Erreur API: {e}")
            return None

    def output(self, data: Any, json_mode: bool = False) -> None:
        """
        Affiche les donn�es en format texte ou JSON.

        Args:
            data: Donn�es � afficher (dict, list, str, etc.)
            json_mode: Si True, sortie JSON, sinon texte format�
        """
        if json_mode:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            if isinstance(data, (dict, list)):
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(data)

    def success(self, message: str) -> None:
        """
        Affiche un message de succ�s.

        Args:
            message: Message � afficher
        """
        self.logger.success(message)
        print(f"\033[1;32m? {message}\033[0m")

    def error(self, message: str) -> None:
        """
        Affiche un message d'erreur.

        Args:
            message: Message d'erreur
        """
        self.logger.error(message)
        print(f"\033[1;31m? {message}\033[0m", file=sys.stderr)

    def warning(self, message: str) -> None:
        """
        Affiche un avertissement.

        Args:
            message: Message d'avertissement
        """
        self.logger.warning(message)
        print(f"\033[1;33m??  {message}\033[0m")

    def info(self, message: str) -> None:
        """
        Affiche un message d'information.

        Args:
            message: Message d'information
        """
        self.logger.info(message)
        print(f"\033[1;34m??  {message}\033[0m", flush=True)

    def debug(self, message: str) -> None:
        """
        Affiche un message de debug.

        Args:
            message: Message � afficher
        """
        self.logger.debug(message)

    def get_device_type(self, device_name: str) -> str:
        """
        R�cup�re le type d'appareil.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Type d'appareil (d�faut: ECHO)
        """
        if not self.device_mgr:
            return "ECHO"

        devices = self.device_mgr.get_devices()
        for device in devices:
            if device.get("accountName") == device_name:
                device_type = device.get("deviceType", "ECHO")
                return str(device_type) if device_type is not None else "ECHO"

        return "ECHO"

    def get_device_info(self, device_name: str) -> Optional[tuple[str, str]]:
        """
        R�cup�re le serial et le type d'un appareil.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Tuple (serial, device_type) ou None si non trouv�
        """
        serial = self.get_device_serial(device_name)
        if not serial:
            return None

        device_type = self.get_device_type(device_name)
        return (serial, device_type)

    def parse_duration(self, duration_str: str) -> Optional[int]:
        """
        Parse une cha�ne de dur�e en secondes.

        Formats accept�s:
        - 10m, 1h30m, 2h, 90s
        - '1 minute', '2 heures', '1 heure 30 minutes'

        Args:
            duration_str: Cha�ne de dur�e

        Returns:
            Dur�e en secondes ou None si format invalide
        """
        import re

        duration_str = duration_str.strip().lower()
        total_seconds = 0

        # Format compact: 1h30m, 10m, 2h, 90s
        compact_pattern = r"(\d+)\s*([hms])"
        matches = re.findall(compact_pattern, duration_str)

        if matches:
            for value, unit in matches:
                value = int(value)
                if unit == "h":
                    total_seconds += value * 3600
                elif unit == "m":
                    total_seconds += value * 60
                elif unit == "s":
                    total_seconds += value
            return total_seconds if total_seconds > 0 else None

        # Format texte: '1 heure 30 minutes', '2 heures', etc.
        text_pattern = r"(\d+)\s*(heure|heures|minute|minutes|seconde|secondes|h|m|s)"
        matches = re.findall(text_pattern, duration_str)

        if matches:
            for value, unit in matches:
                value = int(value)
                if unit in ["heure", "heures", "h"]:
                    total_seconds += value * 3600
                elif unit in ["minute", "minutes", "m"]:
                    total_seconds += value * 60
                elif unit in ["seconde", "secondes", "s"]:
                    total_seconds += value
            return total_seconds if total_seconds > 0 else None

        # Format num�rique pur (suppos� �tre en minutes)
        try:
            minutes = int(duration_str)
            return minutes * 60 if minutes > 0 else None
        except ValueError:
            pass

        return None

    def format_duration(self, seconds: int) -> str:
        """
        Formate une dur�e en secondes en texte lisible.

        Args:
            seconds: Dur�e en secondes

        Returns:
            Texte format� (ex: "1h 30m", "45m", "2h")
        """
        from datetime import timedelta

        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds_remainder = divmod(remainder, 60)

        parts = []
        if td.days > 0:
            parts.append(f"{td.days}j")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds_remainder > 0 and not parts:  # Afficher secondes seulement si < 1 minute
            parts.append(f"{seconds_remainder}s")

        return " ".join(parts) if parts else "0s"

    # ------------------------------------------------------------------
    # Compatibility aliases (historical names used by CLI commands)
    # ------------------------------------------------------------------
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        return self.parse_duration(duration_str)

    def _format_duration(self, seconds: int) -> str:
        return self.format_duration(seconds)

    def _get_device_type(self, device_name: str) -> str:
        return self.get_device_type(device_name)

    # ========================================================================
    # M�THODES DE LOGGING STANDARDIS�ES AVEC SHAREDICONS
    # ========================================================================

    def log_operation_start(self, operation: str, *args: Any) -> None:
        """
        Log le d�but d'une op�ration avec ic�ne standardis�e.

        Args:
            operation: Nom de l'op�ration (ex: "synchronisation", "recherche")
            *args: Arguments suppl�mentaires pour le message
        """
        message = f"{operation}"
        if args:
            message += f" {', '.join(str(arg) for arg in args)}"
        self.logger.info(f"{SharedIcons.SEARCH} {message}...")

    def log_operation_success(self, operation: str, count: Optional[int] = None, details: str = "") -> None:
        """
        Log le succ�s d'une op�ration avec ic�ne standardis�e.

        Args:
            operation: Nom de l'op�ration
            count: Nombre d'�l�ments trait�s (optionnel)
            details: D�tails suppl�mentaires
        """
        message = f"{operation}"
        if count is not None:
            message += f" {count} �l�ment(s)"
        if details:
            message += f" {details}"
        self.logger.success(f"{SharedIcons.SUCCESS} {message}")

    def log_operation_error(self, operation: str, error: Exception) -> None:
        """
        Log une erreur d'op�ration avec ic�ne standardis�e.

        Args:
            operation: Nom de l'op�ration
            error: Exception lev�e
        """
        self.logger.error(f"{SharedIcons.ERROR} Erreur {operation}: {error}")

    def log_cache_hit(self, cache_type: str, key: str, count: Optional[int] = None) -> None:
        """
        Log un hit de cache avec ic�ne standardis�e.

        Args:
            cache_type: Type de cache ("m�moire", "disque")
            key: Cl� du cache
            count: Nombre d'�l�ments (optionnel)
        """
        count_str = f" {count} �l�ment(s)" if count is not None else ""
        self.logger.debug(f"{SharedIcons.SAVE} Cache {cache_type}: {key}{count_str}")

    def log_data_retrieved(self, data_type: str, count: int, cached: bool = True) -> None:
        """
        Log la r�cup�ration de donn�es avec ic�ne standardis�e.

        Args:
            data_type: Type de donn�es (ex: "alarme", "timer", "appareil")
            count: Nombre d'�l�ments r�cup�r�s
            cached: Si les donn�es viennent du cache
        """
        cache_info = " (cache)" if cached else ""
        self.logger.info(f"{SharedIcons.SUCCESS} {count} {data_type}(s) r�cup�r�(s){cache_info}")

    def log_item_created(self, item_type: str, identifier: str, target: Optional[str] = None) -> None:
        """
        Log la cr�ation d'un �l�ment avec ic�ne standardis�e.

        Args:
            item_type: Type d'�l�ment (ex: "alarme", "timer", "rappel")
            identifier: Identifiant de l'�l�ment
            target: Cible de l'op�ration (optionnel)
        """
        target_str = f" pour {target}" if target else ""
        self.logger.success(f"{SharedIcons.SUCCESS} {item_type} '{identifier}' cr��{target_str}")

    def log_item_deleted(self, item_type: str, identifier: str) -> None:
        """
        Log la suppression d'un �l�ment avec ic�ne standardis�e.

        Args:
            item_type: Type d'�l�ment
            identifier: Identifiant de l'�l�ment
        """
        self.logger.success(f"{SharedIcons.TRASH} {item_type} {identifier} supprim�")

    def log_item_modified(self, item_type: str, identifier: str, action: str = "modifi�") -> None:
        """
        Log la modification d'un �l�ment avec ic�ne standardis�e.

        Args:
            item_type: Type d'�l�ment
            identifier: Identifiant de l'�l�ment
            action: Action effectu�e (ex: "modifi�", "activ�", "d�sactiv�")
        """
        self.logger.success(f"{SharedIcons.GEAR} {item_type} {identifier} {action}")

    def log_service_initialized(self, service_name: str) -> None:
        """
        Log l'initialisation d'un service avec ic�ne standardis�e.

        Args:
            service_name: Nom du service
        """
        self.logger.info(f"{SharedIcons.GEAR} {service_name} initialis�")

    def log_sync_started(self, sync_type: str = "donn�es") -> None:
        """
        Log le d�but d'une synchronisation avec ic�ne standardis�e.

        Args:
            sync_type: Type de synchronisation
        """
        self.logger.info(f"{SharedIcons.SYNC} D�marrage synchronisation {sync_type}...")

    def log_sync_completed(self, sync_type: str, count: int, duration: float) -> None:
        """
        Log la fin d'une synchronisation avec ic�ne standardis�e.

        Args:
            sync_type: Type de synchronisation
            count: Nombre d'�l�ments synchronis�s
            duration: Dur�e en secondes
        """
        self.logger.success(
            f"{SharedIcons.CELEBRATION} Synchronisation {sync_type} termin�e: " f"{count} �l�ments en {duration:.1f}s"
        )

    def log_device_found(self, device_name: str, device_type: Optional[str] = None) -> None:
        """
        Log la d�couverte d'un appareil avec ic�ne standardis�e.

        Args:
            device_name: Nom de l'appareil
            device_type: Type d'appareil (optionnel)
        """
        type_str = f" ({device_type})" if device_type else ""
        self.logger.info(f"{SharedIcons.DEVICE} Appareil trouv�: {device_name}{type_str}")

    def log_music_action(self, action: str, track_info: str, device: str) -> None:
        """
        Log une action musicale avec ic�ne standardis�e.

        Args:
            action: Action effectu�e (ex: "lanc�", "arr�t�")
            track_info: Informations sur la piste
            device: Appareil cible
        """
        self.logger.success(f"{SharedIcons.MUSIC} {track_info} {action} sur {device}")


class CommandError(Exception):
    """
    Exception lev�e lors d'erreurs de commande.

    Permet de distinguer les erreurs de commande des autres exceptions.
    """

    pass




