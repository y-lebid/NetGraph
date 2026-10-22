import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sample_graph import create_sample_graph


class TestDFS(unittest.TestCase):
    def setUp(self):
        self.graph = create_sample_graph()

    def test_visits_reachable_vertices(self):
        result = self.graph.dfs("PC")
        self.assertEqual(result[0], "PC")
        self.assertEqual(set(result), set(self.graph.get_vertices()))

    def test_does_not_visit_disconnected_vertices(self):
        self.graph.add_vertex("Isolated")
        self.assertNotIn("Isolated", self.graph.dfs("PC"))

    def test_unknown_start_raises(self):
        with self.assertRaises(ValueError):
            self.graph.dfs("Unknown")
