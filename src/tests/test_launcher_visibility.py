"""自启动与开始屏幕隔离回归；仅写临时目录，不调用真实会话总线。"""

import configparser
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from autostart import AutostartManager
from launcher_refresh import refresh_application_cache


class LauncherVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.notify = Mock()
        self.manager = AutostartManager(self.root, [sys.executable], self.notify)

    def section(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string(self.manager.path.read_text())
        return parser["Desktop Entry"]

    def test_enable_hidden_from_launcher_not_from_autostart(self):
        self.manager.set_enabled(True)
        entry = self.section()
        self.assertTrue(entry.getboolean("NoDisplay"))
        self.assertFalse(entry.getboolean("Hidden"))
        self.assertTrue(self.manager.is_enabled())
        self.notify.assert_called_once_with()

    def test_disable_keeps_menu_hidden_and_refreshes(self):
        self.manager.set_enabled(True)
        self.notify.reset_mock()
        self.manager.set_enabled(False)
        self.assertTrue(self.section().getboolean("NoDisplay"))
        self.assertTrue(self.section().getboolean("Hidden"))
        self.assertFalse(self.manager.is_enabled())
        self.notify.assert_called_once_with()

    def test_disabled_legacy_entry_repaired_on_save(self):
        self.manager.path.parent.mkdir()
        self.manager.path.write_text("[Desktop Entry]\nType=Application\nName=旧启动项\nHidden=true\n")
        self.manager.set_enabled(False)
        self.assertTrue(self.section().getboolean("NoDisplay"))
        self.assertFalse(self.manager.is_enabled())
        self.notify.assert_called_once_with()

    def test_first_start_does_not_create_or_notify(self):
        self.manager.repair_visibility()
        self.assertFalse(self.manager.path.exists())
        self.notify.assert_not_called()

    def test_legacy_enabled_migration_preserves_command(self):
        self.manager.set_enabled(True)
        command = self.section()["Exec"]
        content = self.manager.path.read_text().replace("NoDisplay=true\n", "")
        self.manager.path.write_text(content + "X-Custom=保留此字段\n")
        self.manager.repair_visibility()
        self.assertTrue(self.manager.is_enabled())
        self.assertEqual(self.section()["Exec"], command)
        self.assertEqual(self.section()["X-Custom"], "保留此字段")
        self.assertTrue(self.section().getboolean("NoDisplay"))

    def test_legacy_disabled_migration_does_not_enable(self):
        self.manager.path.parent.mkdir()
        self.manager.path.write_text("[Desktop Entry]\nType=Application\nHidden=true\n")
        self.manager.repair_visibility()
        self.assertFalse(self.manager.is_enabled())
        self.assertTrue(self.section().getboolean("NoDisplay"))

    def test_idempotent_repair_still_refreshes_stale_cache(self):
        self.manager.set_enabled(True)
        previous = self.manager.path.read_bytes()
        self.notify.reset_mock()
        self.manager.repair_visibility()
        self.assertEqual(self.manager.path.read_bytes(), previous)
        self.notify.assert_called_once_with()

    def test_failed_operations_never_notify(self):
        with patch("autostart.os.replace", side_effect=PermissionError("模拟拒绝")):
            with self.assertRaises(PermissionError):
                self.manager.set_enabled(True)
        self.notify.assert_not_called()

        self.manager.path.write_text("模拟读取期间文件被外部改坏")
        with patch.object(self.manager, "is_enabled", return_value=False):
            with self.assertRaises(ValueError):
                self.manager.repair_visibility()
        self.notify.assert_not_called()

    def test_injected_config_never_refreshes_real_desktop(self):
        with patch("autostart.refresh_application_cache") as refresh:
            AutostartManager(self.root, [sys.executable]).set_enabled(True)
        refresh.assert_not_called()

    def test_symlink_migration_rejected(self):
        other = self.root / "other.desktop"
        other.write_text("unchanged")
        self.manager.path.parent.mkdir()
        self.manager.path.symlink_to(other)
        with self.assertRaises(ValueError):
            self.manager.repair_visibility()
        self.assertEqual(other.read_text(), "unchanged")
        self.notify.assert_not_called()

    def test_refresh_without_bus_is_noop(self):
        with patch("launcher_refresh.QDBusConnection") as bus:
            connection = bus.sessionBus.return_value
            connection.isConnected.return_value = False
            refresh_application_cache()
            connection.asyncCall.assert_not_called()

    def test_refresh_async_no_service_activation(self):
        with patch("launcher_refresh.QDBusConnection") as bus:
            connection = bus.sessionBus.return_value
            connection.isConnected.return_value = True
            refresh_application_cache()
            message, timeout = connection.asyncCall.call_args.args
            self.assertEqual(message.service(), "org.desktopspec.ApplicationManager1")
            self.assertEqual(message.member(), "ReloadApplications")
            self.assertFalse(message.autoStartService())
            self.assertEqual(timeout, 1500)


if __name__ == "__main__":
    unittest.main()
