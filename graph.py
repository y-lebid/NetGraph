import heapq
from itertools import count
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

    
    def a_star(self, start, goal, heuristic=None):
        if start not in self.adjacency:
            raise ValueError(f"Unknown vertex: {start}")

        if goal not in self.adjacency:
            raise ValueError(f"Unknown vertex: {goal}")

        if heuristic is None:
            heuristic = lambda vertex, target: 0

        distances = {
            vertex: inf
            for vertex in self.adjacency
        }
        distances[start] = 0

        previous = {start: None}
        counter = count()

        priority_queue = [
            (heuristic(start, goal), 0, next(counter), start)
        ]

        while priority_queue:
            _, current_distance, _, current = heapq.heappop(
                priority_queue
            )

            if current_distance > distances[current]:
                continue

            if current == goal:
                path = []
                vertex = goal

                while vertex is not None:
                    path.append(vertex)
                    vertex = previous[vertex]

                path.reverse()
                return path, current_distance

            for neighbor, weight in self.adjacency[current].items():
                new_distance = current_distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current

                    estimated_total = (
                        new_distance + heuristic(neighbor, goal)
                    )

                    heapq.heappush(
                        priority_queue,
                        (
                            estimated_total,
                            new_distance,
                            next(counter),
                            neighbor,
                        ),
                    )

        return [], inf



        