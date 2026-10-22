import json
import unittest
from unittest.mock import call, patch

import network


class TestPlatformAdapters(unittest.TestCase):
    @patch("network.subprocess.run")
    def test_linux_reads_interface_prefix_and_optional_gateway(self, run):
        run.side_effect = [
            type("Result", (), {"stdout": json.dumps([
                {"dev": "eth0", "prefsrc": "10.12.4.20", "gateway": "10.12.4.1"}
            ])})(),
            type("Result", (), {"stdout": json.dumps([
                {"addr_info": [
                    {"family": "inet", "local": "10.12.4.20", "prefixlen": 20}
                ]}
            ])})(),
        ]
        with patch("network.platform.system", return_value="Linux"):
            result = network.get_network_info()
        self.assertEqual(result["interface"], "eth0")
        self.assertEqual(result["gateway"], "10.12.4.1")
        self.assertEqual(result["subnet_mask"], "255.255.240.0")
        run.assert_has_calls([
            call(["ip", "-j", "route", "get", "8.8.8.8"],
                 capture_output=True, text=True, check=True),
            call(["ip", "-j", "address", "show", "dev", "eth0"],
                 capture_output=True, text=True, check=True),
        ])

    @patch("network.subprocess.run")
    def test_windows_uses_locale_independent_powershell_json(self, run):
        run.return_value.stdout = json.dumps({
            "InterfaceAlias": "Ethernet",
            "LocalIP": "192.168.9.10",
            "PrefixLength": 23,
            "Gateway": "192.168.8.1",
        })
        with patch("network.platform.system", return_value="Windows"):
            result = network.get_network_info()
        self.assertEqual(result["local_ip"], "192.168.9.10")
        self.assertEqual(result["subnet_mask"], "255.255.254.0")
        self.assertEqual(result["gateway"], "192.168.8.1")
        args = run.call_args.args[0]
        self.assertEqual(args[:3], ["powershell.exe", "-NoProfile", "-NonInteractive"])
        self.assertIn("ConvertTo-Json", args[-1])

    @patch("network.subprocess.run")
    def test_linux_detects_real_subnet_instead_of_assuming_slash_24(self, run):
        run.side_effect = [
            type("Result", (), {"stdout": '[{"dev":"eth0","src":"10.12.4.20"}]'})(),
            type("Result", (), {"stdout": '[{"addr_info":[{"family":"inet","local":"10.12.4.20","prefixlen":20}]}]'})(),
        ]
        with patch("network.platform.system", return_value="Linux"), patch(
            "network.get_linux_network_info", wraps=network.get_linux_network_info
        ):
            subnet = network.get_network()
        self.assertEqual(str(subnet), "10.12.0.0/20")


if __name__ == "__main__":
    unittest.main()
