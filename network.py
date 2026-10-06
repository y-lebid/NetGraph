import socket
import subprocess


def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    finally:
        sock.close()


def get_network_info():
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