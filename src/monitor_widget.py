"""主监控窗体模块。

本模块负责把采集模块提供的数据渲染为 Qt 窗体，并处理拖动、锁定、设置预览
和窗体位置记忆。它不实现公网 IP 查询细节，也不创建系统托盘菜单。
"""

from __future__ import annotations

from PyQt5.QtCore import QPoint, QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QDialog,
    QWidget,
)

from config import APP_NAME, DEFAULT_SETTINGS, ICON_PATH
from default_route import DefaultRouteService
from network import get_network_interfaces
from public_ip_service import PublicIPService
from operator_service import OperatorService
from operator_display import operator_text
from settings_dialog import SettingsDialog
from settings_store import SettingsStore, normalize_settings
from system_metrics import SystemMetricsSampler
from utils import format_rate, network_signature


class MonitorWidget(QFrame):
    """显示网络和系统指标的无边框桌面窗体。"""

    DEFAULTS = DEFAULT_SETTINGS

    def __init__(self, tray, network_provider=None, settings_store=None) -> None:
        super().__init__()
        self.tray = tray
        self.store = settings_store or SettingsStore()
        self.values = self.store.load()
        self.network_provider = network_provider or get_network_interfaces
        self.drag_offset = None
        self.network_interfaces = self.network_provider()
        self.network_signature = network_signature(self.network_interfaces)
        self.public_ips = {item["name"]: ["获取中…"] for item in self.network_interfaces}
        self.metrics_sampler = SystemMetricsSampler()
        self.public_ip_service = PublicIPService(self)
        self.public_ip_service.result.connect(self.set_public_ips)
        self.operator_service = OperatorService(self)
        self.operator_service.result.connect(self._update_network_rows)
        self.default_route_service = DefaultRouteService(self)
        self.default_route_service.result.connect(self.set_default_routes)
        self._shutting_down = False
        self.settings_dialog = None
        self.autostart_manager = None
        self._preview_snapshot = None
        # 合并异步地址/指标变化触发的布局请求，等待 Qt 更新文字尺寸后再适配窗体。
        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.timeout.connect(self._fit_content)
        self._layer_timer = QTimer(self)
        self._layer_timer.setSingleShot(True)
        self._layer_timer.timeout.connect(self._restore_bottom_layer)

        self._configure_window()
        self.labels = {}
        self._applied_font_size = None
        self._compact_network_layout = False
        self._build_ui()
        self._apply_font()
        self._apply_lock_state(self.values["locked"], save=False)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(self.values["interval"])
        self.public_timer = QTimer(self)
        self.public_timer.timeout.connect(self.fetch_public_ip)
        self.public_timer.start(self.values["public_ip_interval"] * 1000)
        self.update_metrics()
        QTimer.singleShot(0, self.fetch_public_ip)

        geometry = self.store.load_geometry("geometry")
        if not geometry or not self.restoreGeometry(geometry):
            self.move(36, 120)
        # 保留记忆位置，但按当前内容收紧尺寸，不沿用旧标题或旧内容留下的空白。
        self._fit_content(QSize())

    def _configure_window(self) -> None:
        """设置主窗体属性；设置窗口不会复用这些属性。"""
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(ICON_PATH)))

    def _save_settings(self) -> None:
        """保存配置和主窗体位置。"""
        if self._preview_snapshot is not None:
            self.store.save(*self._preview_snapshot)
        else:
            self.store.save(self.values, self.saveGeometry())

    def _build_ui(self) -> None:
        """创建网络区域和系统指标区域。"""
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(16, 14, 16, 14)

        route_layout = QVBoxLayout()
        route_layout.setSpacing(2)
        for family, title in (("ipv4", "IPv4"), ("ipv6", "IPv6")):
            self._add_value_row(route_layout, f"default_{family}",
                                f"默认出口 {title}", "检测中…")
            self.labels[f"default_{family}"].setToolTip(
                "系统主路由表中优先级最高的默认出口；不代表该网卡能够访问公网。"
                "策略路由、VPN 或特定目的地址可能使用其他出口。")
        layout.addLayout(route_layout)

        self.network_layout = QVBoxLayout()
        self.network_layout.setSpacing(2)
        layout.addLayout(self.network_layout)
        self._rebuild_network_rows()

        self.system_layout = QVBoxLayout()
        self.system_layout.setSpacing(4)
        system_rows = (
            ("upload", "上传速度", "—"),
            ("download", "下载速度", "—"),
            ("cpu", "CPU 占用", "—"),
            ("memory", "内存占用", "—"),
            ("disk", "硬盘使用", "—"),
            ("temperature", "CPU 温度", "—"),
        )
        for key, name, value in system_rows:
            self._add_value_row(self.system_layout, key, name, value)
        layout.addLayout(self.system_layout)
        # 内容保留完整最小尺寸；屏幕放不下时滚动查看，而不是压缩或裁掉标签。
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.content = QWidget()
        self.content.setLayout(layout)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.scroll_area.setWidget(self.content)
        self.content.setAutoFillBackground(False)
        self.scroll_area.viewport().setAutoFillBackground(False)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.scroll_area)

    def _add_value_row(self, parent_layout, key: str, name: str, value: str) -> None:
        """向指定布局追加一行左标签、右数值。"""
        line = QHBoxLayout()
        left = QLabel(name)
        right = QLabel(value)
        left.setObjectName("label")
        right.setObjectName("value")
        for label in (left, right):
            label.setTextFormat(Qt.PlainText)
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        left.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        right.setAlignment(Qt.AlignRight | Qt.AlignTop)
        line.addWidget(left)
        line.addStretch(1)
        line.addWidget(right)
        parent_layout.addLayout(line)
        self.labels[key] = right

    def _rebuild_network_rows(self) -> None:
        """根据当前在线网卡重建网络信息区域。"""
        # 删除动态标签引用，防止反复插拔网卡时保留已销毁的 Qt 控件。
        self.labels = {key: label for key, label in self.labels.items()
                       if not key.startswith(("local:", "public:", "operator:"))}
        self._clear_layout(self.network_layout)
        self.network_rows = {}
        if not self.network_interfaces:
            empty = QLabel("暂无已连接网卡")
            empty.setObjectName("label")
            empty.setAlignment(Qt.AlignCenter)
            self.network_layout.addWidget(empty)
            return

        for interface in self.network_interfaces:
            self._add_network_interface(interface)

    @staticmethod
    def _clear_layout(layout) -> None:
        """递归释放嵌套布局，避免只清理第一层导致动态行积累。"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().hide()
                item.widget().deleteLater()
            elif item.layout() is not None:
                MonitorWidget._clear_layout(item.layout())
                item.layout().deleteLater()

    def _add_network_interface(self, interface: dict) -> None:
        """创建单张网卡的显示区。"""
        name = interface["name"]
        header = QLabel(f"▸ {name}")
        header.setTextFormat(Qt.PlainText)
        header.setObjectName("interface")
        self.network_layout.addWidget(header)
        row_container = QVBoxLayout()
        self.network_layout.addLayout(row_container)
        self._add_value_row(row_container, f"local:{name}", "本机 IP", "\n".join(interface["ips"]))
        self._add_value_row(row_container, f"public:{name}", "公网 IP",
                            "\n".join(self.public_ips.get(name, ["获取中…"])))
        self.labels[f"public:{name}"].setToolTip(
            "仅显示通过本网卡查询的公网 IP。“未连接公网”表示本次未取得有效公网地址，"
            "DNS 或查询服务异常也可能导致此状态。")
        text, tooltip = operator_text(self.public_ips.get(name, []), self.operator_service)
        operator_container = QWidget()
        operator_layout = QVBoxLayout(operator_container)
        operator_layout.setContentsMargins(0, 0, 0, 0)
        self._add_value_row(operator_layout, f"operator:{name}", "运营商", text)
        row_container.addWidget(operator_container)
        operator_container.setVisible(bool(text))
        self.labels[f"operator:{name}"].setToolTip(tooltip)
        self.network_rows[name] = {
            "local": self.labels[f"local:{name}"],
            "public": self.labels[f"public:{name}"],
            "operator": self.labels[f"operator:{name}"],
            "operator_container": operator_container,
        }

    def _update_network_rows(self) -> None:
        """将缓存中的网卡和公网 IP 数据刷新到标签。"""
        for interface in self.network_interfaces:
            rows = self.network_rows.get(interface["name"])
            if rows is None:
                continue
            rows["local"].setText("\n".join(interface["ips"]))
            rows["public"].setText("\n".join(self.public_ips.get(interface["name"], ["获取中…"])))
            text, tooltip = operator_text(self.public_ips.get(interface["name"], []), self.operator_service)
            rows["operator"].setText(text)
            rows["operator"].setToolTip(tooltip)
            container = rows["operator_container"]
            if container.isHidden() == bool(text):
                self._compact_network_layout = True
            container.setVisible(bool(text))
        self._layout_timer.start(0)

    def _apply_font(self) -> None:
        """应用主窗体字体，并按字体比例调整窗体尺寸。"""
        size = int(self.values["font_size"])
        previous_size = self._applied_font_size
        previous_window_size = self.size()
        font = QFont("Sans Serif")
        font.setPixelSize(size)
        self.setFont(font)
        scale = size / self.DEFAULTS["font_size"]
        self.content.layout().setContentsMargins(*(round(value * scale) for value in (16, 14, 16, 14)))
        self._scale_layout(self.content.layout(), scale)
        self.setStyleSheet(
            f"""
            QLabel {{ color: white; font-size: {size}px; }}
            QLabel#label {{ color: rgba(255, 255, 255, 190); }}
            QLabel#value {{ font-weight: 600; }}
            QLabel#interface {{ font-weight: 600; color: white; padding-top: {round(2 * scale)}px; }}
            """
        )
        preferred = QSize()
        if previous_size and previous_size != size:
            scale = size / previous_size
            preferred = QSize(
                round(previous_window_size.width() * scale),
                round(previous_window_size.height() * scale),
            )
        self._applied_font_size = size
        self._fit_content(preferred)
        self.update()

    def _fit_content(self, preferred=None) -> None:
        """按文字实际尺寸扩展窗体，并为屏幕边界和滚动条预留空间。"""
        if self._shutting_down:
            return
        if self._compact_network_layout and preferred is None:
            preferred = QSize(self.width(), 0)
        self._compact_network_layout = False
        self.content.ensurePolished()
        layout = self.content.layout()
        layout.invalidate()
        layout.activate()
        natural = layout.totalSizeHint().expandedTo(layout.totalMinimumSize())
        baseline = round(310 * self.values["font_size"] / self.DEFAULTS["font_size"])
        target = natural.expandedTo(QSize(baseline, 0))
        # 异步更新只增长，不因速率或状态变短而来回抖动；字体变化可显式缩小。
        target = target.expandedTo(self.size() if preferred is None else preferred)
        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            extent = self.scroll_area.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            if target.height() > available.height():
                target.setWidth(max(target.width(), natural.width() + extent))
            if target.width() > available.width():
                target.setHeight(max(target.height(), natural.height() + extent))
            target = target.boundedTo(available.size())
            self.setMinimumWidth(min(baseline, available.width()))
            self.resize(target)
            self.move(
                max(available.left(), min(self.x(), available.right() - self.width() + 1)),
                max(available.top(), min(self.y(), available.bottom() - self.height() + 1)),
            )
        else:
            self.setMinimumWidth(baseline)
            self.resize(target)

    @staticmethod
    def _scale_layout(layout, scale: float) -> None:
        """间距随字体同步缩放，避免文字变大但留白固定。"""
        layout.setSpacing(max(1, round(4 * scale)))
        for index in range(layout.count()):
            child = layout.itemAt(index).layout()
            if child is None and layout.itemAt(index).widget() is not None:
                child = layout.itemAt(index).widget().layout()
            if child is not None:
                MonitorWidget._scale_layout(child, scale)

    def _apply_lock_state(self, locked: bool, save: bool = True) -> None:
        """切换点击穿透状态，并保持位置和尺寸不变。"""
        self.values["locked"] = locked
        # 使用工具窗口类型，不创建任务栏入口；同时保留独立窗口的置底行为。
        flags = (Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnBottomHint
                 | Qt.WindowDoesNotAcceptFocus)
        if locked:
            flags |= Qt.WindowTransparentForInput

        if self.windowFlags() != flags:
            was_visible = self.isVisible()
            old_position = self.pos()
            old_size = self.size()
            self.setWindowFlags(flags)
            self.resize(old_size)
            self.move(old_position)
            if was_visible:
                self.show()

        if save:
            self._save_settings()
        status = "已锁定" if locked else "可拖动"
        self.tray.setToolTip(f"{APP_NAME} · {status}")

    def toggle_lock(self, checked=None) -> None:
        """响应托盘锁定动作。"""
        new_state = not self.values["locked"] if checked is None else checked
        self._apply_lock_state(new_state)

    def _default_settings_position(self, dialog: SettingsDialog) -> QPoint:
        """计算设置窗口的默认居中位置。"""
        dialog.adjustSize()
        screen = QApplication.screenAt(self.frameGeometry().center()) or QApplication.primaryScreen()
        if screen is None:
            return QPoint(120, 120)
        available = screen.availableGeometry()
        return QPoint(
            available.center().x() - dialog.width() // 2,
            available.center().y() - dialog.height() // 2,
        )

    def _restore_settings_dialog_geometry(self, dialog: SettingsDialog) -> None:
        """恢复设置窗口位置，失败时使用默认位置。"""
        saved_geometry = self.store.load_geometry("settings_geometry")
        if not saved_geometry or not dialog.restoreGeometry(saved_geometry):
            dialog.move(self._default_settings_position(dialog))

    def open_settings(self) -> None:
        """打开设置窗口并处理预览、保存和取消回滚。"""
        if self.settings_dialog is not None:
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return
        original_values = dict(self.values)
        original_geometry = self.saveGeometry()
        self._preview_snapshot = (original_values, original_geometry)
        dialog = SettingsDialog(self.values, self.DEFAULTS, parent=self,
                                autostart_manager=self.autostart_manager)
        self.settings_dialog = dialog
        self._restore_settings_dialog_geometry(dialog)
        dialog.preview_changed.connect(self.preview_settings)
        dialog.values_applied.connect(self.apply_settings)
        try:
            result = dialog.exec_()
        finally:
            self.store.save_geometry("settings_geometry", dialog.saveGeometry())
            self.settings_dialog = None
            dialog.deleteLater()
        if result != QDialog.Accepted:
            self.restore_settings_preview(original_values, original_geometry)
        self._preview_snapshot = None

    def reset_window_positions(self) -> None:
        """恢复主窗体和设置窗口的默认位置。"""
        self.move(36, 120)
        self._save_settings()
        self.store.reset_settings_position()
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            self.settings_dialog.move(self._default_settings_position(self.settings_dialog))
            self.store.save_geometry("settings_geometry", self.settings_dialog.saveGeometry())

    def preview_settings(self, updated: dict) -> None:
        """实时应用设置预览，但不落盘。"""
        locked = self.values["locked"]
        previous_font = self.values["font_size"]
        self.values = normalize_settings({**self.values, **updated})
        self.timer.setInterval(self.values["interval"])
        self._update_public_ip_interval()
        if self.values["font_size"] != previous_font:
            self._apply_font()
        self.update()
        self._apply_lock_state(locked, save=False)

    def restore_settings_preview(self, original_values: dict, original_geometry) -> None:
        """取消设置时恢复进入设置窗口前的配置和几何信息。"""
        locked = original_values["locked"]
        self.values = dict(original_values)
        self.timer.setInterval(self.values["interval"])
        self._update_public_ip_interval()
        self._apply_font()
        self._apply_lock_state(locked, save=False)
        self.restoreGeometry(original_geometry)
        self._fit_content()

    def _update_public_ip_interval(self) -> None:
        """只在公网间隔变化时重置倒计时，其他设置预览不推迟公网查询。"""
        interval_ms = self.values["public_ip_interval"] * 1000
        if self.public_timer.interval() != interval_ms:
            self.public_timer.setInterval(interval_ms)

    def apply_settings(self, updated: dict) -> None:
        """保存设置窗口提交的配置。"""
        self._preview_snapshot = None
        self.preview_settings(updated)
        self._save_settings()

    def refresh_network_interfaces(self) -> None:
        """检测网卡变化，变化后重建界面并重新查询公网 IP。"""
        interfaces = self.network_provider()
        signature = network_signature(interfaces)
        if signature == self.network_signature:
            return
        self.network_interfaces = interfaces
        self.network_signature = signature
        self.public_ips = {item["name"]: ["获取中…"] for item in interfaces}
        self.operator_service.request([])
        self._rebuild_network_rows()
        self._apply_font()
        self.fetch_public_ip()

    def fetch_public_ip(self) -> None:
        """查询服务负责去重、取消旧批次和执行超时。刷新时保留已有结果。"""
        if self._shutting_down:
            return
        self.public_ip_service.request(self.network_interfaces)

    def set_public_ips(self, signature: tuple, public_ips: dict) -> None:
        """只接收与当前网卡签名匹配的后台查询结果。"""
        if self._shutting_down or signature != self.network_signature:
            return
        interface_names = {item["name"] for item in self.network_interfaces}
        for name, result in public_ips.items():
            if name not in interface_names:
                continue
            addresses = result["addresses"]
            self.public_ips[name] = (addresses if result["status"] == "ok" and addresses
                                     else ["未连接公网"])
        self.operator_service.request([address for addresses in self.public_ips.values() for address in addresses])
        self._update_network_rows()

    def update_metrics(self) -> None:
        """刷新网卡和系统指标。"""
        self.refresh_network_interfaces()
        self.default_route_service.refresh()
        metrics = self.metrics_sampler.sample()
        self.labels["upload"].setText(format_rate(metrics["upload_bps"]))
        self.labels["download"].setText(format_rate(metrics["download_bps"]))
        for key in ("cpu", "memory", "disk"):
            value = metrics[f"{key}_percent"]
            self.labels[key].setText("不可用" if value is None else f"{value:.0f}%")
        self.labels["temperature"].setText(metrics["temperature"])
        self._layout_timer.start(0)

    def set_default_routes(self, routes: dict) -> None:
        """默认出口独立于本机 IP 和公网查询结果，路由变化也会刷新显示。"""
        if self._shutting_down:
            return
        for family in ("ipv4", "ipv6"):
            names = routes.get(family)
            text = "检测失败" if names is None else "\n".join(names) if names else "无默认路由"
            self.labels[f"default_{family}"].setText(text)
        self._layout_timer.start(0)

    def showEvent(self, event) -> None:
        """首次显示、托盘恢复及切换锁定后均保持置底，不抢占其他窗口焦点。"""
        super().showEvent(event)
        self.lower()
        self._layer_timer.start(0)

    def _restore_bottom_layer(self) -> None:
        """原生窗口重映射后重新提交置底状态，避免窗口管理器丢失旧提示。"""
        if self._shutting_down or not self.isVisible():
            return
        handle = self.windowHandle()
        if handle is not None:
            handle.setFlag(Qt.WindowStaysOnBottomHint, False)
            handle.setFlag(Qt.WindowStaysOnBottomHint, True)
        self.lower()

    def paintEvent(self, event) -> None:
        """绘制半透明圆角背景和边框。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        alpha = round(float(self.values["opacity"]) * 255)
        painter.setBrush(QColor(18, 20, 24, alpha))
        painter.setPen(QPen(QColor(255, 255, 255, min(90, alpha)), 1))
        radius = 14 * self.values["font_size"] / self.DEFAULTS["font_size"]
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), radius, radius)
        painter.end()
        super().paintEvent(event)

    def mousePressEvent(self, event) -> None:
        if not self.values["locked"] and event.button() == Qt.LeftButton:
            self.lower()
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not self.values["locked"] and self.drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self.drag_offset is not None:
            self.drag_offset = None
            self._save_settings()
        super().mouseReleaseEvent(event)

    def shutdown(self) -> None:
        """停止定时器和网络子进程，预览未保存时只持久化原始快照。"""
        if self._shutting_down:
            return
        self._shutting_down = True
        self.timer.stop()
        self.public_timer.stop()
        self._layout_timer.stop()
        self._layer_timer.stop()
        self._save_settings()
        self.public_ip_service.shutdown()
        self.operator_service.shutdown()
        self.default_route_service.shutdown()

    def closeEvent(self, event) -> None:
        self.shutdown()
        event.accept()
