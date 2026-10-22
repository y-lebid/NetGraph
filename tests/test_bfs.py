import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sample_graph import create_sample_graph


class TestBFS(unittest.TestCase):
    def setUp(self):
        self.graph = create_sample_graph()

    def test_visits_reachable_vertices_in_breadth_first_order(self):
        self.assertEqual(self.graph.bfs("PC"), ["PC", "Router", "Laptop", "Switch", "Server"])

    def test_does_not_visit_disconnected_vertices(self):
        self.graph.add_vertex("Isolated")
        self.assertNotIn("Isolated", self.graph.bfs("PC"))

    def test_unknown_start_raises(self):
        with self.assertRaises(ValueError):
            self.graph.bfs("Unknown")
