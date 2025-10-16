"""
Commandes de gestion de bibliothèque musicale.

Gère: library (imported, purchased, playlists, prime-playlists, prime-stations)
      track (library track/album)
      playlist (library, prime-asin, prime-station, prime-queue)

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse
import json

from cli.command_parser import ActionHelpFormatter
from cli.commands.music.base import MusicSubCommand


# Constantes de description simplifiées
LIBRARY_HELP = "Gérer la bibliothèque musicale"
PLAYLIST_HELP = "Gérer les playlists"
TRACK_HELP = "Gérer les pistes musicales"


class LibraryCommands(MusicSubCommand):
    """Commandes de bibliothèque musicale."""

    @staticmethod
    def setup_parsers(subparsers):
        """Configure les parsers pour les commandes de bibliothèque."""

        # Action: track (library track/album)
        track_parser = subparsers.add_parser(
            "track",
            help="Jouer un morceau de bibliothèque",
            description=TRACK_HELP,
            formatter_class=ActionHelpFormatter,
        )
        track_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        track_group = track_parser.add_mutually_exclusive_group(required=True)
        track_group.add_argument(
            "--track-id",
            type=str,
            metavar="TRACK_ID",
            help="ID du morceau",
        )
        track_group.add_argument(
            "--album",
            type=str,
            metavar="ALBUM",
            help="Nom de l'album (nécessite --artist)",
        )
        track_parser.add_argument(
            "--artist",
            type=str,
            metavar="ARTIST",
            help="Nom de l'artiste (si --album utilisé)",
        )
        track_parser.add_argument(
            "--shuffle",
            action="store_true",
            help="Lire en mode aléatoire",
        )

        # Action: playlist
        playlist_parser = subparsers.add_parser(
            "playlist",
            help="Lire une playlist",
            description=PLAYLIST_HELP,
            formatter_class=ActionHelpFormatter,
        )
        playlist_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        playlist_parser.add_argument("--id", type=str, required=True, metavar="PLAYLIST_ID", help="ID de la playlist")
        playlist_parser.add_argument(
            "--type",
            type=str,
            choices=["library", "prime-asin", "prime-station", "prime-queue"],
            default="library",
            help="Type de playlist (défaut: library)",
        )
        playlist_parser.add_argument("--shuffle", action="store_true", help="Lire en mode aléatoire")

        # Action: library
        library_parser = subparsers.add_parser(
            "library",
            help="Bibliothèque musicale",
            description=LIBRARY_HELP,
            formatter_class=ActionHelpFormatter,
        )
        library_group = library_parser.add_mutually_exclusive_group(required=True)
        library_group.add_argument("--playlists", action="store_true", help="Lister les playlists bibliothèque")
        library_group.add_argument("--purchases", action="store_true", help="Lister les achats")
        library_group.add_argument("--imported", action="store_true", help="Lister les titres importés")
        library_group.add_argument("--prime-playlists", action="store_true", help="Lister les playlists Prime Music")
        library_group.add_argument("--prime-stations", action="store_true", help="Lister les stations Prime Music")
        library_parser.add_argument(
            "-d",
            "--device",
            type=str,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil (requis pour Prime)",
        )
        library_parser.add_argument(
            "--json",
            action="store_true",
            help="Afficher en format JSON",
        )

    def track(self, args: argparse.Namespace) -> bool:
        """Jouer un morceau de bibliothèque."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "music_library", None):
                self.error("MusicLibraryService non disponible")
                return False

            media_owner_id = self.get_media_owner_id()

            # Vérifier les arguments
            if args.album and not args.artist:
                self.error("--artist requis avec --album")
                return False

            if args.track_id:
                self.info(f"🎵 Lecture morceau {args.track_id} sur '{args.device}'...")
                result = self.call_with_breaker(
                    ctx.music_library.play_library_track,
                    serial,
                    device_type,
                    media_owner_id,
                    track_id=args.track_id,
                    shuffle=args.shuffle,
                )
            else:
                self.info(f"💿 Lecture album '{args.album}' de {args.artist} sur '{args.device}'...")
                result = self.call_with_breaker(
                    ctx.music_library.play_library_track,
                    serial,
                    device_type,
                    media_owner_id,
                    artist=args.artist,
                    album=args.album,
                    shuffle=args.shuffle,
                )

            if result:
                self.success("✅ Lecture lancée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lecture bibliothèque")
            self.error(f"Erreur: {e}")
            return False

    def playlist(self, args: argparse.Namespace) -> bool:
        """Lire une playlist (library, Prime ASIN, Prime station, Prime queue)."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "music_library", None):
                self.error("MusicLibraryService non disponible")
                return False

            media_owner_id = self.get_media_owner_id()
            shuffle_text = " (mode aléatoire)" if args.shuffle else ""

            # Library playlist
            if args.type == "library":
                self.info(f"📝 Lecture playlist bibliothèque sur '{args.device}'{shuffle_text}...")
                result = self.call_with_breaker(
                    ctx.music_library.play_library_playlist,
                    serial,
                    device_type,
                    media_owner_id,
                    args.id,
                    args.shuffle,
                )

            # Prime playlist (ASIN)
            elif args.type == "prime-asin":
                self.info(f"📝 Lecture playlist Prime (ASIN) sur '{args.device}'...")
                result = self.call_with_breaker(
                    ctx.music_library.play_prime_playlist,
                    serial,
                    device_type,
                    media_owner_id,
                    args.id,
                )

            # Prime station (seedID)
            elif args.type == "prime-station":
                self.info(f"📻 Lecture station Prime sur '{args.device}'...")
                result = self.call_with_breaker(
                    ctx.music_library.play_prime_station,
                    serial,
                    device_type,
                    media_owner_id,
                    args.id,
                )

            # Prime historical queue
            elif args.type == "prime-queue":
                self.info(f"📜 Lecture queue historique Prime sur '{args.device}'...")
                result = self.call_with_breaker(
                    ctx.music_library.play_historical_queue,
                    serial,
                    device_type,
                    media_owner_id,
                    args.id,
                )

            else:
                self.error(f"Type de playlist inconnu: {args.type}")
                return False

            if result:
                self.success("✅ Lecture lancée")
                return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de la lecture playlist")
            self.error(f"Erreur: {e}")
            return False

    def library(self, args: argparse.Namespace) -> bool:
        """Afficher la bibliothèque."""
        try:
            ctx = getattr(self, "context", None)
            # Pour les options Prime, un appareil est requis
            if (args.prime_playlists or args.prime_stations) and not args.device:
                self.error("L'option --device est requise pour les listes Prime")
                return False

            # Pour imported/purchased/playlists, utiliser MusicLibraryService
            if args.imported or args.purchased or args.playlists:
                if not ctx or not getattr(ctx, "music_library", None):
                    self.error("MusicLibraryService non disponible")
                    return False

                # Obtenir les infos appareil (optionnel pour library)
                serial = ""
                device_type = ""
                if args.device:
                    device_info = self.get_device_info(args.device)
                    if device_info:
                        serial, device_type = device_info

                media_owner_id = self.get_media_owner_id()

                # Déterminer le type de playlist
                if args.imported:
                    playlist_type = "imported"
                    self.info("📚 Morceaux importés...")
                elif args.purchased:
                    playlist_type = "purchased"
                    self.info("📚 Morceaux achetés...")
                else:  # playlists
                    playlist_type = "cloudplayer"
                    self.info("📚 Playlists bibliothèque...")

                items = self.call_with_breaker(
                    ctx.music_library.get_library_playlists,
                    serial,
                    device_type,
                    media_owner_id,
                    playlist_type,
                )

                if items:
                    if args.json:
                        print(json.dumps(items, indent=2, ensure_ascii=False))
                    else:
                        self.success(f"✅ {len(items)} éléments trouvés")
                        for i, item in enumerate(items[:20], 1):  # Limiter à 20
                            print(f"  {i}. {item.get('title', 'Sans titre')}")
                        if len(items) > 20:
                            print(f"\n  ... et {len(items) - 20} autres")
                    return True
                else:
                    self.warning("Aucun élément trouvé")
                    return True

            # Prime playlists
            elif args.prime_playlists:
                device_info = self.get_device_info(args.device)
                if not device_info:
                    return False

                serial, device_type = device_info
                media_owner_id = self.get_media_owner_id()

                self.info("📚 Playlists Prime Music...")

                if not ctx or not getattr(ctx, "music_library", None):
                    self.error("MusicLibraryService non disponible")
                    return False

                playlists = self.call_with_breaker(
                    ctx.music_library.get_prime_playlists,
                    serial,
                    device_type,
                    media_owner_id,
                )

                if playlists:
                    if args.json:
                        print(json.dumps(playlists, indent=2, ensure_ascii=False))
                    else:
                        self.success(f"✅ {len(playlists)} playlists Prime trouvées")
                        for i, pl in enumerate(playlists[:20], 1):
                            name = pl.get("title", pl.get("name", "Sans titre"))
                            asin = pl.get("asin", "N/A")
                            print(f"  {i}. {name} (ASIN: {asin})")
                        if len(playlists) > 20:
                            print(f"\n  ... et {len(playlists) - 20} autres")
                    return True
                else:
                    self.warning("Aucune playlist Prime trouvée")
                    return True

            # Prime stations
            elif args.prime_stations:
                device_info = self.get_device_info(args.device)
                if not device_info:
                    return False

                serial, device_type = device_info
                media_owner_id = self.get_media_owner_id()

                self.info("📻 Stations Prime Music...")

                if not ctx or not getattr(ctx, "music_library", None):
                    self.error("MusicLibraryService non disponible")
                    return False

                stations = self.call_with_breaker(
                    ctx.music_library.get_prime_stations,
                    serial,
                    device_type,
                    media_owner_id,
                )

                if stations:
                    if args.json:
                        print(json.dumps(stations, indent=2, ensure_ascii=False))
                    else:
                        self.success(f"✅ {len(stations)} stations Prime trouvées")
                        for i, st in enumerate(stations[:20], 1):
                            name = st.get("title", st.get("name", "Sans titre"))
                            seed = st.get("seedId", "N/A")
                            print(f"  {i}. {name} (Seed: {seed})")
                        if len(stations) > 20:
                            print(f"\n  ... et {len(stations) - 20} autres")
                    return True
                else:
                    self.warning("Aucune station Prime trouvée")
                    return True

            return False

        except Exception as e:
            self.logger.exception("Erreur lors de l'affichage bibliothèque")
            self.error(f"Erreur: {e}")
            return False
