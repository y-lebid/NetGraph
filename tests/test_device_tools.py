import unittest

from models import Connection, Device
from search import search_devices
from sorting import sort_devices


class TestDeviceTools(unittest.TestCase):
    def setUp(self):
        self.devices = [
            Device("192.168.1.12", "aa:00:00:00:00:12", "Laptop", "computer").to_dict(),
            Device("192.168.1.2", "aa:00:00:00:00:02", "Router", "router").to_dict(),
            Device("192.168.1.3", None, "Phone", "unknown").to_dict(),
        ]

    def test_search_matches_ip_mac_name_and_type(self):
        self.assertEqual(search_devices(self.devices, "192.168.1.2"), [self.devices[1]])
        self.assertEqual(search_devices(self.devices, "AA:00:00:00:00:12"), [self.devices[0]])
        self.assertEqual(search_devices(self.devices, "phone"), [self.devices[2]])
        self.assertEqual(search_devices(self.devices, "router"), [self.devices[1]])

    def test_ip_sort_is_numeric(self):
        result = sort_devices(self.devices, "ip")
        self.assertEqual([item["ip"] for item in result],
                         ["192.168.1.2", "192.168.1.3", "192.168.1.12"])

    def test_text_sorts_and_invalid_field(self):
        self.assertEqual(sort_devices(self.devices, "name")[0]["name"], "Laptop")
        with self.assertRaises(ValueError):
            sort_devices(self.devices, "unsupported")

    def test_connection_model_serializes(self):
        self.assertEqual(
            Connection("a", "b", 2).to_dict(),
            {"source": "a", "destination": "b", "weight": 2},
        )


if __name__ == "__main__":
    unittest.main()
