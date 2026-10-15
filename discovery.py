import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


MAX_WORKERS = 32


def ping_host(ip_address):
    system = platform.system()

    if system == "Windows":
        command = [
            "ping",
            "-n", "1",
            "-w", "500",
            str(ip_address),
        ]

    elif system == "Linux":
        command = [
            "ping",
            "-c", "1",
            "-W", "1",
            str(ip_address),
        ]

    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

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
        raise RuntimeError(f"Unsupported operating system: {system}")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    return result.stdout


def parse_arp_table(output):
    devices = []

    for line in output.splitlines():
        parts = line.split()

        if len(parts) < 2:
            continue

        ip_address = parts[0]

        if not ip_address.replace(".", "").isdigit():
            continue

        mac_address = None

        for part in parts:
            if "-" in part or ":" in part:
                mac_address = part
                break

        devices.append({
            "ip": ip_address,
            "mac": mac_address,
        })

    return devices


def discover_devices(network):
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
            ip = futures[future]
            completed += 1

            try:
                if future.result():
                    devices[str(ip)] = {
                        "ip": str(ip),
                        "mac": None,
                    }
            except Exception:
                pass

            print(
                f"\r[*] Scanning: {completed}/{total} "
                f"| Devices found: {len(devices)}",
                end="",
                flush=True,
            )

    print()

    print("[*] Reading ARP table...")

    arp_output = get_arp_table()
    arp_devices = parse_arp_table(arp_output)

    for device in arp_devices:
        ip_address = device["ip"]

        if ip_address in devices:
            devices[ip_address]["mac"] = device["mac"]
        else:
            devices[ip_address] = device

    result = list(devices.values())

    result.sort(
        key=lambda device: tuple(
            int(part)
            for part in device["ip"].split(".")
        )
    )

    return result