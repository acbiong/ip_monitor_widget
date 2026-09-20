"""公网刷新配置及定时更新回归，全程使用临时配置和模拟查询服务。"""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt5.QtCore import QByteArray, QObject, QSettings, pyqtSignal
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from config import DEFAULT_SETTINGS
from monitor_widget import MonitorWidget
from settings_dialog import SettingsDialog
from settings_store import SettingsStore, normalize_settings
from utils import network_signature


class FakePublicService(QObject):
    result = pyqtSignal(object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calls = 0
        self.stopped = False

    def request(self, interfaces):
        self.calls += 1
        address = "8.8.8.8" if self.calls == 1 else "1.1.1.1"
        self.result.emit(network_signature(interfaces), {
            item["name"]: {"status": "ok", "addresses": [address]} for item in interfaces})

    def shutdown(self):
        self.stopped = True


class FakeRouteService(QObject):
    result = pyqtSignal(object)

    def refresh(self):
        pass

    def shutdown(self):
        pass


class PublicIntervalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = str(Path(self.directory.name) / "settings.ini")
        self.store = SettingsStore(QSettings(self.path, QSettings.IniFormat))

    def widget(self):
        with patch("monitor_widget.PublicIPService", FakePublicService), \
                patch("monitor_widget.DefaultRouteService", FakeRouteService):
            widget = MonitorWidget(Mock(), network_provider=lambda: [{"name": "fixture", "ips": ["192.0.2.1"]}],
                                   settings_store=self.store)
        self.app.processEvents()
        self.addCleanup(widget.deleteLater)
        self.addCleanup(widget.close)
        return widget

    def test_legacy_settings_default(self):
        self.store.settings.setValue("font_size", 20)
        values = self.store.load()
        self.assertEqual(values["font_size"], 20)
        self.assertEqual(values["public_ip_interval"], 60)

    def test_bounds_and_invalid_values(self):
        for value, expected in [(1, 10), (0, 10), (9999, 3600), ("120", 120),
                                (None, 60), ("invalid", 60), (float("nan"), 60), (float("inf"), 60)]:
            with self.subTest(value=value):
                self.assertEqual(normalize_settings({"public_ip_interval": value})["public_ip_interval"], expected)

    def test_persist_and_restart_timer(self):
        self.store.save({**DEFAULT_SETTINGS, "public_ip_interval": 120}, QByteArray())
        reloaded = SettingsStore(QSettings(self.path, QSettings.IniFormat))
        self.assertEqual(reloaded.load()["public_ip_interval"], 120)
        self.assertEqual(self.widget().public_timer.interval(), 120000)

    def test_preview_and_cancel_restore_timer(self):
        widget = self.widget()
        original = dict(widget.values)
        geometry = widget.saveGeometry()
        widget.preview_settings({"public_ip_interval": 10})
        self.assertEqual(widget.public_timer.interval(), 10000)
        self.assertEqual(self.store.load()["public_ip_interval"], 60)
        widget.restore_settings_preview(original, geometry)
        self.assertEqual(widget.public_timer.interval(), 60000)

    def test_other_previews_do_not_restart_public_timer(self):
        widget = self.widget()
        with patch.object(widget.public_timer, "setInterval", wraps=widget.public_timer.setInterval) as setter:
            widget.preview_settings({"opacity": 0.6})
            widget.preview_settings({"interval": 2000})
            widget.preview_settings({"font_size": 20})
            setter.assert_not_called()

    def test_save_applies_and_persists(self):
        widget = self.widget()
        widget.apply_settings({"public_ip_interval": 3600})
        self.assertEqual(widget.public_timer.interval(), 3600000)
        self.assertEqual(self.store.load()["public_ip_interval"], 3600)

    def test_defaults_emit_once_and_restore_interval(self):
        dialog = SettingsDialog({**DEFAULT_SETTINGS, "public_ip_interval": 120}, DEFAULT_SETTINGS)
        self.addCleanup(dialog.deleteLater)
        signals = []
        dialog.preview_changed.connect(signals.append)
        dialog.restore_defaults()
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["public_ip_interval"], 60)
        self.assertEqual(dialog.public_ip_interval.minimum(), 10)
        self.assertEqual(dialog.public_ip_interval.maximum(), 3600)

    def test_unchanged_local_ip_still_refreshes_public_ip(self):
        widget = self.widget()
        self.assertEqual(widget.public_ips["fixture"], ["8.8.8.8"])
        original_signature = widget.network_signature
        # 仅加速测试时钟，生产定时器仍使用经校验的秒数。
        widget.public_timer.setInterval(20)
        for attempt in range(30):
            QTest.qWait(10)
            if widget.public_ip_service.calls >= 2:
                break
        self.assertGreaterEqual(widget.public_ip_service.calls, 2)
        self.assertEqual(widget.network_signature, original_signature)
        self.assertEqual(widget.public_ips["fixture"], ["1.1.1.1"])

    def test_shutdown_stops_periodic_queries(self):
        widget = self.widget()
        widget.public_timer.setInterval(10)
        widget.shutdown()
        count = widget.public_ip_service.calls
        QTest.qWait(40)
        self.assertEqual(widget.public_ip_service.calls, count)
        self.assertFalse(widget.public_timer.isActive())
        self.assertTrue(widget.public_ip_service.stopped)

    def test_shutdown_during_preview_saves_original_interval(self):
        widget = self.widget()
        widget._preview_snapshot = (dict(widget.values), widget.saveGeometry())
        widget.preview_settings({"public_ip_interval": 10})
        widget.shutdown()
        self.assertEqual(self.store.load()["public_ip_interval"], 60)


if __name__ == "__main__":
    unittest.main(verbosity=2)
