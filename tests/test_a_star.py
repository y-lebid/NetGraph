import sys
from pathlib import Path
import unittest
from math import inf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sample_graph import create_sample_graph


class TestAStar(unittest.TestCase):
    def setUp(self):
        self.graph = create_sample_graph()

    def test_finds_shortest_path(self):
        path, cost = self.graph.a_star("PC", "Server")
        self.assertEqual(path, ["PC", "Router", "Switch", "Server"])
        self.assertEqual(cost, 6)

    def test_zero_heuristic_finds_shortest_cost(self):
        path, cost = self.graph.a_star("PC", "Server", heuristic=lambda vertex, goal: 0)
        self.assertEqual((path[0], path[-1], cost), ("PC", "Server", 6))

    def test_unreachable_goal_returns_empty_path(self):
        self.graph.add_vertex("Isolated")
        self.assertEqual(self.graph.a_star("PC", "Isolated"), ([], inf))

    def test_unknown_endpoint_raises(self):
        with self.assertRaises(ValueError):
            self.graph.a_star("PC", "Unknown")
