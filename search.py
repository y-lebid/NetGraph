def search_devices(devices, query):
    needle = str(query or "").strip().casefold()
    if not needle:
        return list(devices)
    fields = ("ip", "mac", "name", "device_type", "type")
    return [
        device for device in devices
        if any(needle in str(device.get(field) or "").casefold() for field in fields)
    ]
