from graph import Graph


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
        
    if local_ip and gateway and local_ip != gateway:
        graph.add_edge(local_ip, gateway, weight=1)

    return graph
