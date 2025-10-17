from typing import Any, Dict

from cli.command_template import ManagerCommand


class DeviceManagerCommand(ManagerCommand):
    """
    Manager-based Device command. Async-friendly implementation that uses
    DI container to get the device_manager.
    """

    def __init__(self, di_container) -> None:
        super().__init__("device", di_container)

    @classmethod
    def setup_parser(cls, parser: Any) -> None:
        # Reuse the existing device parser layout via temporary instance of the
        # legacy DeviceCommand if available to avoid duplication.
        try:
            from cli.commands.device import DeviceCommand

            temp = DeviceCommand(context=None)
            temp.setup_parser(parser)
        except Exception:
            # Minimal fallback: create simple list/info actions
            subparsers = parser.add_subparsers(dest="action", metavar="ACTION", required=True)
            subparsers.add_parser("list", help="Lister tous les appareils")
            info_p = subparsers.add_parser("info", help="Info appareil")
            info_p.add_argument("-d", "--device", required=True)

    def validate(self, params: Dict[str, Any]) -> bool:
        # Basic validation: action must be present
        return "action" in params and params["action"] is not None

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Convert params keys to expected names
        action = params.get("action")

        try:
            # Get manager from DI
            mgr = self.get_manager("device_manager")
            if not mgr:
                return {"success": False, "error": "Device manager not available"}

            # Use to_thread to avoid blocking loop if manager is sync
            import asyncio

            if action == "list":
                devices = await asyncio.to_thread(mgr.get_devices)
                # Optional filtering
                flt = params.get("filter")
                if flt:
                    devices = [d for d in devices if flt.lower() in d.get("accountName", "").lower()]

                online_only = params.get("online_only") or params.get("online-only") or params.get("onlineOnly")
                if online_only:
                    devices = [d for d in devices if d.get("online", False)]

                formatted = f"Found {len(devices)} devices"
                return {"success": True, "data": devices, "formatted": formatted}

            elif action == "info":
                device_name = params.get("device")
                devices = await asyncio.to_thread(mgr.get_devices)
                for d in devices:
                    if d.get("accountName") == device_name:
                        return {"success": True, "data": d}
                return {"success": False, "error": f"Device '{device_name}' not found"}

            else:
                return {"success": False, "error": f"Action '{action}' not implemented in ManagerCommand"}

        except Exception as e:
            return {"success": False, "error": str(e)}
