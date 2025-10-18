from typing import Any, Dict

from cli.command_template import ManagerCommand


class TimersManagerCommand(ManagerCommand):
    def __init__(self, di_container: Any) -> None:
        super().__init__("timers", di_container)

    @classmethod
    def setup_parser(cls, parser: Any) -> None:
        # As `timers` aggregated command was removed, provide a minimal parser
        # to avoid import errors. Detailed timer actions are available via
        # `timers_alarm`, `timers_reminder`, `timers_countdown` modules if
        # needed; here we keep a simple 'list' action for the manager wrapper.
        subparsers = parser.add_subparsers(dest="action", required=True)
        subparsers.add_parser("list", help="List timers/alarms/reminders")

    def validate(self, params: Dict[str, Any]) -> bool:
        return "action" in params and params["action"] is not None

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        action = params.get("action")
        if not isinstance(action, str):
            return {"success": False, "error": "Invalid action"}

        try:
            mgr = self.get_manager("timer_manager")
            import asyncio

            if not mgr:
                return {"success": False, "error": "Timer manager not available"}

            # Delegate actions to manager in thread
            result = await asyncio.to_thread(
                lambda: getattr(mgr, action)(**{k: v for k, v in params.items() if k != "action"})
            )
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
