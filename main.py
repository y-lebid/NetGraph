from network import get_network_info, get_network
from discovery import discover_devices


def print_header():
    print("╔══════════════════════════╗")
    print("║         NetGraph         ║")
    print("╚══════════════════════════╝")


def analyze_network():
    print("\n[*] Detecting network configuration...\n")

    network_info = get_network_info()
    network = get_network()

    print(f"Local IP:      {network_info['local_ip']}")
    print(f"Subnet:        {network}")
    print(f"Gateway:       {network_info['gateway']}")
    print(f"Interface:     {network_info['interface']}")

    print("\n[*] Analyzing local network...\n")

    devices = discover_devices(network)

    print(f"\nDevices found: {len(devices)}\n")

    for device in devices:
        mac = device["mac"] or "unknown"

        print(
            f"Device         {device['ip']:<16} "
            f"MAC: {mac}"
    )

    print("\n1. Show network graph")
    print("2. BFS")
    print("3. DFS")
    print("4. Dijkstra")
    print("5. Network statistics")
    print("0. Back")


def main():
    while True:
        print()
        print_header()

        print("\n1. Analyze my network")
        print("2. Load sample network")
        print("3. Generate test network")
        print("0. Exit")

        choice = input("\nSelect: ")

        if choice == "1":
            analyze_network()
            input("\nPress Enter to continue...")

        elif choice == "2":
            print("\n[!] Sample networks are not implemented yet.")
            input("\nPress Enter to continue...")

        elif choice == "3":
            print("\n[!] Network generation is not implemented yet.")
            input("\nPress Enter to continue...")

        elif choice == "0":
            print("\nGoodbye!")
            break

        else:
            print("\n[!] Invalid option.")


if __name__ == "__main__":
    main()