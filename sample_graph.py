from graph import Graph


def create_sample_graph():
    graph = Graph()
    graph.add_edge("PC", "Router", 2)
    graph.add_edge("Router", "Switch", 1)
    graph.add_edge("Switch", "Server", 3)
    graph.add_edge("Router", "Laptop", 4)
    graph.add_edge("Laptop", "Server", 2)
    graph.add_edge("PC", "Laptop", 5)
    return graph


