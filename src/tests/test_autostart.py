"""自启动回归：只写临时配置目录，不注册真实用户登录启动项。"""

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt5.QtWidgets import QApplication, QDialog

from autostart import AutostartManager, ENTRY_NAME, launch_command, quote_exec_argument
from config import DEFAULT_SETTINGS
from settings_dialog import SettingsDialog


class AutostartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manager = AutostartManager(config_home=self.root, command=[sys.executable])

    def dialog(self):
        dialog = SettingsDialog(DEFAULT_SETTINGS, DEFAULT_SETTINGS, autostart_manager=self.manager)
        self.addCleanup(dialog.deleteLater)
        return dialog

    def test_default_off_creates_nothing(self):
        self.assertFalse(self.manager.is_enabled())
        self.manager.set_enabled(False)
        self.assertFalse(self.manager.path.parent.exists())

    def test_enable_and_reopen(self):
        self.manager.set_enabled(True)
        self.assertTrue(AutostartManager(config_home=self.root).is_enabled())
        self.assertTrue(self.dialog().autostart.isChecked())
        self.assertEqual(self.manager.path.stat().st_mode & 0o777, 0o644)

    def test_disable_and_reenable(self):
        self.manager.set_enabled(True)
        self.manager.set_enabled(False)
        self.assertFalse(self.manager.is_enabled())
        self.assertIn("Hidden=true", self.manager.path.read_text())
        self.manager.set_enabled(True)
        self.assertTrue(self.manager.is_enabled())

    def test_unrelated_entries_untouched(self):
        self.manager.path.parent.mkdir()
        other = self.manager.path.parent / "unrelated.desktop"
        other.write_text("unchanged")
        self.manager.set_enabled(True)
        self.manager.set_enabled(False)
        self.assertEqual(other.read_text(), "unchanged")

    def test_xdg_config_home(self):
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root)}):
            self.assertEqual(AutostartManager().path, self.root / "autostart" / ENTRY_NAME)

    def test_relative_xdg_ignored(self):
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "relative"}):
            self.assertEqual(AutostartManager().path, Path.home() / ".config/autostart" / ENTRY_NAME)

    def test_frozen_uses_real_executable_not_extraction(self):
        with patch("autostart.sys.frozen", True, create=True), patch("autostart.sys.executable", "/opt/My Monitor"):
            self.assertEqual(launch_command(), ["/opt/My Monitor"])

    def test_source_preserves_venv_path(self):
        with patch("autostart.sys.frozen", False, create=True), patch("autostart.sys.executable", "/tmp/venv/bin/python"):
            command = launch_command()
            self.assertEqual(command[0], "/tmp/venv/bin/python")
            self.assertTrue(Path(command[1]).is_absolute())
            self.assertEqual(Path(command[1]).name, "main.py")

    def test_special_paths_roundtrip(self):
        for argument in ['/tmp/中文 space', '/tmp/quote"here', '/tmp/back\\slash',
                         '/tmp/$HOME`whoami`;touch pwn', '/tmp/100%name', '/tmp/tab\there']:
            with self.subTest(argument=argument):
                encoded = quote_exec_argument(argument)
                decoded = encoded.replace("\\\\", "\\").replace("\\t", "\t")
                parsed = shlex.split(decoded)[0].replace("\\$", "$").replace("\\`", "`")
                self.assertEqual(parsed.replace("%%", "%"), argument)

    def test_invalid_paths_rejected(self):
        for argument in ("", "/tmp/bad\npath", "/tmp/bad\rpath", "/tmp/bad\0path"):
            with self.assertRaises(ValueError):
                quote_exec_argument(argument)

    def test_missing_executable_does_not_enable(self):
        manager = AutostartManager(config_home=self.root, command=[str(self.root / "missing")])
        with self.assertRaises(ValueError):
            manager.set_enabled(True)
        self.assertFalse(manager.path.exists())

    def test_atomic_failure_preserves_existing_entry(self):
        self.manager.set_enabled(True)
        previous = self.manager.path.read_bytes()
        with patch("autostart.os.replace", side_effect=PermissionError("模拟无权限")):
            with self.assertRaises(PermissionError):
                self.manager.set_enabled(False)
        self.assertEqual(self.manager.path.read_bytes(), previous)
        self.assertEqual(list(self.manager.path.parent.iterdir()), [self.manager.path])

    def test_symlink_not_modified(self):
        other = self.root / "other"
        other.write_text("unchanged")
        self.manager.path.parent.mkdir()
        self.manager.path.symlink_to(other)
        with self.assertRaises(ValueError):
            self.manager.set_enabled(True)
        self.assertEqual(other.read_text(), "unchanged")

    def test_corrupt_file_reports_error(self):
        self.manager.path.parent.mkdir()
        self.manager.path.write_text("not a desktop file")
        with self.assertRaises(ValueError):
            self.manager.is_enabled()

    def test_system_disabled_entry_reflected(self):
        self.manager.set_enabled(True)
        text = self.manager.path.read_text().replace("X-GNOME-Autostart-enabled=true", "X-GNOME-Autostart-enabled=false")
        self.manager.path.write_text(text)
        self.assertFalse(self.dialog().autostart.isChecked())

    def test_cancel_does_not_enable(self):
        dialog = self.dialog()
        dialog.autostart.setChecked(True)
        dialog.reject()
        self.assertFalse(self.manager.path.exists())

    def test_save_enables_and_emits_values(self):
        dialog = self.dialog()
        values = []
        dialog.values_applied.connect(values.append)
        dialog.autostart.setChecked(True)
        dialog.accept()
        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertTrue(self.manager.is_enabled())
        self.assertEqual(len(values), 1)

    def test_defaults_pending_until_save(self):
        self.manager.set_enabled(True)
        dialog = self.dialog()
        dialog.restore_defaults()
        self.assertFalse(dialog.autostart.isChecked())
        self.assertTrue(self.manager.is_enabled())
        dialog.reject()
        self.assertTrue(self.manager.is_enabled())
        another = self.dialog()
        another.restore_defaults()
        another.accept()
        self.assertFalse(self.manager.is_enabled())

    def test_save_failure_keeps_dialog_open(self):
        dialog = self.dialog()
        dialog.autostart.setChecked(True)
        values = []
        dialog.values_applied.connect(values.append)
        dialog.show()
        with patch.object(self.manager, "set_enabled", side_effect=PermissionError("无权限")), \
                patch("settings_dialog.QMessageBox.warning") as warning:
            dialog.accept()
        self.assertTrue(dialog.isVisible())
        self.assertEqual(values, [])
        warning.assert_called_once()
        dialog.reject()

    @unittest.skipUnless(shutil.which("desktop-file-validate"), "系统未安装 desktop 文件校验工具")
    def test_desktop_entry_format(self):
        for enabled in (True, False):
            self.manager.set_enabled(enabled)
            result = subprocess.run(["desktop-file-validate", str(self.manager.path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
