import sys
from pathlib import Path
import unittest
from math import inf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sample_graph import create_sample_graph


class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.graph = create_sample_graph()

    def test_finds_shortest_distances(self):
        distances = self.graph.dijkstra("PC")
        self.assertEqual(distances["PC"], 0)
        self.assertEqual(distances["Router"], 2)
        self.assertEqual(distances["Switch"], 3)
        self.assertEqual(distances["Laptop"], 5)
        self.assertEqual(distances["Server"], 6)

    def test_unreachable_vertex_has_infinite_distance(self):
        self.graph.add_vertex("Isolated")
        self.assertEqual(self.graph.dijkstra("PC")["Isolated"], inf)

    def test_unknown_start_raises(self):
        with self.assertRaises(ValueError):
            self.graph.dijkstra("Unknown")

    def test_negative_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            self.graph.add_edge("PC", "Server", -1)
