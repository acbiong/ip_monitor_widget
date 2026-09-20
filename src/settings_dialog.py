"""设置对话框模块。

设置对话框只负责采集用户输入并发出预览/保存信号，不直接修改主窗体。
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QCheckBox,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMessageBox,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QApplication,
)

from config import ICON_PATH, PUBLIC_IP_INTERVAL_LIMITS
from autostart import AutostartManager


class SettingsDialog(QDialog):
    """监控窗体设置对话框。

    信号协议：
    - ``preview_changed(dict)``：控件变化时发出临时配置。
    - ``values_applied(dict)``：点击保存时发出最终配置。
    """

    preview_changed = pyqtSignal(dict)
    values_applied = pyqtSignal(dict)

    def __init__(self, values: dict, defaults: dict, parent=None, autostart_manager=None) -> None:
        super().__init__(parent)
        self.autostart_manager = autostart_manager or AutostartManager()
        self.defaults = dict(defaults)
        self.setWindowTitle("监视器设置")
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(380)
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        font = QApplication.font()
        font_size = f"{font.pixelSize()}px" if font.pixelSize() > 0 else f"{font.pointSizeF()}pt"
        self.setFont(font)
        self.setWindowOpacity(1.0)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        # 空样式表不能阻止父窗口的白字样式继承，设置页单独使用黑字浅底。
        self.setObjectName("SettingsDialog")
        self.setStyleSheet(
            "QDialog#SettingsDialog { background-color: #f5f5f5; color: #000000; }"
            "QDialog#SettingsDialog QWidget { color: #000000; "
            f"font-size: {font_size}; font-weight: normal; }}"
            "QDialog#SettingsDialog QSpinBox { background-color: #ffffff; "
            "selection-background-color: #cce8ff; selection-color: #000000; }"
            "QDialog#SettingsDialog QPushButton { background-color: #e6e6e6; }"
        )
        self._build_controls(values)
        self._connect_signals()

    def _build_controls(self, values: dict) -> None:
        """创建设置控件，避免设置窗口复用主窗体样式。"""
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 48)
        self.font_size.setSuffix(" px")
        self.font_size.setValue(int(values["font_size"]))

        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(10, 95)
        self.opacity.setValue(round(float(values["opacity"]) * 100))
        self.opacity_value = QLabel()
        self.opacity_value.setText(f"{self.opacity.value()}%")
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(self.opacity)
        opacity_row.addWidget(self.opacity_value)

        self.interval = QSpinBox()
        self.interval.setRange(500, 10000)
        self.interval.setSingleStep(500)
        self.interval.setSuffix(" ms")
        self.interval.setValue(int(values["interval"]))

        self.public_ip_interval = QSpinBox()
        self.public_ip_interval.setRange(*PUBLIC_IP_INTERVAL_LIMITS)
        self.public_ip_interval.setSuffix(" 秒")
        self.public_ip_interval.setValue(int(values["public_ip_interval"]))
        self.public_ip_interval.setToolTip("定时重新查询各网卡的公网 IP；查询进行中时不重复启动。默认 60 秒。")

        self.autostart = QCheckBox("登录桌面后自动启动")
        self.autostart.setToolTip("默认关闭，点击保存后生效；取消不改变启动项。移动程序后需重新启用。")
        self.autostart_status = QLabel("点击保存后生效；取消不改变启动项。")
        try:
            self.autostart.setChecked(self.autostart_manager.is_enabled())
        except (OSError, ValueError) as error:
            self.autostart_status.setText("自启动状态读取失败，请检查启动项权限或格式。")
            self.autostart_status.setToolTip(str(error))

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.addRow("文字大小", self.font_size)
        form.addRow("背景透明度", opacity_row)
        form.addRow("系统指标刷新间隔", self.interval)
        form.addRow("公网 IP 获取间隔", self.public_ip_interval)
        form.addRow("开机启动", self.autostart)
        form.addRow("", self.autostart_status)
        form.addRow("窗口层级", QLabel("始终置底（不遮挡其他软件）"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel
            | QDialogButtonBox.Save
            | QDialogButtonBox.RestoreDefaults
        )
        buttons.button(QDialogButtonBox.Save).setText("保存")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.button(QDialogButtonBox.RestoreDefaults).setText("还原默认设置")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)

        layout = QVBoxLayout(self)
        # 依据控件和系统字体计算固定尺寸，禁止手动缩放而不写死高度。
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _connect_signals(self) -> None:
        """将控件变化统一转换为预览信号。"""
        self.font_size.valueChanged.connect(self._emit_preview)
        self.opacity.valueChanged.connect(self._update_opacity_text)
        self.opacity.valueChanged.connect(self._emit_preview)
        self.interval.valueChanged.connect(self._emit_preview)
        self.public_ip_interval.valueChanged.connect(self._emit_preview)

    def _update_opacity_text(self, value: int) -> None:
        self.opacity_value.setText(f"{value}%")

    def current_values(self) -> dict:
        """返回对话框当前的标准配置字典。"""
        return {
            "font_size": self.font_size.value(),
            "opacity": self.opacity.value() / 100,
            "interval": self.interval.value(),
            "public_ip_interval": self.public_ip_interval.value(),
        }

    def _emit_preview(self) -> None:
        self.preview_changed.emit(self.current_values())

    def restore_defaults(self) -> None:
        """将控件恢复到默认值并立即触发预览。"""
        controls = (self.font_size, self.opacity, self.interval, self.public_ip_interval)
        for control in controls:
            control.blockSignals(True)
        self.font_size.setValue(int(self.defaults["font_size"]))
        self.opacity.setValue(round(float(self.defaults["opacity"]) * 100))
        self.interval.setValue(int(self.defaults["interval"]))
        self.public_ip_interval.setValue(int(self.defaults["public_ip_interval"]))
        self.autostart.setChecked(False)
        for control in controls:
            control.blockSignals(False)
        self._update_opacity_text(self.opacity.value())
        self._emit_preview()

    def accept(self) -> None:
        try:
            self.autostart_manager.set_enabled(self.autostart.isChecked())
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "开机启动设置失败", f"未能保存启动项，设置窗口将保持打开。\n{error}")
            return
        self.values_applied.emit(self.current_values())
        super().accept()
