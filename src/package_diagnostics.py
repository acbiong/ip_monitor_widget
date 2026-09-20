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
                     ("PyQt5", "psutil", "requests", "dnspython", "certifi")},
        "checks": {},
    }
    checks = report["checks"]
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
    report["ok"] = all(checks.values())
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0 if report["ok"] else 1


def smoke_test() -> int:
    """使用临时配置显示三秒后自动退出，只采集本地信息，不查询公网。"""
    from PyQt5.QtCore import QSettings, QTimer
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication
    from config import ICON_PATH
    from settings_store import SettingsStore
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
                                            and not controller.widget.default_route_service._active)
        controller.widget.close()
        controller.tray.hide()
    report["ok"] = status == 0 and all(report.get(key, False) for key in
                                     ("icon_rendered", "window_visible", "route_detection",
                                      "background_query", "no_remaining_workers"))
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0 if report["ok"] else 1
