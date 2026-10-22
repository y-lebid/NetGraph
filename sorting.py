import ipaddress


def _sort_key(device, field):
    if field == "ip":
        try:
            return (0, int(ipaddress.ip_address(device.get("ip", "0.0.0.0"))))
        except ValueError:
            return (1, str(device.get("ip", "")).casefold())
    if field in ("type", "device_type"):
        field = "device_type"
    return (0, str(device.get(field) or "").casefold())


def sort_devices(devices, field="ip", reverse=False):
    aliases = {"type": "device_type"}
    field = aliases.get(field, field)
    if field not in {"ip", "name", "device_type", "mac"}:
        raise ValueError("Sort field must be ip, name, type, or mac")
    return sorted(devices, key=lambda item: _sort_key(item, field), reverse=reverse)
