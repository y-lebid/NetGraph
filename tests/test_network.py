
import sys
from pathlib import Path
import ipaddress
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from network import get_network, get_network_info


class TestNetwork(unittest.TestCase):

    def test_get_network_info_returns_ip_gateway_and_string_types(self):
        expected_info = {
            "interface": "Ethernet",
            "gateway": "192.168.1.1",
            "local_ip": "192.168.1.42",
            "subnet_mask": "255.255.255.0",
        }

        with patch("network.platform.system", return_value="Windows"), patch(
            "network.get_windows_network_info",
            return_value=expected_info,
        ):
            info = get_network_info()

        self.assertEqual(info["local_ip"], "192.168.1.42")
        self.assertEqual(info["gateway"], "192.168.1.1")
        self.assertIsInstance(info["local_ip"], str)
        self.assertIsInstance(info["gateway"], str)
        self.assertIsInstance(info["interface"], str)


    def test_get_network_returns_expected_subnet_and_ip_network_type(self):
        network_info = {
            "interface": "Ethernet",
            "gateway": "192.168.1.1",
            "local_ip": "192.168.1.42",
            "subnet_mask": "255.255.255.0",
        }

        with patch("network.get_network_info", return_value=network_info):
            subnet = get_network()

        self.assertEqual(
            subnet,
            ipaddress.ip_network("192.168.1.0/24"),
        )
        self.assertIsInstance(subnet, ipaddress.IPv4Network)


    def test_get_network_uses_default_slash_24_without_subnet_mask(self):
        network_info = {
            "interface": "eth0",
            "gateway": "10.0.0.1",
            "local_ip": "10.0.0.25",
        }

        with patch("network.get_network_info", return_value=network_info):
            subnet = get_network()

        self.assertEqual(
            subnet,
            ipaddress.ip_network("10.0.0.0/24"),
        )



if __name__ == "__main__":
    print("\n=== NetGraph: Network Tests ===\n")
    unittest.main(verbosity=2)
