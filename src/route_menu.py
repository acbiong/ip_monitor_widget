"""默认出口二级菜单，按实际 IPv4/IPv6 路由勾选，不乐观修改状态。"""

from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtWidgets import QAction, QSystemTrayIcon

from route_switch_service import RouteSwitchService


class RouteMenu(QObject):
    """只在菜单需要时读取候选网卡，所有网络写操作由明确点击触发。"""

    def __init__(self, menu, tray, widget, service=None):
        super().__init__(menu)
        self.menu = menu.addMenu("默认出口")
        self.menu.setToolTipsVisible(True)
        self.tray = tray
        self.widget = widget
        self.service = service or RouteSwitchService(self)
        self.snapshot = {"ok": False, "message": "正在读取网卡…"}
        self.service.result.connect(self._updated)
        self.service.finished.connect(self._finished)
        menu.aboutToShow.connect(self.refresh)
        self.menu.aboutToShow.connect(self.refresh)
        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.refresh)
        self.menu.aboutToShow.connect(self.timer.start)
        self.menu.aboutToHide.connect(self.timer.stop)
        self._render()

    def refresh(self):
        self.service.refresh()

    def _updated(self, report):
        self.snapshot = report
        self._render()

    def _render(self):
        self.menu.clear()
        if self.service.switching:
            self.menu.addAction("正在切换，请完成系统授权…").setEnabled(False)
            return
        if not self.snapshot.get("ok"):
            self.menu.addAction(self.snapshot.get("message", "默认出口检测失败")).setEnabled(False)
            return
        for choice in self.snapshot.get("choices", []):
            families = "/".join(family.upper() for family in choice["default_for"])
            suffix = f"当前 {families}" if families else "/".join(family.upper() for family in choice["families"])
            if not choice["enabled"]:
                suffix = " · ".join(part for part in (suffix, choice["reason"]) if part)
            name = choice["name"].replace("&", "&&")
            action = QAction(f"{name}（{suffix}）", self.menu)
            action.setCheckable(True)
            action.setChecked(bool(choice["default_for"]))
            action.setEnabled(choice["enabled"])
            action.setToolTip(" / ".join(choice["ips"])
                              + "\n仅切换主路由表默认出口；VPN/专用流量仍遵循原策略规则"
                              + "\n切换可能中断现有连接；临时生效，网络重连后恢复系统配置")
            action.triggered.connect(lambda checked, item=choice, entry=action: self._select(item, entry))
            self.menu.addAction(action)
        if not self.snapshot.get("choices"):
            self.menu.addAction("没有已连接网卡").setEnabled(False)

    def _select(self, choice, action):
        action.setChecked(bool(choice["default_for"]))
        if self.service.switch(choice["name"], choice["uuid"]):
            QTimer.singleShot(0, self._render)
        else:
            self.tray.showMessage("默认出口", "正在读取或切换，请稍后重试", QSystemTrayIcon.Information)

    def _finished(self, report):
        icon = QSystemTrayIcon.Information if report["ok"] else QSystemTrayIcon.Warning
        self.tray.showMessage("默认出口", report.get("message", "切换结束"), icon, 8000)
        self.widget.default_route_service.refresh()
        if report["ok"]:
            self.widget.fetch_public_ip()
        else:
            self.service.refresh()

    def shutdown(self):
        self.timer.stop()
        self.service.shutdown()
