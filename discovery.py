import ipaddress
import platform
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


MAX_WORKERS = 32

MAC_PATTERN = re.compile(
    r"^(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$"
)


def ping_host(ip_address):
    system = platform.system()

    if system == "Windows":
        command = [
            "ping", "-n", "1", "-w", "500",
            str(ip_address),
        ]

    elif system == "Linux":
        command = [
            "ping", "-c", "1", "-W", "1",
            str(ip_address),
        ]

    else:
        raise RuntimeError(
            f"Unsupported operating system: {system}"
        )

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0


def get_arp_table():
    system = platform.system()

    if system == "Windows":
        command = ["arp", "-a"]

    elif system == "Linux":
        command = ["ip", "neigh"]

    else:
        raise RuntimeError(
            f"Unsupported operating system: {system}"
        )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    return result.stdout


def is_valid_device_ip(ip_address, network=None):
    try:
        address = ipaddress.ip_address(ip_address)
    except ValueError:
        return False

    if not isinstance(address, ipaddress.IPv4Address):
        return False

    if (
        address.is_multicast
        or address.is_loopback
        or address.is_link_local
        or address.is_unspecified
        or address == ipaddress.IPv4Address("255.255.255.255")
    ):
        return False

    if network is not None:
        if address not in network:
            return False

        if (
            address == network.network_address
            or address == network.broadcast_address
        ):
            return False

    return True


def parse_arp_table(output, network=None):
    devices = {}

    for line in output.splitlines():
        parts = line.split()

        if len(parts) < 2:
            continue

        ip_address = parts[0]

        if not is_valid_device_ip(ip_address, network):
            continue

        mac_address = next(
            (
                part.lower()
                for part in parts
                if MAC_PATTERN.fullmatch(part)
            ),
            None,
        )

        if mac_address is None:
            continue

        devices[ip_address] = {
            "ip": ip_address,
            "mac": mac_address,
        }

    return list(devices.values())


def discover_devices(network):
    if not isinstance(network, ipaddress.IPv4Network):
        raise ValueError("An IPv4 network is required")

    hosts = list(network.hosts())
    devices = {}
    total = len(hosts)
    completed = 0

    print(f"[*] Scanning {total} addresses...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(ping_host, ip): ip
            for ip in hosts
        }

        for future in as_completed(futures):
            ip_address = futures[future]
            completed += 1

            try:
                if future.result():
                    devices[str(ip_address)] = {
                        "ip": str(ip_address),
                        "mac": None,
                    }
            except Exception as error:
                print(
                    f"\n[!] Could not scan {ip_address}: {error}"
                )

            print(
                f"\r[*] Scanning: {completed}/{total} "
                f"| Devices found: {len(devices)}",
                end="",
                flush=True,
            )

    print()
    print("[*] Reading ARP table...")

    try:
        arp_output = get_arp_table()
        arp_devices = parse_arp_table(arp_output, network)
    except (OSError, subprocess.SubprocessError) as error:
        print(f"[!] Could not read ARP table: {error}")
        arp_devices = []

    for device in arp_devices:
        ip_address = device["ip"]

        if ip_address in devices:
            devices[ip_address]["mac"] = device["mac"]
        else:
            devices[ip_address] = device

    result = sorted(
        devices.values(),
        key=lambda device: ipaddress.ip_address(device["ip"]),
    )

    return result
