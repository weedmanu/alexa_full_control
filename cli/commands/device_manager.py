from typing import Any, Dict

from cli.command_template import ManagerCommand


class DeviceManagerCommand(ManagerCommand):
    """
    Manager-based Device command. Async-friendly implementation that uses
    DI container to get the device_manager.
    """

    def __init__(self, name: str, di_container: Any) -> None:
        super().__init__(name, di_container)

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

            elif action == "volume":
                # Expect nested volume_action: get | set
                volume_action = params.get("volume_action") or params.get("volume-action")
                # Acquire settings manager from DI/context. Try several common names.
                settings_mgr = None
                for _name in ("settings_mgr", "settings_manager", "device_settings_manager", "device_settings"):
                    try:
                        settings_mgr = self.get_manager(_name)
                    except Exception:
                        settings_mgr = None
                    if settings_mgr:
                        break

                # Fallback: some setups expose volume methods on the device manager itself
                if not settings_mgr and hasattr(mgr, "get_volume") and hasattr(mgr, "set_volume"):  # type: ignore[attr-defined]
                    settings_mgr = mgr

                if not settings_mgr:
                    # Provide diagnostic info to help debug DI registration
                    try:
                        from core.manager_factory import ManagerFactory

                        mf = ManagerFactory()
                        available = mf.get_registered_names()
                    except Exception:
                        available = []

                    try:
                        singletons = list(self.di_container._singletons.keys())  # type: ignore[attr-defined]
                    except Exception:
                        singletons = []

                    return {
                        "success": False,
                        "error": "SettingsManager not available",
                        "available_managers": available,
                        "di_singletons": singletons,
                    }

                # Helper to resolve device serial/type if provided via device name
                device_name = params.get("device")
                serial = params.get("serial")
                device_type = params.get("device_type") or params.get("device-type")

                # If only device name provided, try to resolve via device manager
                if device_name and not serial:
                    devices = await asyncio.to_thread(mgr.get_devices)
                    from data.name_id_mapper import find_id_by_name

                    found_serial, matched = find_id_by_name(devices, device_name, name_keys=("accountName", "name"))
                    if found_serial:
                        serial = found_serial
                        device_type = device_type or (matched.get("deviceType") if matched else None)

                try:
                    if volume_action == "get":
                        if not serial or not device_type:
                            return {"success": False, "error": "Missing device identifier for get volume"}
                        # Diagnostic logging: report resolved identifiers
                        try:
                            from loguru import logger

                            logger.debug(f"Resolved for get_volume -> serial={serial!r}, device_type={device_type!r}")
                        except Exception:
                            pass
                        vol = await asyncio.to_thread(settings_mgr.get_volume, serial, device_type)
                        # Try to resolve friendly name from serial for nicer output
                        device_name_resolved = None
                        try:
                            devices = await asyncio.to_thread(mgr.get_devices)
                            from data.name_id_mapper import find_name_by_id

                            device_name_resolved = find_name_by_id(devices, serial)
                        except Exception:
                            device_name_resolved = None

                        return {
                            "success": True,
                            "data": {"volume": vol, "serial": serial, "device_name": device_name_resolved},
                        }

                    elif volume_action == "set":
                        level = params.get("level")
                        if level is None:
                            return {"success": False, "error": "Missing volume level for set"}
                        if not serial or not device_type:
                            # try resolve again
                            devices = await asyncio.to_thread(mgr.get_devices)
                            for d in devices:
                                if d.get("accountName") == device_name:
                                    serial = d.get("serialNumber")
                                    device_type = device_type or d.get("deviceType")
                                    break
                        if not serial or not device_type:
                            return {"success": False, "error": "Missing device identifier for set volume"}
                        ok = await asyncio.to_thread(settings_mgr.set_volume, serial, device_type, int(level))
                        # Resolve name for response
                        device_name_resolved = None
                        try:
                            devices = await asyncio.to_thread(mgr.get_devices)
                            from data.name_id_mapper import find_name_by_id

                            device_name_resolved = find_name_by_id(devices, serial)
                        except Exception:
                            device_name_resolved = None
                        return {
                            "success": True,
                            "data": {"result": ok, "serial": serial, "device_name": device_name_resolved},
                        }

                    else:
                        return {"success": False, "error": f"Volume action '{volume_action}' not supported"}
                except Exception as e:
                    return {"success": False, "error": str(e)}

            else:
                return {"success": False, "error": f"Action '{action}' not implemented in ManagerCommand"}

        except Exception as e:
            return {"success": False, "error": str(e)}
