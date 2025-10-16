"""Commande de gestion du cache."""

import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from loguru import logger

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter
from cli.context import Context

# Constantes de description simplifiÃ©es
CACHE_DESCRIPTION = "GÃ©rer le cache de la CLI"
CLEAR_HELP = "Vider le cache"
REFRESH_HELP = "Actualiser le cache"
SHOW_HELP = "Afficher le contenu du cache"
STATUS_HELP = "Afficher l'Ã©tat du cache"


class CacheCommand(BaseCommand):
    """Commande cache : gestion du cache local (status, refresh, clean, clear)."""

    def __init__(self, context: Context):
        super().__init__(context)
        self.category = "cache"

    def setup_parser(self, parser: ArgumentParser) -> None:
        """Configure le parser pour cache."""
        # Utiliser le formatter universel pour l'aide simplifiÃ©e
        parser.formatter_class = UniversalHelpFormatter

        # Description simplifiÃ©e
        parser.description = CACHE_DESCRIPTION

        subparsers = parser.add_subparsers(dest="action", help="Actions de gestion du cache", required=True)

        # cache status
        subparsers.add_parser(
            "status",
            help="Afficher statistiques cache",
            description=STATUS_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )

        # cache refresh
        refresh_parser = subparsers.add_parser(
            "refresh",
            help="Forcer resynchronisation",
            description=REFRESH_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        refresh_parser.add_argument(
            "--category",
            dest="refresh_category",
            choices=["devices", "smart_home", "alarms_and_reminders", "all"],
            default="all",
            help="CatÃ©gorie Ã  resynchroniser (dÃ©faut: all)",
        )

        # cache clear
        subparsers.add_parser(
            "clear",
            help="Supprimer tout le cache",
            description=CLEAR_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )

        # cache show
        show_parser = subparsers.add_parser(
            "show",
            help="Afficher contenu JSON",
            description=SHOW_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=True,
        )
        show_parser.add_argument(
            "--category",
            dest="show_category",
            choices=["devices", "smart_home", "alarms_and_reminders", "routines", "sync_stats"],
            required=True,
            help="CatÃ©gorie Ã  afficher",
        )

    def execute(self, args: Namespace) -> bool:
        """ExÃ©cute cache status/refresh/clear."""
        if not args.action:
            print("\nCommandes cache disponibles:\n")
            print("  status   - Afficher statistiques cache")
            print("  refresh  - Forcer resynchronisation")
            print("  show     - Afficher contenu JSON d'une catÃ©gorie")
            print("  clear    - Supprimer tout le cache")
            return True

        if args.action == "status":
            self._status()
        elif args.action == "refresh":
            category = getattr(args, "refresh_category", "all")
            self._refresh(category)
        elif args.action == "show":
            category = getattr(args, "show_category", None)
            if category:
                self._show(category)
            else:
                print("\nâŒ CatÃ©gorie requise pour la commande show")
                print("   Utilisez: alexa cache show --category <category>")
        elif args.action == "clear":
            self._clear()

        return True

    def _status(self) -> None:
        """Affiche statistiques cache."""
        try:
            ctx = self.require_context()
            cache_service = ctx.cache_service
            if not cache_service:
                print("\nâŒ CacheService indisponible")
                return

            # Obtenir les vraies statistiques du CacheService
            stats = cache_service.get_stats()

            print("\nðŸ“Š Statistiques cache:\n")
            print(f"  Hits: {stats['hits']}")
            print(f"  Misses: {stats['misses']}")
            print(f"  Taux de succÃ¨s: {stats['hit_rate']:.1%}")
            print(f"  Ã‰critures: {stats['writes']}")
            print(f"  Invalidations: {stats['invalidations']}")
            print(f"  Compression: {'ActivÃ©e' if stats['compression_enabled'] else 'DÃ©sactivÃ©e'}")
            if stats["compression_enabled"]:
                print(f"  Ratio compression moyen: {stats['avg_compression_ratio']:.1f}%")
            print(f"  EntrÃ©es totales: {stats['total_entries']}")

            if stats["entries"]:
                print("\nðŸ’¾ DÃ©tail des entrÃ©es:\n")
                for entry in stats["entries"]:
                    status = "âœ… Valide" if not entry["expired"] else "âŒ ExpirÃ©"
                    key_part = f"  {entry['key']:15} {entry['size_bytes']:>8} octets"
                    time_part = f"  {entry['expires_in_seconds']:>6}s  {status}"
                    print(key_part + time_part)

            # Statistiques de synchronisation si disponibles
            sync_stats_file = Path("data/cache/sync_stats.json")
            if sync_stats_file.exists():
                try:
                    with open(sync_stats_file) as f:
                        sync_stats = json.load(f)
                    print("\nï¿½ Statistiques synchronisation:\n")
                    print(f"  DerniÃ¨re sync: {sync_stats.get('timestamp', 'N/A')}")
                    print(f"  DurÃ©e: {sync_stats.get('duration_seconds', 0):.2f}s")
                    if "synced" in sync_stats:
                        for category, count in sync_stats["synced"].items():
                            print(f"  {category.capitalize()}: {count}")
                except Exception as e:
                    logger.debug(f"Erreur lecture sync_stats: {e}")

        except Exception as e:
            logger.error(f"Erreur lecture stats: {e}")
            print(f"\nâŒ Erreur: {e}")

    def _refresh(self, category: str) -> None:
        """Force resynchronisation."""
        try:
            ctx = self.require_context()
            if not ctx.auth:
                print("\nâŒ Authentification requise pour la synchronisation")
                print("   Utilisez 'alexa auth create' d'abord")
                return

            if not ctx.sync_service:
                print("\nâŒ SyncService indisponible")
                return

            print(f"\nðŸ”„ Resynchronisation {category}...\n")

            result = None
            if category == "all":
                result = ctx.sync_service.sync_all()
            elif category == "devices":
                devices = ctx.sync_service._sync_alexa_devices()
                result = {"success": True, "count": len(devices)}
            elif category == "smart_home":
                smart = ctx.sync_service._sync_smart_home_devices()
                result = {"success": True, "count": len(smart)}
            elif category == "alarms_and_reminders":
                notifs = ctx.sync_service._sync_notifications()
                result = {"success": True, "count": len(notifs)}
            else:
                print(f"\nâŒ CatÃ©gorie '{category}' non reconnue")
                return

            print("\nâœ… Synchronisation terminÃ©e")
            if result and "duration_seconds" in result:
                print(f"   DurÃ©e: {result.get('duration_seconds', 0):.2f}s")

        except Exception as e:
            logger.error(f"Erreur refresh: {e}")
            print(f"\nâŒ Erreur: {e}")

    def _clear(self) -> None:
        """Supprime tout le cache sauf les donnÃ©es d'authentification."""
        try:
            ctx = self.require_context()
            cache_service = ctx.cache_service
            if not cache_service:
                print("\nâŒ CacheService indisponible")
                return

            print("\nðŸ—‘ï¸  Suppression cache (prÃ©servation des donnÃ©es d'authentification)...")
            count = cache_service.clear_all_except(preserve_keys=["auth_data"])
            print(f"âœ… {count} entrÃ©e(s) supprimÃ©e(s), donnÃ©es d'authentification prÃ©servÃ©es")

        except Exception as e:
            logger.error(f"Erreur clear: {e}")
            print(f"\nâŒ Erreur: {e}")

    def _show(self, category: str) -> None:
        """Affiche le contenu JSON d'une catÃ©gorie de cache."""
        try:
            ctx = self.require_context()
            cache_service = ctx.cache_service
            if not cache_service:
                print("\nâŒ CacheService indisponible")
                return

            print(f"\nðŸ“„ Contenu JSON de la catÃ©gorie '{category}':\n")

            # RÃ©cupÃ©rer les donnÃ©es du cache
            data = cache_service.get(category)
            if data is None:
                print(f"âŒ Aucune donnÃ©e trouvÃ©e pour la catÃ©gorie '{category}'")
                return

            # Afficher le JSON formatÃ©
            print(json.dumps(data, indent=2, ensure_ascii=False))

        except Exception as e:
            logger.error(f"Erreur show: {e}")
            print(f"\nâŒ Erreur: {e}")

