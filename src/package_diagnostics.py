"""单文件包诊断：检查内置依赖、后台入口及无公网请求的 GUI 启停。"""

import importlib.metadata
import json
from pathlib import Path
import shutil
import ssl
import subprocess
import sys
import tempfile

from build_info import load_build_info
from version import APP_VERSION


def self_test() -> int:
    """不创建 GUI，验证资源、依赖、路由工具及单文件后台入口。"""
    import certifi
    from PyQt5.QtCore import QLibraryInfo, QT_VERSION_STR, qVersion
    from config import ICON_PATH

    root = Path(__file__).resolve().parent
    frozen = bool(getattr(sys, "frozen", False))
    command = str(root / "bin" / "ip") if frozen else shutil.which("ip")
    build_info = load_build_info()
    report = {
        "application_version": APP_VERSION,
        "git": build_info.get("git", {}),
        "build": build_info.get("build", {}),
        "frozen": frozen,
        "python": sys.version.split()[0],
        "qt": qVersion(),
        "qt_binding_build": QT_VERSION_STR,
        "packages": {name: importlib.metadata.version(name) for name in
                     ("PyQt5", "psutil", "requests", "dnspython", "certifi", "dbus-next")},
        "checks": {},
    }
    checks = report["checks"]
    checks["build_metadata"] = (not frozen or (
        build_info.get("application_version") == APP_VERSION
        and build_info.get("git", {}).get("commit") not in (None, "", "未知")
        and bool(build_info.get("build", {}).get("built_at"))
    ))
    checks["icon"] = ICON_PATH.is_file()
    checks["ca_certificates"] = Path(certifi.where()).is_file()
    checks["tls_context"] = ssl.create_default_context(cafile=certifi.where()).cert_store_stats()["x509_ca"] > 0
    plugins = Path(QLibraryInfo.location(QLibraryInfo.PluginsPath))
    checks["xcb_plugin"] = (plugins / "platforms" / "libqxcb.so").is_file()
    try:
        result = subprocess.run([command, "-Version"], capture_output=True, timeout=10, check=False)
        checks["bundled_route_tool"] = result.returncode == 0
    except (OSError, TypeError, subprocess.TimeoutExpired):
        checks["bundled_route_tool"] = False
    arguments = ([sys.executable, "--public-ip-lookup"] if frozen
                 else [sys.executable, str(root / "public_ip_lookup.py")])
    try:
        result = subprocess.run(arguments, input=b'{"name": null}', capture_output=True,
                                timeout=15, check=False)
        checks["background_entry"] = (result.returncode == 0 and json.loads(result.stdout)
                                      == {"status": "failed", "addresses": []})
    except (OSError, ValueError, subprocess.TimeoutExpired):
        checks["background_entry"] = False
    arguments = ([sys.executable] if frozen else [sys.executable, str(root / "main.py")])
    try:
        result = subprocess.run(arguments + ["--default-route-control"], input=b'{"action":"invalid"}',
                                capture_output=True, timeout=15, check=False)
        checks["route_control_entry"] = (result.returncode == 1 and json.loads(result.stdout)
                                          == {"ok": False, "message": "无效的默认出口操作"})
    except (OSError, ValueError, subprocess.TimeoutExpired):
        checks["route_control_entry"] = False
    report["ok"] = all(checks.values())
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0 if report["ok"] else 1


