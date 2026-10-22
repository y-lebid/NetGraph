from graph import Graph
from models import Connection


def create_network_graph(devices, local_ip, gateway):
    graph = Graph()

    for device in devices:
        ip_address = device.get("ip")
        if ip_address:
            graph.add_vertex(ip_address)

    if local_ip:
        graph.add_vertex(local_ip)

    if gateway:
        graph.add_vertex(gateway)

    def connect(source, destination):
        edge = Connection(source, destination, weight=1)
        graph.add_edge(edge.source, edge.destination, weight=edge.weight)

    if gateway:
        for device in devices:
            ip_address = device.get("ip")
            if ip_address and ip_address != gateway:
                connect(gateway, ip_address)
        if local_ip and local_ip != gateway:
            connect(gateway, local_ip)

    return graph
