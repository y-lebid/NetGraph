import ipaddress
import platform
import re
import subprocess


def get_network_info():
    system = platform.system()

    if system == "Linux":
        return get_linux_network_info()

    if system == "Windows":
        return get_windows_network_info()

    raise RuntimeError(f"Unsupported operating system: {system}")


def get_linux_network_info():
    result = subprocess.run(
        ["ip", "route", "get", "8.8.8.8"],
        capture_output=True,
        text=True,
        check=True
    )

    parts = result.stdout.split()

    interface = parts[parts.index("dev") + 1]
    gateway = parts[parts.index("via") + 1]
    local_ip = parts[parts.index("src") + 1]

    return {
        "interface": interface,
        "gateway": gateway,
        "local_ip": local_ip,
    }


def get_windows_network_info():
    result = subprocess.run(
        ["ipconfig"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True
    )

    output = result.stdout

    ipv4_match = re.search(
        r"IPv4 Address[.\s]*:\s*([\d.]+)",
        output
    )

    mask_match = re.search(
        r"Subnet Mask[.\s]*:\s*([\d.]+)",
        output
    )

    gateway_match = re.search(
        r"Default Gateway[.\s]*:\s*([\d.]+)",
        output
    )

    if not ipv4_match:
        raise RuntimeError("Could not determine local IP address")

    if not mask_match:
        raise RuntimeError("Could not determine subnet mask")

    local_ip = ipv4_match.group(1)
    subnet_mask = mask_match.group(1)

    gateway = gateway_match.group(1) if gateway_match else None

    return {
        "interface": "Windows network adapter",
        "gateway": gateway,
        "local_ip": local_ip,
        "subnet_mask": subnet_mask,
    }


def get_network():
    network_info = get_network_info()

    local_ip = network_info["local_ip"]
    subnet_mask = network_info["subnet_mask"] if "subnet_mask" in network_info else None

    if subnet_mask:
        network = ipaddress.ip_network(
            f"{local_ip}/{subnet_mask}",
            strict=False
        )
    else:
        network = ipaddress.ip_network(
            f"{local_ip}/24",
            strict=False
        )

    return network