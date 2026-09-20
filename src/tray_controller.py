"""系统托盘控制器模块。"""

from __future__ import annotations

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon

from config import APP_NAME, ICON_PATH
from monitor_widget import MonitorWidget


class TrayController:
    """创建托盘图标、菜单，并持有主监控窗体。"""

    def __init__(self, app: QApplication, network_provider=None, settings_store=None) -> None:
        self.app = app
        self.tray = QSystemTrayIcon(QIcon(str(ICON_PATH)), app)
        self.tray.setToolTip(APP_NAME)
        self.widget = MonitorWidget(self.tray, network_provider=network_provider, settings_store=settings_store)
        app.aboutToQuit.connect(self.widget.shutdown)
        self.menu = QMenu()
        self._build_menu()
        self.menu.aboutToShow.connect(self._sync_menu)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self._on_activated)
        self.tray.show()
        self.widget.show()

    def _build_menu(self) -> None:
        """构建锁定、设置、位置还原和退出菜单。"""
        lock_action = QAction("锁定（鼠标穿透，不可选中）", self.menu)
        self.lock_action = lock_action
        lock_action.setCheckable(True)
        lock_action.setChecked(self.widget.values["locked"])
        lock_action.triggered.connect(self.widget.toggle_lock)
        self.menu.addAction(lock_action)

        self.menu.addSeparator()
        settings_action = QAction("打开设置", self.menu)
        settings_action.triggered.connect(self.widget.open_settings)
        self.menu.addAction(settings_action)

        reset_positions_action = QAction("还原桌面和设置窗体位置", self.menu)
        reset_positions_action.triggered.connect(self.widget.reset_window_positions)
        self.menu.addAction(reset_positions_action)

        quit_action = QAction("退出", self.menu)
        quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(quit_action)

    def _sync_menu(self) -> None:
        """设置取消可能还原锁定状态，显示菜单时同步勾选值。"""
        self.lock_action.setChecked(self.widget.values["locked"])

    def _on_activated(self, reason) -> None:
        """单击托盘图标恢复监视器显示，但不将其抬到其他软件上方。"""
        if reason == QSystemTrayIcon.Trigger:
            self.widget.showNormal()
            self.widget.lower()
