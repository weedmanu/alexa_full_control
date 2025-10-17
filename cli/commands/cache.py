"""Commande de gestion du cache."""

import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from loguru import logger

from cli.base_command import BaseCommand
from cli.command_parser import ActionHelpFormatter, UniversalHelpFormatter
from cli.context import Context

# Constantes de description simplifi…es
CACHE_DESCRIPTION = "G…rer le cache de la CLI"
CLEAR_HELP = "Vider le cache"
REFRESH_HELP = "Actualiser le cache"
SHOW_HELP = "Afficher le contenu du cache"
STATUS_HELP = "Afficher l'…tat du cache"


class CacheCommand(BaseCommand):
    """Commande cache : gestion du cache local (status, refresh, clean, clear)."""

    def __init__(self, context: Context):
        super().__init__(context)
        self.category = "cache"

    def setup_parser(self, parser: ArgumentParser) -> None:
        """Configure le parser pour cache."""
        # Utiliser le formatter universel pour l'aide simplifi…e
        parser.formatter_class = UniversalHelpFormatter

        # Description simplifi…e
        parser.description = CACHE_DESCRIPTION

        subparsers = parser.add_subparsers(dest="action", help="Actions de gestion du cache", required=True)

        # cache status
        subparsers.add_parser(
            "status",
            help="Afficher statistiques cache",
            description=STATUS_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # cache refresh
        refresh_parser = subparsers.add_parser(
            "refresh",
            help="Forcer resynchronisation",
            description=REFRESH_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        refresh_parser.add_argument(
            "--category",
            dest="refresh_category",
            choices=["devices", "smart_home", "alarms_and_reminders", "all"],
            default="all",
            help="Cat…gorie … resynchroniser (d…faut: all)",
        )

        # cache clear
        subparsers.add_parser(
            "clear",
            help="Supprimer tout le cache",
            description=CLEAR_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )

        # cache show
        show_parser = subparsers.add_parser(
            "show",
            help="Afficher contenu JSON",
            description=SHOW_HELP,
            formatter_class=ActionHelpFormatter,
            add_help=False,
        )
        show_parser.add_argument(
            "--category",
            dest="show_category",
            choices=["devices", "smart_home", "alarms_and_reminders", "routines", "sync_stats"],
            required=True,
            help="Cat…gorie … afficher",
        )

    def execute(self, args: Namespace) -> bool:
        """Ex…cute cache status/refresh/clear."""
        if not args.action:
            print("\nCommandes cache disponibles:\n")
            print("  status   - Afficher statistiques cache")
            print("  refresh  - Forcer resynchronisation")
            print("  show     - Afficher contenu JSON d'une cat…gorie")
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
                print("\n? Cat…gorie requise pour la commande show")
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
                print("\n? CacheService indisponible")
                return

            # Obtenir les vraies statistiques du CacheService
            stats = cache_service.get_stats()

            print("\n?? Statistiques cache:\n")
            print(f"  Hits: {stats['hits']}")
            print(f"  Misses: {stats['misses']}")
            print(f"  Taux de succ…s: {stats['hit_rate']:.1%}")
            print(f"  …critures: {stats['writes']}")
            print(f"  Invalidations: {stats['invalidations']}")
            print(f"  Compression: {'Activ…e' if stats['compression_enabled'] else 'D…sactiv…e'}")
            if stats["compression_enabled"]:
                print(f"  Ratio compression moyen: {stats['avg_compression_ratio']:.1f}%")
            print(f"  Entr…es totales: {stats['total_entries']}")

            if stats["entries"]:
                print("\n?? D…tail des entr…es:\n")
                for entry in stats["entries"]:
                    status = "? Valide" if not entry["expired"] else "? Expir…"
                    key_part = f"  {entry['key']:15} {entry['size_bytes']:>8} octets"
                    time_part = f"  {entry['expires_in_seconds']:>6}s  {status}"
                    print(key_part + time_part)

            # Statistiques de synchronisation si disponibles
            sync_stats_file = Path("data/cache/sync_stats.json")
            if sync_stats_file.exists():
                try:
                    with open(sync_stats_file) as f:
                        sync_stats = json.load(f)
                    print("\n? Statistiques synchronisation:\n")
                    print(f"  Derni…re sync: {sync_stats.get('timestamp', 'N/A')}")
                    print(f"  Dur…e: {sync_stats.get('duration_seconds', 0):.2f}s")
                    if "synced" in sync_stats:
                        for category, count in sync_stats["synced"].items():
                            print(f"  {category.capitalize()}: {count}")
                except Exception as e:
                    logger.debug(f"Erreur lecture sync_stats: {e}")

        except Exception as e:
            logger.error(f"Erreur lecture stats: {e}")
            print(f"\n? Erreur: {e}")

    def _refresh(self, category: str) -> None:
        """Force resynchronisation."""
        try:
            ctx = self.require_context()
            if not ctx.auth:
                print("\n? Authentification requise pour la synchronisation")
                print("   Utilisez 'alexa auth create' d'abord")
                return

            if not ctx.sync_service:
                print("\n? SyncService indisponible")
                return

            print(f"\n?? Resynchronisation {category}...\n")

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
                print(f"\n? Cat…gorie '{category}' non reconnue")
                return

            print("\n? Synchronisation termin…e")
            if result and "duration_seconds" in result:
                print(f"   Dur…e: {result.get('duration_seconds', 0):.2f}s")

        except Exception as e:
            logger.error(f"Erreur refresh: {e}")
            print(f"\n? Erreur: {e}")

    def _clear(self) -> None:
        """Supprime tout le cache sauf les donn…es d'authentification."""
        try:
            ctx = self.require_context()
            cache_service = ctx.cache_service
            if not cache_service:
                print("\n? CacheService indisponible")
                return

            print("\n???  Suppression cache (pr…servation des donn…es d'authentification)...")
            count = cache_service.clear_all_except(preserve_keys=["auth_data"])
            print(f"? {count} entr…e(s) supprim…e(s), donn…es d'authentification pr…serv…es")

        except Exception as e:
            logger.error(f"Erreur clear: {e}")
            print(f"\n? Erreur: {e}")

    def _show(self, category: str) -> None:
        """Affiche le contenu JSON d'une cat…gorie de cache."""
        try:
            ctx = self.require_context()
            cache_service = ctx.cache_service
            if not cache_service:
                print("\n? CacheService indisponible")
                return

            print(f"\n?? Contenu JSON de la cat…gorie '{category}':\n")

            # R…cup…rer les donn…es du cache
            data = cache_service.get(category)
            if data is None:
                print(f"? Aucune donn…e trouv…e pour la cat…gorie '{category}'")
                return

            # Afficher le JSON format…
            print(json.dumps(data, indent=2, ensure_ascii=False))

        except Exception as e:
            logger.error(f"Erreur show: {e}")
            print(f"\n? Erreur: {e}")
