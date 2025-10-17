"""
Classe de base abstraite pour toutes les commandes CLI.

Ce module définit le contrat que toutes les commandes doivent respecter,
fournit des utilitaires communs, et encapsule la logique partagée.

Auteur: M@nu
Date: 7 octobre 2025
"""

import argparse
import json
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Optional

from loguru import logger

from utils.logger import SharedIcons


class BaseCommand(ABC):
    """
    Classe abstraite de base pour toutes les commandes CLI.

    Toutes les commandes spécifiques (DeviceCommand, MusicCommand, etc.)
    doivent hériter de cette classe et implémenter les méthodes abstraites.

    Architecture:
        - setup_parser(): Configure le sous-parser argparse pour la commande
        - execute(): Exécute la logique de la commande

    Attributes:
        context: Contexte partagé (auth, config, state_machine, managers)
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
                    Peut être None lors de l'initialisation temporaire pour setup_parser()
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

        Cette méthode doit créer les sous-parsers (actions) et définir
        tous les arguments spécifiques à cette catégorie de commandes.

        Args:
            parser: Sous-parser argparse pour cette catégorie

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
        Exécute la commande avec les arguments parsés.

        Cette méthode doit:
        1. Vérifier l'état de connexion (state_machine)
        2. Router vers la bonne action selon args.action
        3. Appeler les managers appropriés
        4. Gérer les erreurs proprement
        5. Retourner True si succès, False sinon

        Args:
            args: Arguments parsés par argparse

        Returns:
            True si la commande a réussi, False sinon

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
    # MÉTHODES UTILITAIRES COMMUNES
    # ========================================================================

    def setup_common_parser_config(self, parser: argparse.ArgumentParser, description: str) -> Any:
        """
        Configure les paramètres communs du parser pour une catégorie de commandes.

        Args:
            parser: Parser de la catégorie
            description: Description de la catégorie

        Returns:
            Sous-parsers action pour ajouter les actions spécifiques
        """
        # Utiliser le formatter universel pour l'ordre exact demandé
        from cli.command_parser import UniversalHelpFormatter

        parser.formatter_class = UniversalHelpFormatter

        # Supprimer la ligne d'usage automatique
        parser.usage = argparse.SUPPRESS

        # Description
        parser.description = description

        # Créer les sous-parsers
        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        return subparsers

    def add_device_argument(self, parser: argparse.ArgumentParser, required: bool = True) -> None:
        """
        Ajoute l'argument --device/-d à un parser.

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
        Ajoute l'argument --json à un parser.
        """
        parser.add_argument(
            "--json",
            action="store_true",
            help="Afficher les données au format JSON",
        )

    def add_refresh_argument(self, parser: argparse.ArgumentParser) -> None:
        """
        Ajoute l'argument --refresh à un parser.
        """
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Forcer la resynchronisation avant d'afficher",
        )

    def add_filter_argument(self, parser: argparse.ArgumentParser) -> None:
        """
        Ajoute l'argument --filter à un parser.
        """
        parser.add_argument(
            "--filter",
            type=str,
            metavar="PATTERN",
            help="Filtrer par nom (recherche partielle)",
        )

    def create_action_parser(
        self,
        subparsers: Any,
        action_name: str,
        help_text: str,
        description: str = "",
        add_help: bool = False,
    ) -> argparse.ArgumentParser:
        """
        Crée un parser d'action standardisé.

        Args:
            subparsers: Sous-parsers action
            action_name: Nom de l'action
            help_text: Texte d'aide court
            description: Description détaillée
            add_help: Si ajouter l'aide automatique

        Returns:
            Parser configuré pour l'action
        """
        from cli.command_parser import ActionHelpFormatter

        return subparsers.add_parser(
            action_name,
            help=help_text,
            description=description,
            formatter_class=ActionHelpFormatter,
            add_help=add_help,
        )

    def validate_device_arg(self, args: argparse.Namespace) -> Optional[tuple[str, str]]:
        """
        Valide et résout l'argument device.

        Args:
            args: Arguments parsés contenant device

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
        Appelle une méthode sur un manager avec gestion d'erreur centralisée.

        Args:
            manager_name: Nom du manager (ex: 'alarm_mgr', 'device_mgr')
            method_name: Nom de la méthode à appeler
            *args: Arguments positionnels
            **kwargs: Arguments nommés

        Returns:
            Résultat de la méthode ou None si erreur

        Example:
            >>> result = self.call_manager_method('alarm_mgr', 'create_alarm',
            ...                                   device_serial, device_type, time_str)
        """
        # Obtenir le manager depuis le contexte
        manager = getattr(self.context, manager_name, None) if self.context else None

        if not manager:
            self.error(f"Manager '{manager_name}' non disponible")
            return None

        # Obtenir la méthode
        method = getattr(manager, method_name, None)
        if not method:
            self.error(f"Méthode '{method_name}' non trouvée sur {manager_name}")
            return None

        # Appeler la méthode avec gestion d'erreur
        try:
            result = method(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Erreur lors de l'appel {manager_name}.{method_name}: {e}")
            self.error(f"Erreur {manager_name}: {e}")
            return None

    def validate_connection(self) -> bool:
        """
        Vérifie que la connexion à l'API Alexa est établie.

        Utilise la state machine pour valider l'état de connexion.
        Affiche un message d'erreur si non connecté.

        Returns:
            True si connecté, False sinon
        """
        if not self.state_machine:
            self.logger.error("State machine non initialise")
            self.error("Erreur interne: state machine manquante")
            return False

        if not self.state_machine.can_execute_commands:
            self.logger.warning("Tentative d'excution sans connexion tablie")
            self.error("Authentification non initialisée. Utilisez 'alexa auth create' pour vous connecter.")
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
        Exécute une fonction avec protection du circuit breaker.

        Encapsule l'appel dans le circuit breaker pour éviter les cascades
        d'erreurs en cas de problème API.

        Args:
            func: Fonction à appeler
            *args: Arguments positionnels
            **kwargs: Arguments nommés

        Returns:
            Résultat de func() ou None si erreur

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
        Affiche les données en format texte ou JSON.

        Args:
            data: Données à afficher (dict, list, str, etc.)
            json_mode: Si True, sortie JSON, sinon texte formaté
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
        Affiche un message de succès.

        Args:
            message: Message à afficher
        """
        self.logger.success(message)
        print(f"\033[1;32m✅ {message}\033[0m")

    def error(self, message: str) -> None:
        """
        Affiche un message d'erreur.

        Args:
            message: Message d'erreur
        """
        self.logger.error(message)
        print(f"\033[1;31m❌ {message}\033[0m", file=sys.stderr)

    def warning(self, message: str) -> None:
        """
        Affiche un avertissement.

        Args:
            message: Message d'avertissement
        """
        self.logger.warning(message)
        print(f"\033[1;33m⚠️  {message}\033[0m")

    def info(self, message: str) -> None:
        """
        Affiche un message d'information.

        Args:
            message: Message d'information
        """
        self.logger.info(message)
        print(f"\033[1;34mℹ️  {message}\033[0m", flush=True)

    def get_device_serial(self, device_name: str) -> Optional[str]:
        """
        Récupère le serial d'un appareil depuis son nom.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Serial de l'appareil ou None si non trouvé
        """
        if not self.device_mgr:
            self.error("Gestionnaire d'appareils non disponible")
            return None

        try:
            devices = self.device_mgr.get_devices()
            for device in devices:
                if device.get("accountName") == device_name:
                    return device.get("serialNumber")

            self.error(f"Appareil '{device_name}' non trouvé")
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'appareil: {e}")
            self.error(f"Impossible de trouver l'appareil: {e}")
            return None

    def get_device_serial_and_type(self, device_name: str) -> Optional[tuple[str, str]]:
        """
        Récupère le serial et le type d'un appareil depuis son nom.

        Args:
            device_name: Nom de l'appareil

        Returns:
            Tuple (serial, device_type) ou None si non trouvé
        """
        if not self.device_mgr:
            self.error("Gestionnaire d'appareils non disponible")
            return None

        try:
            devices = self.device_mgr.get_devices()
            for device in devices:
                if device.get("accountName") == device_name:
                    serial = device.get("serialNumber")
                    device_type = device.get("deviceType")
                    if serial and device_type:
                        return (serial, device_type)

            self.error(f"Appareil '{device_name}' non trouvé")
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'appareil: {e}")
            self.error(f"Impossible de trouver l'appareil: {e}")
            return None

    def validate_required_args(self, args: argparse.Namespace, *required_fields: str) -> bool:
        """
        Valide que les arguments requis sont présents.

        Args:
            args: Arguments parsés
            *required_fields: Noms des champs requis

        Returns:
            True si tous les champs requis sont présents, False sinon

        Example:
            >>> if not self.validate_required_args(args, 'device', 'duration'):
            ...     return False
        """
        for field in required_fields:
            if not hasattr(args, field) or getattr(args, field) is None:
                self.error(f"Argument requis manquant: --{field.replace('_', '-')}")
                return False
        return True

    def validate_manager_available(self, manager_name: str) -> bool:
        """
        Valide qu'un manager est disponible dans le contexte.

        Args:
            manager_name: Nom du manager à vérifier (ex: 'alarm_mgr', 'device_mgr')

        Returns:
            True si le manager est disponible, False sinon

        Example:
            >>> if not self.validate_manager_available('alarm_mgr'):
            ...     return False
        """
        manager = getattr(self.context, manager_name, None) if self.context else None
        if not manager:
            self.error(f"Manager '{manager_name}' non disponible. Vérifiez la connexion.")
            return False
        return True

    def format_table(self, data: list[list[Any]], headers: list[str]) -> str:
        """
        Formate des données en tableau texte avec couleurs.

        Args:
            data: Liste de listes/tuples (lignes du tableau)
            headers: Liste des en-têtes de colonnes

        Returns:
            Chaîne formatée comme tableau coloré

        Example:
            >>> table = self.format_table(
            ...     [['Echo Salon', 'online'], ['Echo Chambre', 'offline']],
            ...     ['Appareil', 'État']
            ... )
        """
        if not data:
            return "\033[1;33mAucune donnée\033[0m"

        # Fonction pour calculer la longueur visible (sans codes ANSI)
        def visible_length(text: str) -> int:
            import re

            # Supprimer les codes ANSI
            ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            return len(ansi_escape.sub("", text))

        # Calculer largeurs colonnes basées sur la longueur visible
        col_widths = [visible_length(str(h)) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], visible_length(str(cell)))

        # Construire tableau
        lines: list[str] = []

        # En-tête avec couleur
        header_parts: list[str] = []
        for i, h in enumerate(headers):
            header_parts.append(f"\033[1;36m{str(h).ljust(col_widths[i])}\033[0m")
        header_line = "\033[1;36m │ \033[0m".join(header_parts)
        lines.append(header_line)

        # Séparateur avec la bonne longueur
        separator_length = sum(col_widths) + 3 * (len(headers) - 1)  # 3 = len(" │ ")
        lines.append("\033[1;36m" + "─" * separator_length + "\033[0m")

        # Données
        for row in data:
            line_parts: list[str] = []
            for i, cell in enumerate(row):
                cell_str = str(cell)
                # Colorer certaines valeurs spéciales
                if cell_str in ["🟢 En ligne", "online", "Online"]:
                    cell_str = f"\033[1;32m{cell_str}\033[0m"
                elif cell_str in ["🔴 Hors ligne", "offline", "Offline"]:
                    cell_str = f"\033[1;31m{cell_str}\033[0m"
                elif "Echo Show" in cell_str:
                    cell_str = f"\033[1;35m{cell_str}\033[0m"
                elif "Echo Dot" in cell_str or "PC Voice" in cell_str:
                    cell_str = f"\033[1;34m{cell_str}\033[0m"
                # Ajuster le padding pour aligner correctement
                visible_len = visible_length(cell_str)
                padding = col_widths[i] - visible_len
                line_parts.append(cell_str + " " * padding)
            lines.append(" │ ".join(line_parts))

        return "\n".join(lines)

    # ========================================================================
    # MÉTHODES DE LOGGING STANDARDISÉES AVEC SHAREDICONS
    # ========================================================================

    def log_operation_start(self, operation: str, *args: Any) -> None:
        """
        Log le début d'une opération avec icône standardisée.

        Args:
            operation: Nom de l'opération (ex: "synchronisation", "recherche")
            *args: Arguments supplémentaires pour le message
        """
        message = f"{operation}"
        if args:
            message += f" {', '.join(str(arg) for arg in args)}"
        self.logger.info(f"{SharedIcons.SEARCH} {message}...")

    def log_operation_success(self, operation: str, count: Optional[int] = None, details: str = "") -> None:
        """
        Log le succès d'une opération avec icône standardisée.

        Args:
            operation: Nom de l'opération
            count: Nombre d'éléments traités (optionnel)
            details: Détails supplémentaires
        """
        message = f"{operation}"
        if count is not None:
            message += f" {count} élément(s)"
        if details:
            message += f" {details}"
        self.logger.success(f"{SharedIcons.SUCCESS} {message}")

    def log_operation_error(self, operation: str, error: Exception) -> None:
        """
        Log une erreur d'opération avec icône standardisée.

        Args:
            operation: Nom de l'opération
            error: Exception levée
        """
        self.logger.error(f"{SharedIcons.ERROR} Erreur {operation}: {error}")

    def log_cache_hit(self, cache_type: str, key: str, count: Optional[int] = None) -> None:
        """
        Log un hit de cache avec icône standardisée.

        Args:
            cache_type: Type de cache ("mémoire", "disque")
            key: Clé du cache
            count: Nombre d'éléments (optionnel)
        """
        count_str = f" {count} élément(s)" if count is not None else ""
        self.logger.debug(f"{SharedIcons.SAVE} Cache {cache_type}: {key}{count_str}")

    def log_data_retrieved(self, data_type: str, count: int, cached: bool = True) -> None:
        """
        Log la récupération de données avec icône standardisée.

        Args:
            data_type: Type de données (ex: "alarme", "timer", "appareil")
            count: Nombre d'éléments récupérés
            cached: Si les données viennent du cache
        """
        cache_info = " (cache)" if cached else ""
        self.logger.info(f"{SharedIcons.SUCCESS} {count} {data_type}(s) récupéré(s){cache_info}")

    def log_item_created(self, item_type: str, identifier: str, target: Optional[str] = None) -> None:
        """
        Log la création d'un élément avec icône standardisée.

        Args:
            item_type: Type d'élément (ex: "alarme", "timer", "rappel")
            identifier: Identifiant de l'élément
            target: Cible de l'opération (optionnel)
        """
        target_str = f" pour {target}" if target else ""
        self.logger.success(f"{SharedIcons.SUCCESS} {item_type} '{identifier}' créé{target_str}")

    def log_item_deleted(self, item_type: str, identifier: str) -> None:
        """
        Log la suppression d'un élément avec icône standardisée.

        Args:
            item_type: Type d'élément
            identifier: Identifiant de l'élément
        """
        self.logger.success(f"{SharedIcons.TRASH} {item_type} {identifier} supprimé")

    def log_item_modified(self, item_type: str, identifier: str, action: str = "modifié") -> None:
        """
        Log la modification d'un élément avec icône standardisée.

        Args:
            item_type: Type d'élément
            identifier: Identifiant de l'élément
            action: Action effectuée (ex: "modifié", "activé", "désactivé")
        """
        self.logger.success(f"{SharedIcons.GEAR} {item_type} {identifier} {action}")

    def log_service_initialized(self, service_name: str) -> None:
        """
        Log l'initialisation d'un service avec icône standardisée.

        Args:
            service_name: Nom du service
        """
        self.logger.info(f"{SharedIcons.GEAR} {service_name} initialisé")

    def log_sync_started(self, sync_type: str = "données") -> None:
        """
        Log le début d'une synchronisation avec icône standardisée.

        Args:
            sync_type: Type de synchronisation
        """
        self.logger.info(f"{SharedIcons.SYNC} Démarrage synchronisation {sync_type}...")

    def log_sync_completed(self, sync_type: str, count: int, duration: float) -> None:
        """
        Log la fin d'une synchronisation avec icône standardisée.

        Args:
            sync_type: Type de synchronisation
            count: Nombre d'éléments synchronisés
            duration: Durée en secondes
        """
        self.logger.success(
            f"{SharedIcons.CELEBRATION} Synchronisation {sync_type} terminée: " f"{count} éléments en {duration:.1f}s"
        )

    def log_device_found(self, device_name: str, device_type: Optional[str] = None) -> None:
        """
        Log la découverte d'un appareil avec icône standardisée.

        Args:
            device_name: Nom de l'appareil
            device_type: Type d'appareil (optionnel)
        """
        type_str = f" ({device_type})" if device_type else ""
        self.logger.info(f"{SharedIcons.DEVICE} Appareil trouvé: {device_name}{type_str}")

    def log_music_action(self, action: str, track_info: str, device: str) -> None:
        """
        Log une action musicale avec icône standardisée.

        Args:
            action: Action effectuée (ex: "lancé", "arrêté")
            track_info: Informations sur la piste
            device: Appareil cible
        """
        self.logger.success(f"{SharedIcons.MUSIC} {track_info} {action} sur {device}")


class CommandError(Exception):
    """
    Exception levée lors d'erreurs de commande.

    Permet de distinguer les erreurs de commande des autres exceptions.
    """

    pass
