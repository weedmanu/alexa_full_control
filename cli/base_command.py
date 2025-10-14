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
from typing import Any, Optional

from loguru import logger


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
        self.context = context
        self.logger = logger.bind(command=self.__class__.__name__)

        # Attributs de commodité (None si context est None)
        self.auth = context.auth if context else None
        self.config = context.config if context else None
        self.state_machine = context.state_machine if context else None
        self.device_mgr = context.device_mgr if context else None
        self.breaker = context.breaker if context else None

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

    def validate_connection(self) -> bool:
        """
        Vérifie que la connexion à l'API Alexa est établie.

        Utilise la state machine pour valider l'état de connexion.
        Affiche un message d'erreur si non connecté.

        Returns:
            True si connecté, False sinon
        """
        if not self.state_machine:
            self.logger.error("State machine non initialisée")
            self.error("Erreur interne: state machine manquante")
            return False

        if not self.state_machine.can_execute_commands:
            self.logger.warning("Tentative d'exécution sans connexion établie")
            self.error(
                "Authentification non initialisée. "
                "Utilisez 'alexa auth login' pour vous connecter."
            )
            return False

        return True

    def call_with_breaker(self, func, *args, **kwargs) -> Optional[Any]:
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

    def format_table(self, data: list, headers: list) -> str:
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
        lines = []

        # En-tête avec couleur
        header_parts = []
        for i, h in enumerate(headers):
            header_parts.append(f"\033[1;36m{str(h).ljust(col_widths[i])}\033[0m")
        header_line = "\033[1;36m │ \033[0m".join(header_parts)
        lines.append(header_line)

        # Séparateur avec la bonne longueur
        separator_length = sum(col_widths) + 3 * (len(headers) - 1)  # 3 = len(" │ ")
        lines.append("\033[1;36m" + "─" * separator_length + "\033[0m")

        # Données
        for row in data:
            line_parts = []
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


class CommandError(Exception):
    """
    Exception levée lors d'erreurs de commande.

    Permet de distinguer les erreurs de commande des autres exceptions.
    """

    pass
