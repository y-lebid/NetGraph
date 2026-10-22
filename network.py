import ipaddress
import json
import platform
import subprocess


def get_network_info():
    system = platform.system()
    if system == "Linux":
        return get_linux_network_info()
    if system == "Windows":
        return get_windows_network_info()
    raise RuntimeError(f"Unsupported operating system: {system}")


def _prefix_to_mask(prefix):
    return str(ipaddress.IPv4Network(f"0.0.0.0/{prefix}").netmask)


def get_linux_network_info():
    route_result = subprocess.run(
        ["ip", "-j", "route", "get", "8.8.8.8"],
        capture_output=True, text=True, check=True,
    )
    routes = json.loads(route_result.stdout)
    if not routes:
        raise RuntimeError("No route is available to determine the local network")
    route = routes[0]
    interface = route.get("dev")
    local_ip = route.get("prefsrc") or route.get("src")
    gateway = route.get("gateway")
    if not interface or not local_ip:
        raise RuntimeError("Could not determine the active interface and local IP")

    address_result = subprocess.run(
        ["ip", "-j", "address", "show", "dev", interface],
        capture_output=True, text=True, check=True,
    )
    addresses = json.loads(address_result.stdout)
    prefix = next(
        (address["prefixlen"] for item in addresses
         for address in item.get("addr_info", [])
         if address.get("family") == "inet" and address.get("local") == local_ip),
        None,
    )
    if prefix is None:
        raise RuntimeError(f"Could not determine subnet prefix for {local_ip}")

    return {
        "interface": interface,
        "gateway": gateway,
        "local_ip": local_ip,
        "subnet_mask": _prefix_to_mask(prefix),
    }


def get_windows_network_info():
    script = (
        "Get-NetIPConfiguration | "
        "Where-Object { $_.IPv4Address -and $_.NetAdapter.Status -eq 'Up' } | "
        "Sort-Object { [bool]$_.IPv4DefaultGateway } -Descending | "
        "Select-Object -First 1 InterfaceAlias,"
        "@{Name='LocalIP';Expression={$_.IPv4Address[0].IPAddress}},"
        "@{Name='PrefixLength';Expression={$_.IPv4Address[0].PrefixLength}},"
        "@{Name='Gateway';Expression={$_.IPv4DefaultGateway.NextHop}} | "
        "ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    )
    try:
        config = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Could not parse Windows network configuration") from error
    if not config or not config.get("LocalIP") or config.get("PrefixLength") is None:
        raise RuntimeError("Could not determine local IPv4 network configuration")
    return {
        "interface": config.get("InterfaceAlias") or "Windows network adapter",
        "gateway": config.get("Gateway"),
        "local_ip": config["LocalIP"],
        "subnet_mask": _prefix_to_mask(int(config["PrefixLength"])),
    }


def get_network():
    info = get_network_info()
    local_ip = info["local_ip"]
    subnet_mask = info.get("subnet_mask")
    network = ipaddress.ip_network(
        f"{local_ip}/{subnet_mask or '24'}", strict=False
    )
    return network
