from typing import Any, Dict

from cli.command_template import ManagerCommand


class MusicPlaybackManagerCommand(ManagerCommand):
    def __init__(self, di_container) -> None:
        super().__init__("music_playback", di_container)

    @classmethod
    def setup_parser(cls, parser: Any) -> None:
        # Reuse existing parser definitions from music_playback module
        try:
            from cli.commands.music_playback import PlaybackCommands

            subparsers = parser.add_subparsers(dest="action", required=True)
            PlaybackCommands.setup_parsers(subparsers)
        except Exception:
            sp = parser.add_subparsers(dest="action", required=True)
            sp.add_parser("play", help="Play music")

    def validate(self, params: Dict[str, Any]) -> bool:
        return True

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        action = params.get("action")
        try:
            mgr = self.get_manager("playback_manager")
            import asyncio

            if not mgr:
                return {"success": False, "error": "Playback manager not available"}

            # Map action to manager methods
            if action == "pause":
                res = await asyncio.to_thread(mgr.pause, params.get("device"))
            elif action == "stop":
                res = await asyncio.to_thread(mgr.stop, params.get("device"))
            elif action == "control":
                # action_type contains the control
                res = await asyncio.to_thread(mgr.play if params.get("action_type") == "play" else mgr.pause, params.get("device"))
            elif action == "shuffle":
                res = await asyncio.to_thread(mgr.set_shuffle, params.get("device"), params.get("mode") in ("on", "enable"))
            elif action == "repeat":
                res = await asyncio.to_thread(mgr.set_repeat, params.get("device"), params.get("mode"))
            else:
                return {"success": False, "error": f"Unknown action {action}"}

            return {"success": bool(res), "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}
