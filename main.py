
from network import get_network_info, get_network
from discovery import discover_devices
from sample_graph import create_sample_graph
from terminal_graph import draw_graph


def print_header():
    print("╔══════════════════════════╗")
    print("║         NetGraph         ║")
    print("╚══════════════════════════╝")


def pause():
    input("\nPress Enter to continue...")


def analyze_network():
    print("\n[*] Detecting network configuration...\n")

    try:
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

    except (OSError, RuntimeError, ValueError, KeyError) as error:
        print(f"\n[!] Network analysis failed: {error}")



def select_vertex(graph, message):
    vertices = graph.get_vertices()

    print("\nAvailable vertices:")
    print(", ".join(vertices))

    while True:
        value = input(message).strip()

        if not value:
            print("[!] Input cannot be empty. Try again.")
            continue

        for vertex in vertices:
            if value.casefold() == str(vertex).casefold():
                return vertex

        print(f"[!] Unknown vertex: {value}")
        print("Please choose a vertex from the list.")



def run_bfs(graph):
    start = select_vertex(graph, "Start vertex: ")

    if start is not None:
        print("\nBFS traversal:")
        print(" -> ".join(graph.bfs(start)))


def run_dfs(graph):
    start = select_vertex(graph, "Start vertex: ")

    if start is not None:
        print("\nDFS traversal:")
        print(" -> ".join(graph.dfs(start)))


def run_dijkstra(graph):
    start = select_vertex(graph, "Start vertex: ")

    if start is None:
        return

    print(f"\nShortest distances from {start}:")

    for vertex, distance in graph.dijkstra(start).items():
        if distance == float("inf"):
            print(f"  {vertex}: unreachable")
        else:
            print(f"  {vertex}: {distance}")


def run_a_star(graph):
    start = select_vertex(graph, "Start vertex: ")

    if start is None:
        return

    goal = select_vertex(graph, "Goal vertex: ")

    if goal is None:
        return

    path, cost = graph.a_star(start, goal)

    if path:
        print("\nA* path:")
        print(" -> ".join(path))
        print(f"Total cost: {cost}")
    else:
        print("\n[!] No path found.")


def show_statistics(graph):
    vertices = graph.get_vertices()
    edges = graph.get_edges()

    print("\nNetwork statistics")
    print("-" * 30)
    print(f"Vertices: {len(vertices)}")
    print(f"Edges:    {len(edges)}")

    for vertex in vertices:
        neighbors = graph.adjacency[vertex]
        print(f"{vertex}: {len(neighbors)} neighbor(s)")


def graph_menu(graph):
    while True:
        print()
        print_header()

        print("\n1. Show graph in terminal")
        print("2. BFS")
        print("3. DFS")
        print("4. Dijkstra")
        print("5. A*")
        print("6. Network statistics")
        print("0. Back")

        choice = input("\nSelect: ").strip()

        if choice == "1":
            draw_graph(graph)
            pause()

        elif choice == "2":
            run_bfs(graph)
            pause()

        elif choice == "3":
            run_dfs(graph)
            pause()

        elif choice == "4":
            run_dijkstra(graph)
            pause()

        elif choice == "5":
            run_a_star(graph)
            pause()

        elif choice == "6":
            show_statistics(graph)
            pause()

        elif choice == "0":
            break

        else:
            print("\n[!] Invalid option.")
            pause()


def main():
    while True:
        print()
        print_header()

        print("\n1. Analyze my network")
        print("2. Load sample network")
        print("3. Generate test network")
        print("0. Exit")

        choice = input("\nSelect: ").strip()

        if choice == "1":
            analyze_network()
            pause()

        elif choice == "2":
            graph = create_sample_graph()
            graph_menu(graph)

        elif choice == "3":
            print("\n[*] Generating test network...")
            graph = create_sample_graph()
            print("[+] Test network generated.")
            graph_menu(graph)

        elif choice == "0":
            print("\nGoodbye!")
            break

        else:
            print("\n[!] Invalid option.")
            pause()


if __name__ == "__main__":
    main()
