"""策略路由判定回归：模拟 Tailscale/出口节点规则，不操作系统网络。"""

import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from route_policy import policy_allows_main, table_preserves_default


def tailscale_rules():
    return [
        {"priority": 0, "src": "all", "table": "local"},
        {"priority": 5210, "src": "all", "fwmark": "0x80000", "fwmask": "0xff0000", "table": "main"},
        {"priority": 5230, "src": "all", "fwmark": "0x80000", "fwmask": "0xff0000", "table": "default"},
        {"priority": 5250, "src": "all", "fwmark": "0x80000", "fwmask": "0xff0000", "action": "unreachable"},
        {"priority": 5270, "src": "all", "table": "52"},
        {"priority": 32766, "src": "all", "table": "main"},
        {"priority": 32767, "src": "all", "table": "default"},
    ]


class RoutePolicyTests(unittest.TestCase):
    def test_standard_rules_need_no_extra_query(self):
        read = Mock()
        rules = [{"priority": 0, "table": 255}, {"priority": 32766, "table": 254}]
        self.assertTrue(policy_allows_main(rules, read, 4))
        read.assert_not_called()

    def test_tailscale_peer_and_dns_routes_allowed(self):
        read = Mock(return_value=[{"dst": "100.64.0.2", "dev": "tailscale0"},
                                  {"dst": "100.100.100.100", "dev": "tailscale0"}])
        rules = tailscale_rules()
        original = copy.deepcopy(rules)
        self.assertTrue(policy_allows_main(rules, read, 4))
        self.assertEqual(rules, original)
        read.assert_called_once_with("52")

    def test_tailscale_ipv6_private_routes_allowed(self):
        read = Mock(return_value=[{"dst": "fd7a:115c:a1e0::/48", "dev": "tailscale0"}])
        self.assertTrue(policy_allows_main(tailscale_rules(), read, 6))

    def test_exit_node_default_rejected(self):
        for destination in ("default", "0.0.0.0/0", "::/0"):
            with self.subTest(destination=destination):
                read = Mock(return_value=[{"dst": destination, "dev": "tailscale0"}])
                self.assertFalse(policy_allows_main(tailscale_rules(), read, 6 if ":" in destination else 4))

    def test_split_default_rejected(self):
        for destinations, version in [(["0.0.0.0/1", "128.0.0.0/1"], 4), (["::/1", "8000::/1"], 6)]:
            read = Mock(return_value=[{"dst": destination} for destination in destinations])
            self.assertFalse(policy_allows_main(tailscale_rules(), read, version))

    def test_four_quarters_covering_default_rejected(self):
        routes = [{"dst": f"{prefix}.0.0.0/2"} for prefix in (0, 64, 128, 192)]
        self.assertFalse(table_preserves_default(routes, 4))

    def test_subnet_routes_preserved(self):
        read = Mock(return_value=[{"dst": "10.10.0.0/16"}, {"dst": "203.0.113.0/24"}])
        self.assertTrue(policy_allows_main(tailscale_rules(), read, 4))

    def test_empty_policy_table_allowed(self):
        self.assertTrue(policy_allows_main(tailscale_rules(), Mock(return_value=[]), 4))

    def test_mark_zero_unreachable_rejected(self):
        rules = tailscale_rules()
        rules[3]["fwmark"] = "0x0"
        self.assertFalse(policy_allows_main(rules, Mock(), 4))

    def test_inverted_mark_rejected(self):
        rules = tailscale_rules()
        rules[1]["not"] = True
        self.assertFalse(policy_allows_main(rules, Mock(), 4))

    def test_source_based_rule_rejected(self):
        rules = tailscale_rules()
        rules[4]["src"] = "192.0.2.0/24"
        self.assertFalse(policy_allows_main(rules, Mock(), 4))

    def test_suppress_prefix_rule_rejected(self):
        rules = [{"priority": 100, "table": "main", "suppress_prefixlength": 0}]
        self.assertFalse(policy_allows_main(rules, Mock(), 4))

    def test_no_unmarked_main_lookup_rejected(self):
        self.assertFalse(policy_allows_main(tailscale_rules()[:4], Mock(), 4))

    def test_policy_after_main_not_relevant(self):
        read = Mock()
        rules = [{"priority": 100, "table": "main"}, {"priority": 200, "action": "unreachable"}]
        self.assertTrue(policy_allows_main(rules, read, 4))
        read.assert_not_called()

    def test_table_lookup_cached(self):
        rules = tailscale_rules()
        rules.insert(5, {"priority": 5271, "table": 52})
        read = Mock(return_value=[])
        self.assertTrue(policy_allows_main(rules, read, 4))
        read.assert_called_once_with("52")

    def test_table_read_failure_not_ignored(self):
        with self.assertRaises(OSError):
            policy_allows_main(tailscale_rules(), Mock(side_effect=OSError("读取失败")), 4)

    def test_throw_default_falls_through(self):
        read = Mock(return_value=[{"dst": "default", "type": "throw"}])
        self.assertTrue(policy_allows_main(tailscale_rules(), read, 4))

    def test_blackhole_default_rejected(self):
        read = Mock(return_value=[{"dst": "default", "type": "blackhole"}])
        self.assertFalse(policy_allows_main(tailscale_rules(), read, 4))

    def test_malformed_inputs_rejected(self):
        for rules in (None, [], [None], [{"table": "main"}], [{"priority": -1, "table": "main"}]):
            with self.subTest(rules=rules):
                self.assertFalse(policy_allows_main(rules, Mock(), 4))
        for routes in (None, [None], [{"dst": "invalid"}], [{"dst": "::/64"}]):
            with self.subTest(routes=routes):
                self.assertFalse(table_preserves_default(routes, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
