"""运营商归属、异步隔离及布局回归；所有网络响应均模拟。"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from monitor_widget import MonitorWidget
from operator_display import operator_text
from operator_lookup import canonical_public_ip, chinese_operator, lookup_operator, _query
from operator_service import OperatorService
from settings_store import SettingsStore
from utils import network_signature


class OperatorLookupTests(unittest.TestCase):
    def test_chinese_names(self):
        examples = {"CHINANET-BACKBONE - No.31": "中国电信", "CHINATELECOM": "中国电信",
                    "CHINA-UNICOM China169 Backbone": "中国联通", "CNCGROUP": "中国联通",
                    "CMNET-GD": "中国移动", "China Mobile Communications": "中国移动",
                    "CERNET-BACKBONE": "中国教育网", "CSTNET-AS": "中国科技网",
                    "EXAMPLE-CMNETWORK": "其他运营商", "Unknown ISP": "其他运营商",
                    "CMNET CHINANET": "其他运营商"}
        for holder, name in examples.items():
            with self.subTest(holder=holder):
                self.assertEqual(chinese_operator(holder), name)

    def test_only_global_unicast(self):
        for address in [None, {}, "获取中…", "10.0.0.1", "127.0.0.1", "192.0.2.1",
                        "224.0.0.1", "::1", "fe80::1", "ff02::1", "2606:4700::1%eth0"]:
            self.assertEqual(canonical_public_ip(address), "")
        self.assertEqual(canonical_public_ip("2001:4860:4860:0:0:0:0:8888"), "2001:4860:4860::8888")

    def test_invalid_never_network(self):
        with patch("operator_lookup.requests.Session") as session:
            self.assertEqual(lookup_operator("192.168.1.1")["status"], "failed")
            session.assert_not_called()

    def test_lookup_success(self):
        with patch("operator_lookup._query", side_effect=[
                {"prefix": "1.1.1.0/24", "asns": ["4134"]},
                {"resource": "4134", "holder": "CHINANET-BACKBONE"}]) as query:
            result = lookup_operator("1.1.1.1")
        self.assertEqual(result["name"], "中国电信")
        self.assertEqual(result["address"], "1.1.1.1")
        self.assertEqual(query.call_args_list[0].args[2], "1.1.1.1")

    def test_mismatched_prefix(self):
        with patch("operator_lookup._query", return_value={"prefix": "8.8.8.0/24", "asns": ["4134"]}):
            self.assertEqual(lookup_operator("1.1.1.1")["status"], "failed")

    def test_malformed_asns(self):
        for asns in [[], None, "4134", [True], [0], [4294967296], [{}], ["AS4134"]]:
            with patch("operator_lookup._query", return_value={"prefix": "1.1.1.0/24", "asns": asns}):
                self.assertEqual(lookup_operator("1.1.1.1")["status"], "failed")

    def test_mismatched_asn(self):
        with patch("operator_lookup._query", side_effect=[
                {"prefix": "1.1.1.0/24", "asns": ["4134"]},
                {"resource": "4837", "holder": "CHINANET"}]):
            self.assertEqual(lookup_operator("1.1.1.1")["status"], "failed")

    def test_multiple_origins(self):
        with patch("operator_lookup._query", return_value={"prefix": "1.1.1.0/24", "asns": [4134, 4837]}):
            self.assertEqual(lookup_operator("1.1.1.1")["name"], "多运营商（归属不唯一）")

    def test_network_failure(self):
        import requests
        with patch("operator_lookup._query", side_effect=requests.Timeout()):
            self.assertEqual(lookup_operator("1.1.1.1")["status"], "failed")

    def test_https_protocol_limits(self):
        session = Mock()
        response = session.get.return_value.__enter__ = Mock()
        session.get.return_value.__exit__ = Mock(return_value=False)
        reply = response.return_value
        reply.status_code = 200
        reply.iter_content.return_value = [b'{"status":"ok","data":{}}']
        self.assertEqual(_query(session, "network-info", "8.8.8.8"), {})
        self.assertFalse(session.get.call_args.kwargs["allow_redirects"])
        for body in [b"x" * 65537, b"[]", b'{"status":"ok","data":[]}', b"not-json"]:
            reply.iter_content.return_value = [body]
            with self.assertRaises(ValueError):
                _query(session, "network-info", "8.8.8.8")

    def test_worker_invalid_input(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(root / "main.py"), "--operator-lookup"],
                                input=b'{"address":"127.0.0.1"}', capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")


class OperatorServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = OperatorService()
        self.launch = patch.object(self.service, "_launch").start()
        self.addCleanup(patch.stopall)
        self.addCleanup(self.service.shutdown)

    def finish(self, address="8.8.8.8", candidate=None, aborted=False, exit_code=0):
        process = Mock()
        process.readAllStandardOutput.return_value = b""
        self.service._active[process] = {"address": address, "timer": Mock(), "aborted": aborted,
                                         "output": bytearray(json.dumps(candidate).encode())}
        self.service._finish(process, exit_code)
        return process

    def candidate(self, address="8.8.8.8"):
        return {"address": address, "status": "ok", "holder": "CHINANET", "asns": [4134], "name": "伪造名称"}

    def test_deduplicate_and_filter(self):
        self.service.request(["8.8.8.8", "8.8.8.8", "127.0.0.1", "未连接公网"])
        self.assertEqual(self.service._pending, ["8.8.8.8"])

    def test_success_cache_and_expiry(self):
        self.service.request(["8.8.8.8"])
        self.finish(candidate=self.candidate())
        self.assertEqual(self.service.get("8.8.8.8")["name"], "中国电信")
        self.service.request(["8.8.8.8"])
        self.assertEqual(self.service._pending, [])
        with patch("operator_service.time.monotonic", return_value=time.monotonic() + 3601):
            self.service.request(["8.8.8.8"])
        self.assertEqual(self.service._pending, ["8.8.8.8"])

    def test_wrong_address_ignored(self):
        self.service.request(["8.8.8.8"])
        self.finish(candidate=self.candidate("1.1.1.1"))
        self.assertEqual(self.service.get("8.8.8.8")["name"], "暂未识别")

    def test_removed_address_not_cached(self):
        self.service.request(["1.1.1.1"])
        self.finish(candidate=self.candidate())
        self.assertNotIn("8.8.8.8", self.service._cache)

    def test_failure_cache_retries(self):
        self.service.request(["8.8.8.8"])
        self.finish(candidate=self.candidate(), aborted=True)
        self.service.request(["8.8.8.8"])
        self.assertEqual(self.service._pending, [])
        with patch("operator_service.time.monotonic", return_value=time.monotonic() + 61):
            self.service.request(["8.8.8.8"])
        self.assertEqual(self.service._pending, ["8.8.8.8"])

    def test_bad_protocol(self):
        for candidate in [[], None, {}, {**self.candidate(), "asns": [True]},
                          {**self.candidate(), "holder": ""}]:
            self.service.request(["8.8.8.8"])
            self.finish(candidate=candidate)
            self.assertEqual(self.service.get("8.8.8.8")["status"], "failed")

    def test_cache_bound(self):
        self.service.MAX_CACHE = 2
        for address in ["1.1.1.1", "8.8.8.8", "9.9.9.9"]:
            self.service.request([address])
            self.finish(address, self.candidate(address))
        self.assertEqual(len(self.service._cache), 2)

    def test_shutdown_kills_without_network_wait(self):
        process = Mock()
        self.service._active[process] = {"timer": Mock(), "address": "8.8.8.8", "aborted": False}
        self.service.shutdown()
        process.kill.assert_called_once()
        process.waitForFinished.assert_called_once_with(200)
        self.service.request(["8.8.8.8"])
        self.assertEqual(self.service._pending, [])
        self.service._active.clear()


class OperatorProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_real_process_queue_timeout_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = Path(directory) / "worker.py"
            worker.write_text(
                'import json, sys, time\n'
                'address = json.load(sys.stdin)["address"]\n'
                'if address == "9.9.9.9": time.sleep(10)\n'
                'print(json.dumps({"address": address, "status": "ok", '
                '"holder": "CHINANET", "asns": [4134]}), flush=True)\n', encoding="utf-8")
            service = OperatorService()
            service.TIMEOUT_MS = 500
            try:
                with patch("operator_service.Path") as path_class:
                    path_class.return_value.with_name.return_value = worker
                    service.request(["8.8.8.8", "1.1.1.1", "9.9.9.9"])
                    self.assertEqual(len(service._active), 2)
                    deadline = time.monotonic() + 4
                    while (service._active or service._pending) and time.monotonic() < deadline:
                        self.assertLessEqual(len(service._active), 2)
                        QTest.qWait(10)
                self.assertFalse(service._active)
                self.assertFalse(service._pending)
                self.assertEqual(service.get("8.8.8.8")["name"], "中国电信")
                self.assertEqual(service.get("1.1.1.1")["name"], "中国电信")
                self.assertEqual(service.get("9.9.9.9")["name"], "暂未识别")
            finally:
                service.shutdown()
                service.deleteLater()


class OperatorWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_dual_stack_and_disconnected(self):
        service = Mock()
        service.get.side_effect = [{"name": "中国电信"}, {"name": "中国联通"}]
        text, tooltip = operator_text(["8.8.8.8", "2001:4860:4860::8888"], service)
        self.assertEqual(text, "IPv4：中国电信\nIPv6：中国联通")
        self.assertIn("8.8.8.8", tooltip)
        service.reset_mock()
        for addresses in (["未连接公网"], ["获取中…"], [], ["192.168.1.1"]):
            self.assertEqual(operator_text(addresses, service)[0], "")
        service.get.assert_not_called()

    def test_multi_interface_live_labels_hotplug_and_font(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch("monitor_widget.PublicIPService"), patch("monitor_widget.DefaultRouteService"), \
                patch("operator_service.OperatorService._launch"):
            interfaces = [{"name": "无线", "ips": ["192.0.2.1"]},
                          {"name": "有线", "ips": ["192.0.2.2"]}]
            store = SettingsStore(QSettings(str(Path(directory) / "settings.ini"), QSettings.IniFormat))
            widget = MonitorWidget(Mock(), lambda: interfaces, store)
            try:
                self.assertTrue(all(rows["operator_container"].isHidden() for rows in widget.network_rows.values()))
                signature = network_signature(interfaces)
                widget.set_public_ips(signature, {"无线": {"status": "ok", "addresses": ["8.8.8.8"]},
                                                   "有线": {"status": "failed", "addresses": []}})
                service = widget.operator_service
                service._cache["8.8.8.8"] = (time.monotonic() + 3600, {"name": "中国电信", "holder": "CHINANET"})
                service.result.emit()
                self.assertEqual(widget.network_rows["无线"]["operator"].text(), "中国电信")
                self.assertFalse(widget.network_rows["无线"]["operator_container"].isHidden())
                self.assertTrue(widget.network_rows["有线"]["operator_container"].isHidden())
                widget.set_public_ips(signature, {"无线": {"status": "ok", "addresses": ["1.1.1.1"]}})
                self.assertEqual(widget.network_rows["无线"]["operator"].text(), "查询中…")
                service.result.emit()
                self.assertEqual(widget.network_rows["无线"]["public"].text(), "1.1.1.1")
                widget.show()
                widget.preview_settings({"font_size": 32})
                self.app.processEvents()
                widget._fit_content()
                self.app.processEvents()
                for rows in widget.network_rows.values():
                    if rows["operator_container"].isHidden():
                        continue
                    label = rows["operator"]
                    self.assertGreaterEqual(label.width(), label.sizeHint().width())
                    self.assertGreaterEqual(label.height(), label.sizeHint().height())
                previous_height = widget.height()
                previous_content_height = widget.content.layout().totalSizeHint().height()
                widget.set_public_ips(signature, {"无线": {"status": "failed", "addresses": []}})
                self.app.processEvents()
                self.assertTrue(widget.network_rows["无线"]["operator_container"].isHidden())
                self.assertLessEqual(widget.height(), previous_height)
                self.assertLess(widget.content.layout().totalSizeHint().height(), previous_content_height)
                widget.set_public_ips(signature, {"无线": {"status": "ok", "addresses": ["8.8.8.8"]}})
                self.app.processEvents()
                self.assertFalse(widget.network_rows["无线"]["operator_container"].isHidden())
                interfaces.pop()
                widget.refresh_network_interfaces()
                self.assertNotIn("operator:有线", widget.labels)
                self.assertTrue(widget.network_rows["无线"]["operator_container"].isHidden())
            finally:
                widget.close()
                widget.deleteLater()


if __name__ == "__main__":
    unittest.main()
