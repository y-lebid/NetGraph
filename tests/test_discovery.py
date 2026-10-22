
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from discovery import ping_host, parse_arp_table


class TestPingHost(unittest.TestCase):

    @patch("discovery.platform.system", return_value="Windows")
    @patch("discovery.subprocess.run")
    def test_ping_success(self, mock_run, mock_system):
        mock_run.return_value.returncode = 0

        result = ping_host("192.168.0.1")

        self.assertTrue(result)

    @patch("discovery.platform.system", return_value="Windows")
    @patch("discovery.subprocess.run")
    def test_ping_failure(self, mock_run, mock_system):
        mock_run.return_value.returncode = 1

        result = ping_host("192.168.0.100")

        self.assertFalse(result)


class TestArpParser(unittest.TestCase):

    def test_parse_windows_arp_table(self):
        arp_output = """
Interface: 192.168.0.233 --- 0x8
  Internet Address      Physical Address      Type
  192.168.0.1           aa-bb-cc-dd-ee-ff     dynamic
  192.168.0.110         11-22-33-44-55-66     dynamic
  192.168.0.233         77-88-99-aa-bb-cc     dynamic
"""

        result = parse_arp_table(arp_output)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["ip"], "192.168.0.1")
        self.assertEqual(result[0]["mac"], "aa-bb-cc-dd-ee-ff")


    def test_parse_empty_arp_table(self):
        result = parse_arp_table("")

        self.assertEqual(result, [])


    def test_rejects_subnet_above_scan_limit(self):
        import ipaddress
        from discovery import discover_devices

        with self.assertRaises(ValueError):
            discover_devices(ipaddress.ip_network("10.0.0.0/16"))


if __name__ == "__main__":
    print("\n=== NetGraph: Discovery Tests ===\n")
    unittest.main(verbosity=2)