def smoke_test() -> int:
    """使用临时配置显示三秒后自动退出，只采集本地信息，不查询公网。"""
    from PyQt5.QtCore import QCoreApplication, QEvent, QSettings, QTimer, Qt
    from PyQt5.QtGui import QColor, QIcon, QPalette
    from PyQt5.QtWidgets import QApplication, QCheckBox, QDialogButtonBox, QLabel, QLineEdit, QPushButton, QSpinBox
    from about_dialog import AboutDialog
    from config import APP_NAME, ICON_PATH
    from settings_store import SettingsStore
    from settings_dialog import SettingsDialog
    from autostart import AutostartManager
    from tray_controller import TrayController

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    report = {"application_version": APP_VERSION}
    with tempfile.TemporaryDirectory(prefix="ip-monitor-smoke-") as directory:
        settings = QSettings(str(Path(directory) / "settings.ini"), QSettings.IniFormat)
        # 空地址列表保证后台入口不发送网络请求，同时覆盖冻结后的真实 QProcess 链路。
        fixture = [{"name": "打包自检", "ips": []}]
        controller = TrayController(app, network_provider=lambda: fixture, settings_store=SettingsStore(settings))
        controller.widget.autostart_manager = AutostartManager(config_home=Path(directory) / "config")
        controller.route_menu.service.result.connect(
            lambda result: report.update(route_menu_readonly=bool(result.get("ok"))))
        controller.route_menu.refresh()

        def check_about():
            """通过真实托盘动作打开关于页，检查内容并自动关闭两次。"""
            def inspect_and_close():
                dialog = next((child for child in controller.widget.findChildren(AboutDialog)
                               if child.isVisible()), None)
                if dialog is None:
                    report["about_fields"] = False
                    app.quit()
                    return
                texts = [label.text() for label in dialog.findChildren(QLabel)]
                report["about_fields"] = all(value in texts for value in
                                              (APP_VERSION, "开发者", "Git 分支", "Git 提交", "编译时间"))
                report["about_icon"] = any(label.pixmap() is not None and not label.pixmap().isNull()
                                           for label in dialog.findChildren(QLabel))
                version_label = next(label for label in dialog.findChildren(QLabel)
                                     if label.text() == APP_VERSION)
                report["about_style"] = (dialog.windowOpacity() == 1.0 and
                                         version_label.palette().windowText().color()
                                         == app.palette().windowText().color())
                report["about_title"] = dialog.windowTitle() == "关于"
                title_label = next(label for label in dialog.findChildren(QLabel)
                                   if f"<h2>{APP_NAME}</h2>" in label.text())
                report["about_name_centered"] = title_label.alignment() == Qt.AlignCenter
                original_size = dialog.size()
                dialog.resize(original_size.width() + 100, original_size.height() + 100)
                report["about_fixed_size"] = (dialog.size() == original_size
                                               == dialog.minimumSize() == dialog.maximumSize())
                dialog.resize(100, 100)
                report["about_fixed_size"] = (report["about_fixed_size"]
                                               and dialog.size() == original_size)
                dialog.reject()

            action = next(action for action in controller.menu.actions() if action.text() == "关于")
            results = []
            for attempt in range(2):
                QTimer.singleShot(0, inspect_and_close)
                action.trigger()
                QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
                results.append(report.get("about_fields", False) and report.get("about_icon", False)
                               and report.get("about_style", False)
                               and report.get("about_title", False)
                               and report.get("about_name_centered", False)
                               and report.get("about_fixed_size", False)
                               and not controller.widget.findChildren(AboutDialog))
            report["about_open_close"] = all(results)

        QTimer.singleShot(500, check_about)

        def check_settings():
            """验证设置页黑字、固定尺寸及预览/取消/保存，不使用用户配置。"""
            original_values = dict(controller.widget.values)
            results = []

            def inspect_and_close(save):
                dialog = controller.widget.settings_dialog
                if dialog is None:
                    results.append(False)
                    return
                try:
                    original_size = dialog.size()
                    labels = dialog.findChildren(QLabel)
                    original_fonts = [label.font().toString() for label in labels]
                    dialog.font_size.setValue(48)
                    dialog.opacity.setValue(95)
                    dialog.interval.setValue(10000)
                    dialog.public_ip_interval.setValue(10)
                    report["autostart_default_off"] = not dialog.autostart.isChecked()
                    dialog.autostart.setChecked(True)
                    report["autostart_deferred"] = not controller.widget.autostart_manager.path.exists()
                    QApplication.processEvents()
                    report["settings_preview"] = all(controller.widget.values[key] == value
                                                      for key, value in dialog.current_values().items())
                    report["public_ip_interval_preview"] = controller.widget.public_timer.interval() == 10000
                    text_widgets = dialog.findChildren((QLabel, QSpinBox, QLineEdit, QPushButton, QCheckBox))
                    report["settings_black_text"] = all(
                        child.palette().color(role) == QColor("#000000")
                        for child in text_widgets
                        for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText))
                    report["settings_style_isolated"] = (
                        dialog.windowOpacity() == 1.0
                        and dialog.palette().color(QPalette.Window) == QColor("#f5f5f5")
                        and original_fonts == [label.font().toString() for label in labels])
                    dialog.resize(original_size.width() + 100, original_size.height() + 100)
                    report["settings_fixed_size"] = (dialog.size() == original_size
                                                      == dialog.minimumSize() == dialog.maximumSize())
                    dialog.resize(100, 100)
                    report["settings_fixed_size"] &= dialog.size() == original_size
                    buttons = dialog.findChild(QDialogButtonBox)
                    buttons.button(QDialogButtonBox.RestoreDefaults).click()
                    report["settings_restore_defaults"] = all(
                        controller.widget.values[key] == value == dialog.defaults[key]
                        for key, value in dialog.current_values().items())
                    report["public_ip_interval_default"] = controller.widget.public_timer.interval() == 60000
                    report["autostart_reset_default"] = not dialog.autostart.isChecked()
                    dialog.font_size.setValue(24)
                    dialog.public_ip_interval.setValue(120)
                    dialog.autostart.setChecked(True)
                    results.append(all(report[key] for key in (
                        "settings_preview", "settings_black_text", "settings_style_isolated",
                        "settings_fixed_size", "settings_restore_defaults", "public_ip_interval_preview",
                        "public_ip_interval_default", "autostart_default_off", "autostart_deferred",
                        "autostart_reset_default")))
                    buttons.button(QDialogButtonBox.Save if save else QDialogButtonBox.Cancel).click()
                except Exception as error:
                    report["settings_error"] = str(error)
                    results.append(False)
                    dialog.reject()

            action = next(action for action in controller.menu.actions() if action.text() == "打开设置")
            for save in (False, True):
                QTimer.singleShot(0, lambda save=save: inspect_and_close(save))
                action.trigger()
                QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
                if save:
                    report["settings_saved"] = (controller.widget.values["font_size"] == 24
                                                 == controller.widget.store.load()["font_size"]
                                                 and controller.widget.store.load()["public_ip_interval"] == 120
                                                 and controller.widget.public_timer.interval() == 120000)
                    report["autostart_saved"] = controller.widget.autostart_manager.is_enabled()
                else:
                    report["settings_cancelled"] = (controller.widget.values == original_values
                        and controller.widget.public_timer.interval() == original_values["public_ip_interval"] * 1000)
                    report["autostart_cancelled"] = not controller.widget.autostart_manager.path.exists()
                results.append(not controller.widget.findChildren(SettingsDialog))
            report["settings_open_close"] = (all(results) and report["settings_saved"]
                                               and report["settings_cancelled"] and report["autostart_saved"]
                                               and report["autostart_cancelled"])
            controller.widget.autostart_manager.set_enabled(False)
            report["autostart_disabled"] = not controller.widget.autostart_manager.is_enabled()

        QTimer.singleShot(1000, check_settings)

        def finish():
            report["icon_rendered"] = not QIcon(str(ICON_PATH)).pixmap(32, 32).isNull()
            report["window_visible"] = controller.widget.isVisible()
            report["routes"] = dict(controller.widget.default_route_service._results)
            report["route_detection"] = (len(report["routes"]) == 2
                                          and all(value is not None for value in report["routes"].values()))
            report["background_query"] = (controller.widget.public_ip_service._results.get("打包自检")
                                           == {"status": "failed", "addresses": []})
            app.quit()

        QTimer.singleShot(3000, finish)
        status = app.exec_()
        controller.widget.shutdown()
        report["no_remaining_workers"] = (not controller.widget.public_ip_service._active
                                            and not controller.widget.default_route_service._active
                                            and controller.route_menu.service.process is None)
        controller.widget.close()
        controller.tray.hide()
    report["ok"] = status == 0 and all(report.get(key, False) for key in
                                     ("icon_rendered", "window_visible", "route_detection",
                                      "background_query", "no_remaining_workers", "about_open_close",
                                      "settings_open_close", "route_menu_readonly", "autostart_disabled"))
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0 if report["ok"] else 1
