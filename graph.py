
from collections import deque
from math import inf


class Graph:

    def __init__(self, directed=False):
        self.directed = directed
        self.adjacency = {}

    def add_vertex(self, vertex):
        if vertex not in self.adjacency:
            self.adjacency[vertex] = {}

    def add_edge(self, source, target, weight=1):
        if weight < 0:
            raise ValueError("Edge weight cannot be negative")

        self.add_vertex(source)
        self.add_vertex(target)

        self.adjacency[source][target] = weight

        if not self.directed:
            self.adjacency[target][source] = weight

    def get_vertices(self):
        return list(self.adjacency)

    def get_edges(self):
        edges = []

        for source, neighbors in self.adjacency.items():
            for target, weight in neighbors.items():
                if self.directed or (target, source) not in edges:
                    edges.append((source, target, weight))

        return edges

    def bfs(self, start):
        if start not in self.adjacency:
            raise ValueError(f"Unknown vertex: {start}")

        visited = {start}
        queue = deque([start])
        order = []

        while queue:
            vertex = queue.popleft()
            order.append(vertex)

            for neighbor in self.adjacency[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def dfs(self, start):
        if start not in self.adjacency:
            raise ValueError(f"Unknown vertex: {start}")

        visited = set()
        order = []

        def visit(vertex):
            visited.add(vertex)
            order.append(vertex)

            for neighbor in self.adjacency[vertex]:
                if neighbor not in visited:
                    visit(neighbor)

        visit(start)
        return order

    def dijkstra(self, start):
        if start not in self.adjacency:
            raise ValueError(f"Unknown vertex: {start}")

        distances = {vertex: inf for vertex in self.adjacency}
        distances[start] = 0
        unvisited = set(self.adjacency)

        while unvisited:
            current = min(
                unvisited,
                key=lambda vertex: distances[vertex],
            )

            if distances[current] == inf:
                break

            unvisited.remove(current)

            for neighbor, weight in self.adjacency[current].items():
                if neighbor not in unvisited:
                    continue

                new_distance = distances[current] + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance

        return distances
