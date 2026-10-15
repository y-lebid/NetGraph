import math


def draw_graph(graph):
    vertices = graph.get_vertices()

    if not vertices:
        print("\n[!] Graph is empty.")
        return

    width = 80
    height = max(22, len(vertices) * 3 + 6)
    canvas = [
        [" " for _ in range(width)]
        for _ in range(height)
    ]

    center_x = width // 2
    center_y = height // 2
    radius_x = min(30, width // 2 - 10)
    radius_y = max(5, min(height // 2 - 3, len(vertices) + 3))

    positions = {}

    for index, vertex in enumerate(vertices):
        angle = -math.pi / 2 + (
            2 * math.pi * index / len(vertices)
        )

        x = int(center_x + radius_x * math.cos(angle))
        y = int(center_y + radius_y * math.sin(angle))

        positions[vertex] = (x, y)

    for source, target, weight in graph.get_edges():
        x1, y1 = positions[source]
        x2, y2 = positions[target]

        steps = max(abs(x2 - x1), abs(y2 - y1), 1)

        for step in range(1, steps):
            x = round(x1 + (x2 - x1) * step / steps)
            y = round(y1 + (y2 - y1) * step / steps)

            if 0 <= x < width and 0 <= y < height:
                if canvas[y][x] == " ":
                    canvas[y][x] = "."
                elif canvas[y][x] == ".":
                    canvas[y][x] = "+"

    for vertex, (x, y) in positions.items():
        label = f"[{vertex}]"
        start_x = max(0, min(width - len(label), x - len(label) // 2))

        for offset, char in enumerate(label):
            canvas[y][start_x + offset] = char

    print("\n" + "=" * width)
    print(" " * 27 + "NETGRAPH — GRAPH VIEW")
    print("=" * width)

    for row in canvas:
        print("".join(row).rstrip())

    print("\nEdges and weights:")

    for source, target, weight in graph.get_edges():
        print(f"  {source} -- {target}  (weight: {weight})")

    print("=" * width)
