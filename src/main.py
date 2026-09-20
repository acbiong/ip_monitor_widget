#!/usr/bin/env python3
"""本机状态监视器应用入口。"""

from __future__ import annotations

import sys

from version import APP_VERSION

def main() -> int:
    """初始化 Qt 应用、托盘控制器并进入事件循环。"""
    # 冻结后 sys.executable 是本程序；后台查询走专用入口，不能再次启动 GUI。
    if sys.argv[1:] == ["--version"]:
        print(APP_VERSION)
        return 0
    if sys.argv[1:] == ["--public-ip-lookup"]:
        from public_ip_lookup import main as lookup_main
        return lookup_main()
    if sys.argv[1:] == ["--self-test"]:
        from package_diagnostics import self_test
        return self_test()
    if sys.argv[1:] == ["--smoke-test"]:
        from package_diagnostics import smoke_test
        return smoke_test()

    from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
    from config import APP_ID, APP_NAME, ORG_NAME
    from tray_controller import TrayController

    QApplication.setOrganizationName(ORG_NAME)
    QApplication.setApplicationName(APP_ID)
    QApplication.setApplicationVersion(APP_VERSION)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")

    if not QSystemTrayIcon.isSystemTrayAvailable():
        print(f"警告：当前桌面环境不支持{APP_NAME}的系统托盘图标。", file=sys.stderr)

    controller = TrayController(app)
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
