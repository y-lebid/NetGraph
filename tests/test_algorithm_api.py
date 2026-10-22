import asyncio
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import web_app
from sample_graph import create_sample_graph


class TestAlgorithmAPI(unittest.TestCase):
    def setUp(self):
        self.graph = create_sample_graph()
        self.request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))
        self.temp_dir = tempfile.TemporaryDirectory()
        self.graph_patch = patch.object(web_app, "_graph", self.graph)
        self.base_patch = patch.object(web_app, "BASE_DIR", Path(self.temp_dir.name))
        self.graph_patch.start()
        self.base_patch.start()

    def tearDown(self):
        self.base_patch.stop()
        self.graph_patch.stop()
        self.temp_dir.cleanup()

    def _run(self, endpoint, payload):
        return asyncio.run(endpoint(self.request, payload))

    def _assert_report(self, result, algorithm):
        self.assertGreaterEqual(result["runtime_ms"], 0)
        report = Path(self.temp_dir.name) / "test log" / result["report"]
        self.assertTrue(report.is_file())
        self.assertIn(f"# {algorithm} benchmark", report.read_text(encoding="utf-8"))

    def test_bfs_response_contains_order_runtime_and_markdown_report(self):
        result = self._run(web_app.bfs, {"start": "PC"})
        self.assertEqual(result["order"][0], "PC")
        self._assert_report(result, "bfs")

    def test_dfs_response_contains_order_runtime_and_markdown_report(self):
        result = self._run(web_app.dfs, {"start": "PC"})
        self.assertEqual(result["order"][0], "PC")
        self._assert_report(result, "dfs")

    def test_dijkstra_response_contains_distances_runtime_and_markdown_report(self):
        result = self._run(web_app.dijkstra, {"start": "PC"})
        self.assertEqual(result["distances"]["Server"], 6)
        self._assert_report(result, "dijkstra")

    def test_a_star_response_contains_path_runtime_and_markdown_report(self):
        result = self._run(web_app.a_star, {"start": "PC", "goal": "Server"})
        self.assertEqual(result["path"][0], "PC")
        self._assert_report(result, "a-star")
