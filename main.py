import ipaddress

from discovery import discover_devices
from network import get_network_info
from network_graph import create_network_graph
from models import Device
from search import search_devices
from sorting import sort_devices
from terminal_graph import draw_graph


def print_header():
    print("+--------------------------+")
    print("|         NetGraph         |")
    print("+--------------------------+")


def pause():
    input("\nPress Enter to continue...")


def show_devices(devices):
    if not devices:
        print("No matching devices.")
        return
    for device in devices:
        print(
            f"{device.get('ip') or '-':<16} "
            f"{device.get('name') or '-':<16} "
            f"{device.get('device_type') or 'unknown':<12} "
            f"{device.get('mac') or 'unknown'}"
        )


def manage_devices(graph, discovered=None):
    devices = list(discovered or [])
    present = {str(item.get("ip", "")).casefold() for item in devices}
    for vertex in graph.get_vertices():
        if str(vertex).casefold() not in present:
            devices.append({
                "ip": str(vertex),
                "name": str(vertex),
                "device_type": "router" if "router" in str(vertex).casefold() else "unknown",
                "mac": None,
            })

    while True:
        print("\nDevice tools: 1. Search  2. Sort  0. Back")
        choice = input("Select: ").strip()
        if choice == "0":
            return
        if choice == "1":
            query = input("Search IP, MAC, name, or type: ").strip()
            show_devices(search_devices(devices, query))
        elif choice == "2":
            field = input("Sort by ip, name, type, or mac [ip]: ").strip().lower() or "ip"
            try:
                show_devices(sort_devices(devices, field))
            except ValueError as error:
                print(f"[!] {error}")
        else:
            print("[!] Invalid option.")


def analyze_network():
    print("\n[*] Detecting network configuration...\n")
    try:
        info = get_network_info()
        subnet_mask = info.get("subnet_mask") or "24"
        network = ipaddress.ip_network(
            f"{info['local_ip']}/{subnet_mask}", strict=False
        )
        print(f"Local IP:      {info['local_ip']}")
        print(f"Subnet:        {network}")
        print(f"Gateway:       {info.get('gateway') or 'unknown'}")
        print(f"Interface:     {info['interface']}")
        if not network.is_private or ipaddress.ip_address(info["local_ip"]) not in network:
            raise ValueError("Scanning is limited to the detected private IPv4 subnet.")
        print("\n[*] Analyzing local network...\n")
        devices = [
            Device.from_dict({
                **item,
                "device_type": (
                    "computer" if item.get("ip") == info.get("local_ip")
                    else "router" if item.get("ip") == info.get("gateway")
                    else item.get("device_type", "unknown")
                ),
            }).to_dict()
            for item in discover_devices(network)
        ]
        print(f"\nDevices found: {len(devices)}\n")
        show_devices(devices)
        graph = create_network_graph(devices, info["local_ip"], info.get("gateway"))
        graph_menu(graph, devices)
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        print(f"\n[!] Network analysis failed: {error}")


def select_vertex(graph, message):
    vertices = graph.get_vertices()
    print("\nAvailable vertices:")
    print(", ".join(map(str, vertices)))
    while True:
        value = input(message).strip()
        match = next((vertex for vertex in vertices
                      if value.casefold() == str(vertex).casefold()), None)
        if match is not None:
            return match
        print("[!] Choose a vertex from the list.")


def run_bfs(graph):
    print("\nBFS traversal:")
    print(" -> ".join(map(str, graph.bfs(select_vertex(graph, "Start vertex: ")))))


def run_dfs(graph):
    print("\nDFS traversal:")
    print(" -> ".join(map(str, graph.dfs(select_vertex(graph, "Start vertex: ")))))


def run_dijkstra(graph):
    start = select_vertex(graph, "Start vertex: ")
    print(f"\nShortest distances from {start}:")
    for vertex, distance in graph.dijkstra(start).items():
        print(f"  {vertex}: {'unreachable' if distance == float('inf') else distance}")


def run_a_star(graph):
    start = select_vertex(graph, "Start vertex: ")
    goal = select_vertex(graph, "Goal vertex: ")
    path, cost = graph.a_star(start, goal)
    if path:
        print("\nA* path:")
        print(" -> ".join(map(str, path)))
        print(f"Total cost: {cost}")
    else:
        print("\n[!] No path found.")


def show_statistics(graph):
    print("\nNetwork statistics")
    print("-" * 30)
    print(f"Vertices: {len(graph.get_vertices())}")
    print(f"Edges:    {len(graph.get_edges())}")
    for vertex in graph.get_vertices():
        print(f"{vertex}: {len(graph.adjacency[vertex])} neighbor(s)")


def graph_menu(graph, devices=None):
    actions = {
        "1": lambda: draw_graph(graph),
        "2": lambda: run_bfs(graph),
        "3": lambda: run_dfs(graph),
        "4": lambda: run_dijkstra(graph),
        "5": lambda: run_a_star(graph),
        "6": lambda: show_statistics(graph),
        "7": lambda: manage_devices(graph, devices),
    }
    while True:
        print_header()
        print("\n1. Show graph in terminal")
        print("2. BFS")
        print("3. DFS")
        print("4. Dijkstra")
        print("5. A*")
        print("6. Network statistics")
        print("7. Search and sort devices")
        print("0. Back")
        choice = input("\nSelect: ").strip()
        if choice == "0":
            return
        action = actions.get(choice)
        if action:
            action()
            if choice != "7":
                pause()
        else:
            print("\n[!] Invalid option.")


def main():
    while True:
        print_header()
        print("\n1. Analyze my network")
        print("0. Exit")
        choice = input("\nSelect: ").strip()
        if choice == "1":
            analyze_network()
            pause()
        elif choice == "0":
            print("\nGoodbye!")
            return
        else:
            print("\n[!] Invalid option.")


if __name__ == "__main__":
    main()
