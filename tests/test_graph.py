
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sample_graph import create_sample_graph


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = create_sample_graph()

    def test_bfs_visits_all_vertices(self):
        result = self.graph.bfs("PC")

        self.assertEqual(result[0], "PC")
        self.assertEqual(set(result), set(self.graph.get_vertices()))

    def test_dfs_visits_all_vertices(self):
        result = self.graph.dfs("PC")

        self.assertEqual(result[0], "PC")
        self.assertEqual(set(result), set(self.graph.get_vertices()))

    def test_dijkstra_finds_shortest_distances(self):
        distances = self.graph.dijkstra("PC")

        self.assertEqual(distances["PC"], 0)
        self.assertEqual(distances["Router"], 2)
        self.assertEqual(distances["Switch"], 3)
        self.assertEqual(distances["Laptop"], 5)
        self.assertEqual(distances["Server"], 6)

    def test_unknown_vertex_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.bfs("Unknown")

    def test_negative_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            self.graph.add_edge("PC", "Server", -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
