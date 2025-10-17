"""Commande de gestion des groupes multiroom Alexa.

Ce module fournit une interface CLI pour gérer les groupes multi-pièces :
- Lister les groupes existants
- Créer un nouveau groupe
- Supprimer un groupe
- Obtenir des informations sur un groupe
"""

import argparse

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter

# Constantes de description simplifiées
MULTIROOM_DESCRIPTION = "Gérer les groupes multiroom Alexa"
CREATE_HELP = "Créer un nouveau groupe"
DELETE_HELP = "Supprimer un groupe"
INFO_HELP = "Obtenir des informations sur un groupe"
LIST_HELP = "Lister les groupes existants"


class MultiroomCommand(BaseCommand):
    """
    Commande pour gérer les groupes multiroom (multi-pièces) Alexa.

    Les groupes multiroom permettent de synchroniser la lecture audio
    sur plusieurs appareils Echo simultanément.

    Exemples:
        >>> # Lister tous les groupes
        >>> alexa multiroom list

        >>> # Créer un groupe
        >>> alexa multiroom create --name "Maison" --devices "Salon,Chambre,Cuisine"

        >>> # Voir détails d'un groupe
        >>> alexa multiroom info --name "Maison"

        >>> # Supprimer un groupe
        >>> alexa multiroom delete --name "Maison"
    """

    def get_name(self) -> str:
        """Retourne le nom de la commande."""
        return "multiroom"

    def get_help(self) -> str:
        """Retourne l'aide de la commande."""
        return "Gérer les groupes multiroom (multi-pièces)"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure le parser pour la commande multiroom.

        Args:
            parser: Parser à configurer
        """
        # Utiliser le formatter universel pour l'aide simplifiée
        parser.formatter_class = UniversalHelpFormatter

        # Description simplifiée
        parser.description = MULTIROOM_DESCRIPTION

        subparsers = parser.add_subparsers(
            dest="action",
            metavar="ACTION",
            help="Action à exécuter",
            required=True,
        )

        # Action: list
        subparsers.add_parser(
            "list",
            help="Lister groupes",
            description=LIST_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # Action: create
        create_parser = subparsers.add_parser(
            "create",
            help="Créer groupe",
            description=CREATE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        create_parser.add_argument(
            "--name", type=str, required=True, metavar="GROUP_NAME", help="Nom du groupe à créer"
        )
        create_parser.add_argument(
            "--devices",
            type=str,
            required=True,
            metavar="DEVICE1,DEVICE2,...",
            help="Liste des appareils séparés par des virgules",
        )
        create_parser.add_argument(
            "--primary",
            type=str,
            metavar="DEVICE_NAME",
            help="Appareil principal (optionnel, par défaut le premier)",
        )

        # Action: delete
        delete_parser = subparsers.add_parser(
            "delete",
            help="Supprimer groupe",
            description=DELETE_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        delete_parser.add_argument(
            "--name",
            type=str,
            required=True,
            metavar="GROUP_NAME",
            help="Nom du groupe à supprimer",
        )
        delete_parser.add_argument("--force", action="store_true", help="Supprimer sans confirmation")

        # Action: info
        info_parser = subparsers.add_parser(
            "info",
            help="Informations groupe",
            description=INFO_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        info_parser.add_argument("--name", type=str, required=True, metavar="GROUP_NAME", help="Nom du groupe")

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Exécute la commande multiroom.

        Args:
            args: Arguments parsés

        Returns:
            True si succès, False sinon
        """
        # Validation connexion
        if not self.validate_connection():
            return False

        if args.action == "list":
            return self._list_groups(args)
        elif args.action == "create":
            return self._create_group(args)
        elif args.action == "delete":
            return self._delete_group(args)
        elif args.action == "info":
            return self._show_group_info(args)
        else:
            self.error(f"Action '{args.action}' non reconnue")
            return False

    def _list_groups(self, args: argparse.Namespace) -> bool:
        """Lister les groupes multiroom."""
        try:
            verbose = getattr(args, "verbose", False)

            self.info("🔊 Récupération des groupes multiroom...")

            ctx = self.require_context()
            if not ctx.multiroom_mgr:
                self.error("MultiroomManager non disponible")
                return False

            groups = self.call_with_breaker(ctx.multiroom_mgr.get_groups)

            if not groups:
                self.warning("Aucun groupe multiroom trouvé")
                return True

            # Afficher les groupes
            self._display_groups(groups, verbose)
            return True

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération des groupes")
            self.error(f"Erreur: {e}")
            return False

    def _create_group(self, args: argparse.Namespace) -> bool:
        """Créer un nouveau groupe multiroom."""
        try:
            # Parser la liste des appareils
            devices = [d.strip() for d in args.devices.split(",") if d.strip()]

            if len(devices) < 2:
                self.error("Un groupe doit contenir au moins 2 appareils")
                return False

            # Appareil principal
            primary_device = getattr(args, "primary", None)
            if not primary_device:
                primary_device = devices[0]
                self.info(f"Appareil principal: {primary_device} (par défaut)")

            if primary_device not in devices:
                self.error(f"L'appareil principal '{primary_device}' doit être dans la liste des appareils")
                return False

            self.info(f"🔊 Création groupe '{args.name}' avec {len(devices)} appareil(s)...")

            ctx = self.require_context()
            if not ctx.multiroom_mgr:
                self.error("MultiroomManager non disponible")
                return False

            # Récupérer les serials des appareils
            device_serials = []
            for device_name in devices:
                serial = self.get_device_serial(device_name)
                if not serial:
                    self.error(f"Appareil '{device_name}' non trouvé")
                    return False
                device_serials.append(serial)

            # Créer le groupe (pas de device principal spécifique dans MultiRoomManager)
            result = self.call_with_breaker(ctx.multiroom_mgr.create_group, args.name, device_serials)

            if result:
                self.success(f"✅ Groupe '{args.name}' créé avec succès")
                self.info(f"   Appareils: {', '.join(devices)}")
                self.info(f"   Principal: {primary_device}")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la création du groupe")
            self.error(f"Erreur: {e}")
            return False

    def _delete_group(self, args: argparse.Namespace) -> bool:
        """Supprimer un groupe multiroom."""
        try:
            force = getattr(args, "force", False)

            # Confirmation si pas --force
            if not force:
                self.warning(f"⚠️  Vous allez supprimer le groupe '{args.name}'")
                self.info("Utilisez --force pour supprimer sans confirmation")
                return False

            self.info(f"🗑️  Suppression groupe '{args.name}'...")

            ctx = self.require_context()
            if not ctx.multiroom_mgr:
                self.error("MultiroomManager non disponible")
                return False

            result = self.call_with_breaker(ctx.multiroom_mgr.delete_group, args.name)

            if result:
                self.success(f"✅ Groupe '{args.name}' supprimé")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la suppression du groupe")
            self.error(f"Erreur: {e}")
            return False

    def _show_group_info(self, args: argparse.Namespace) -> bool:
        """Afficher les informations d'un groupe."""
        try:
            self.info(f"ℹ️  Récupération groupe '{args.name}'...")

            ctx = self.require_context()
            if not ctx.multiroom_mgr:
                self.error("MultiroomManager non disponible")
                return False

            group = self.call_with_breaker(ctx.multiroom_mgr.get_group, args.name)

            if group:
                self._display_group_details(group)
                return True

            self.error(f"Groupe '{args.name}' non trouvé")
            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la récupération du groupe")
            self.error(f"Erreur: {e}")
            return False

    def _display_groups(self, groups: list, verbose: bool = False) -> None:
        """Affiche la liste des groupes de manière formatée."""
        print(f"\n🔊 Groupes Multiroom ({len(groups)}):")
        print("=" * 80)

        # groups est un dictionnaire {normalized_name: group_data}
        if isinstance(groups, dict):
            for key, group in groups.items():
                group_name = group.get("name", "N/A")
                devices = group.get("devices", [])
                primary = group.get("primary_device", "N/A")

                print(f"\n📁 {group_name} ({len(devices)} appareil(s))")

                if verbose:
                    print(f"   Principal: {primary}")
                    print("   Appareils:")
                    for device in devices:
                        print(f"     - {device}")
                else:
                    print(f"   Appareils: {', '.join(devices)}")

    def _display_group_details(self, group: dict) -> None:
        """Affiche les détails d'un groupe de manière formatée."""
        group_name = group.get("name", "N/A")
        devices = group.get("devices", [])

        print(f"\n🔊 Groupe Multiroom: {group_name}")
        print("=" * 80)
        print(f"Nombre d'appareils: {len(devices)}")

        print("\nAppareils du groupe:")
        for device_serial in devices:
            # Les devices sont juste des serials (strings)
            print(f"  - {device_serial}")

        # Afficher les dates
        created = group.get("created", "N/A")
        modified = group.get("modified", "N/A")
        print(f"\nCréé: {created}")
        if modified and modified != "N/A":
            print(f"Modifié: {modified}")
