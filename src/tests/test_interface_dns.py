"""公网 DNS 回归：使用模拟 DNS/HTTP，保证系统解析回退不改变网卡绑定。"""

from pathlib import Path
import socket
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dns.exception
import dns.rdatatype
import dns.resolver

from interface_dns import resolve_interface_host
from public_ip_lookup import SourceAddressAdapter, lookup_interface, query_endpoints


class InterfaceDNSTests(unittest.TestCase):
    def setUp(self):
        self.resolver = MagicMock()
        self.resolver.nameservers = ["100.100.100.100"]
        self.resolver.resolve.return_value = [SimpleNamespace(address="203.0.113.10")]
        self.resolver_patch = patch("interface_dns.dns.resolver.Resolver", return_value=self.resolver)
        self.resolver_patch.start()
        self.addCleanup(self.resolver_patch.stop)
        self.socket_patch = patch("interface_dns.socket.socket")
        self.transport = self.socket_patch.start().return_value.__enter__.return_value
        self.addCleanup(self.socket_patch.stop)
        self.udp_patch = patch("interface_dns.dns.query.udp", side_effect=dns.exception.Timeout)
        self.udp = self.udp_patch.start()
        self.addCleanup(self.udp_patch.stop)

    def test_vpn_dns_falls_back_without_unbinding_https(self):
        result = resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6)
        self.assertEqual(result, ["203.0.113.10"])
        self.transport.setsockopt.assert_called_with(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"wifi\0")
        self.transport.bind.assert_called_once_with(("192.0.2.10", 0))
        self.resolver.resolve.assert_called_once()
        self.assertFalse(self.resolver.resolve.call_args.kwargs["search"])
        self.assertLessEqual(self.udp.call_args.kwargs["timeout"], 0.3)
        self.assertLessEqual(self.resolver.resolve.call_args.kwargs["lifetime"], 0.6)

    def test_bound_dns_success_does_not_use_system_fallback(self):
        self.udp.side_effect = None
        with patch("interface_dns.dns.resolver.Answer", return_value=[SimpleNamespace(address="203.0.113.20")]):
            self.assertEqual(resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6), ["203.0.113.20"])
        self.resolver.resolve.assert_not_called()

    def test_loopback_dns_uses_bounded_resolver_not_getaddrinfo(self):
        self.resolver.nameservers = ["127.0.0.53"]
        with patch("interface_dns.socket.getaddrinfo", side_effect=AssertionError("不应阻塞系统解析")):
            resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6)
        self.udp.assert_not_called()
        self.resolver.resolve.assert_called_once()

    def test_ipv6_record_can_use_ipv4_dns_transport(self):
        self.resolver.nameservers = ["192.0.2.53"]
        self.resolver.resolve.return_value = [SimpleNamespace(address="2001:db8::10")]
        self.assertEqual(resolve_interface_host("api64.ipify.org", "2001:db8::2", "wifi", 0.6), ["2001:db8::10"])
        self.udp.assert_not_called()
        self.assertEqual(self.resolver.resolve.call_args.args[1], dns.rdatatype.AAAA)

    def test_all_dns_fail(self):
        self.resolver.resolve.side_effect = dns.resolver.LifetimeTimeout(timeout=0.6, errors=[])
        with self.assertRaises(socket.gaierror):
            resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6)

    def test_expired_budget_does_not_query(self):
        with self.assertRaises(socket.gaierror):
            resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0)
        self.udp.assert_not_called()
        self.resolver.resolve.assert_not_called()

    def test_exhausted_bound_budget_does_not_extend_deadline(self):
        with patch("interface_dns.time.monotonic", side_effect=[0, 0, 0, 1]):
            with self.assertRaises(socket.gaierror):
                resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6)
        self.resolver.resolve.assert_not_called()

    def test_socket_error_still_tries_system_dns(self):
        self.transport.bind.side_effect = OSError("绑定失败")
        self.assertEqual(resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6), ["203.0.113.10"])
        self.udp.assert_not_called()

    def test_response_deduplicated(self):
        self.resolver.resolve.return_value = [SimpleNamespace(address="203.0.113.10")] * 2
        self.assertEqual(resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6), ["203.0.113.10"])

    def test_bad_resolver_config_becomes_connection_error(self):
        with patch("interface_dns.dns.resolver.Resolver", side_effect=dns.resolver.NoResolverConfiguration):
            with self.assertRaises(socket.gaierror):
                resolve_interface_host("api.ipify.org", "192.0.2.10", "wifi", 0.6)


class PublicIPIsolationTests(unittest.TestCase):
    def test_adapter_keeps_device_source_and_tls_host(self):
        adapter = SourceAddressAdapter("192.0.2.10", "wifi")
        connection_class = adapter.poolmanager.pool_classes_by_scheme["https"].ConnectionCls
        connection = connection_class("api.ipify.org", timeout=0.6,
                                      source_address=adapter.poolmanager.connection_pool_kw["source_address"],
                                      socket_options=adapter.poolmanager.connection_pool_kw["socket_options"])
        with patch("public_ip_lookup.resolve_interface_host", return_value=["203.0.113.10"]), \
                patch("public_ip_lookup.HTTPSConnection._new_conn", return_value=object()) as connect:
            connection._new_conn()
        self.assertEqual(connection.source_address, ("192.0.2.10", 0))
        self.assertIn((socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"wifi\0"), connection.socket_options)
        self.assertEqual(connection.host, "api.ipify.org")
        self.assertEqual(connection._dns_host, "api.ipify.org")
        connect.assert_called_once()
        adapter.close()

    def test_proxy_environment_remains_disabled(self):
        with patch("public_ip_lookup.requests.Session") as session_class, \
                patch("public_ip_lookup.time.monotonic", return_value=1):
            session = session_class.return_value.__enter__.return_value
            response = session.get.return_value.__enter__.return_value
            response.status_code = 200
            response.iter_content.return_value = [b"8.8.8.8"]
            self.assertEqual(query_endpoints("192.0.2.10", 2, interface_name="wifi"), "8.8.8.8")
        self.assertFalse(session.trust_env)
        self.assertFalse(session.get.call_args.kwargs["allow_redirects"])

    def test_failed_interface_never_borrows_another_public_ip(self):
        with patch("public_ip_lookup.query_endpoints", return_value=None) as query:
            self.assertEqual(lookup_interface({"name": "vmnet1", "ips": ["192.0.2.10"]}),
                             {"status": "failed", "addresses": []})
        self.assertEqual(query.call_args.args[3], "vmnet1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
