from network import get_network_info


def main():
    print("╔══════════════════════════╗")
    print("║         NetGraph         ║")
    print("║  Local Network Analyzer  ║")
    print("╚══════════════════════════╝")

    network_info = get_network_info()

    print(f"Local IP Address: {network_info['local_ip']}")
    print(f"Network Interface: {network_info['interface']}")
    print(f"Default Gateway: {network_info['gateway']}")


if __name__ == "__main__":
    main()