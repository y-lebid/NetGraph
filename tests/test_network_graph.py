import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from network_graph import create_network_graph


class TestNetworkGraph(unittest.TestCase):
    def test_connects_all_discovered_devices_to_router(self):
        devices = [{"ip": "192.168.1.10"}, {"ip": "192.168.1.11"}]
        graph = create_network_graph(devices, "192.168.1.10", "192.168.1.1")

        self.assertEqual(set(graph.adjacency["192.168.1.1"]), {"192.168.1.10", "192.168.1.11"})
        self.assertEqual(graph.bfs("192.168.1.1"), ["192.168.1.1", "192.168.1.10", "192.168.1.11"])

    def test_without_gateway_devices_remain_vertices(self):
        graph = create_network_graph([{"ip": "192.168.1.10"}], "192.168.1.10", None)
        self.assertEqual(graph.get_vertices(), ["192.168.1.10"])


if __name__ == "__main__":
    unittest.main()
