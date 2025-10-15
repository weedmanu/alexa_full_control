"""
Commandes de statut et informations.

Gère: status, queue, history

Auteur: M@nu
Date: 8 octobre 2025
"""

import argparse

from cli.commands.music.base import MusicSubCommand


class StatusCommands(MusicSubCommand):
    """Commandes de statut et informations."""

    @staticmethod
    def setup_parsers(subparsers):
        """Configure les parsers pour les commandes de statut."""

        # Action: queue
        queue_parser = subparsers.add_parser(
            "queue",
            help="Afficher la file d'attente",
            description="Affiche la file d'attente actuelle d'un appareil.",
        )
        queue_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )

        # Action: status
        status_parser = subparsers.add_parser(
            "status",
            help="État de la lecture",
            description="Affiche l'état actuel de la lecture musicale.",
        )
        status_parser.add_argument(
            "-d",
            "--device",
            type=str,
            required=True,
            metavar="DEVICE_NAME",
            help="Nom de l'appareil",
        )
        status_parser.add_argument(
            "--complete",
            action="store_true",
            help="Afficher l'état complet avec détails qualité audio",
        )

    def queue(self, args: argparse.Namespace) -> bool:
        """Afficher la file d'attente (identique à status)."""
        # Queue et status utilisent la même logique
        return self.status(args)

    def status(self, args: argparse.Namespace) -> bool:
        """Afficher l'état actuel de la lecture (comme le script shell -q)."""
        try:
            device_info = self.get_device_info(args.device)
            if not device_info:
                return False

            serial, device_type = device_info

            self.info(f"📊 État de la lecture sur '{args.device}'...")

            ctx = getattr(self, "context", None)
            if not ctx or not getattr(ctx, "playback_mgr", None):
                self.error("PlaybackManager non disponible")
                return False

            # Récupérer parent multiroom si applicable
            parent_id, parent_type = self._get_parent_multiroom(args.device)

            # Récupérer l'état complet (3 endpoints API comme le shell)
            state = ctx.playback_mgr.get_state(
                serial,
                device_type,
                parent_id,
                parent_type,
            )

            if state:
                self._display_complete_status(state, args.device, device_type)
                return True
            else:
                self.warning("Aucune lecture en cours")
                return True

        except Exception as e:
            self.logger.exception("Erreur statut")
            self.error(f"Erreur: {e}")
            return False

    def _display_complete_status(self, state: dict, device_name: str, device_type: str):
        """Affiche l'état complet de la lecture avec qualité audio."""
        print(f"\n🎵 État Lecture - {device_name} ({device_type})")
        print()

        # État de lecture
        player_state = state.get("playerInfo", {}).get("state", "UNKNOWN")
        state_icons = {
            "PLAYING": "▶️  Actuellement en lecture",
            "PAUSED": "⏸️  En pause",
            "STOPPED": "⏹️  Arrêté",
        }
        print(state_icons.get(player_state, f"❓ État: {player_state}"))
        print("━" * 42)

        # Informations du morceau
        info_data = state.get("playerInfo", {}).get("infoText", {})
        state.get("playerInfo", {}).get("mainArt", {})

        title = info_data.get("title", "Inconnu")
        artist = info_data.get("subText1", "Inconnu")
        album = info_data.get("subText2", "")

        print(f"\n🎵 Titre      : {title}")
        print(f"🎤 Artiste    : {artist}")
        if album:
            print(f"💿 Album      : {album}")

        # Position et durée
        progress = state.get("playerInfo", {}).get("progress", {})
        if progress:
            media_length = progress.get("mediaLength", 0)
            media_progress = progress.get("mediaProgress", 0)

            if media_length > 0:
                duration_min = media_length // 60000
                duration_sec = (media_length % 60000) // 1000
                progress_min = media_progress // 60000
                progress_sec = (media_progress % 60000) // 1000

                pos_str = f"{progress_min:02d}:{progress_sec:02d} / {duration_min:02d}:{duration_sec:02d}"
                print(f"⏱️  Position   : {pos_str}")

        # Provider et qualité
        provider = state.get("playerInfo", {}).get("provider", {}).get("providerName", "")
        if provider:
            print(f"📻 Provider   : {provider}")

        # Qualité audio (si disponible)
        quality_info = state.get("mediaState", {}).get("contentQuality", {})
        if quality_info:
            codec = quality_info.get("codec", "")
            sample_rate = quality_info.get("sampleRate", 0)
            bitrate = quality_info.get("bitrate", 0)

            if codec or sample_rate or bitrate:
                quality_parts = []
                if codec:
                    quality_parts.append(codec)
                if sample_rate:
                    quality_parts.append(f"{sample_rate // 1000}kHz")
                if bitrate:
                    quality_parts.append(f"{bitrate} kbps")

                print(f"🎚️  Qualité   : {' • '.join(quality_parts)}")

        # Modes shuffle et repeat
        print()
        shuffle_enabled = state.get("playerInfo", {}).get("transport", {}).get("shuffle", False)
        repeat_mode = state.get("playerInfo", {}).get("transport", {}).get("repeat", False)

        print(f"🔀 Shuffle    : {'ON' if shuffle_enabled else 'OFF'}")
        print(f"🔁 Repeat     : {'ON' if repeat_mode else 'OFF'}")

        # Multiroom
        if state.get("multiroom"):
            parent_name = state.get("multiroom", {}).get("parentName", device_name)
            print(f"🔊 Multiroom  : {parent_name} (appareil parent)")

        # Queue info
        queue_data = state.get("queue", {})
        if queue_data:
            queue_size = len(queue_data.get("entries", []))
            if queue_size > 0:
                print(f"\n📋 File d'attente : {queue_size} morceaux")

                # Afficher les 5 prochains
                for i, entry in enumerate(queue_data.get("entries", [])[:5], 1):
                    track_title = entry.get("title", "Sans titre")
                    track_artist = entry.get("artist", "")
                    if track_artist:
                        print(f"  {i}. {track_title} - {track_artist}")
                    else:
                        print(f"  {i}. {track_title}")

                if queue_size > 5:
                    print(f"  ... et {queue_size - 5} autres morceaux")

        print()
