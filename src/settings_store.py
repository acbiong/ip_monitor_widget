"""配置校验、兼容旧 QSettings 和窗口几何持久化。"""

import math
import logging

from PyQt5.QtCore import QByteArray, QSettings

from config import APP_ID, DEFAULT_SETTINGS, ORG_NAME


def normalize_settings(values: dict) -> dict:
    """忽略未知字段，非法值恢复默认；数值约束与设置界面保持一致。"""
    result = dict(DEFAULT_SETTINGS)
    limits = {"font_size": (8, 48), "opacity": (0.10, 0.95), "interval": (500, 10000)}
    for name, default in result.items():
        value = values.get(name, default)
        try:
            if isinstance(default, bool):
                lowered = str(value).lower()
                if lowered in ("true", "1", "yes", "false", "0", "no"):
                    result[name] = lowered in ("true", "1", "yes")
            else:
                number = float(value)
                if math.isfinite(number):
                    minimum, maximum = limits[name]
                    number = min(maximum, max(minimum, number))
                    result[name] = int(number) if isinstance(default, int) else number
        except (ValueError, TypeError, OverflowError):
            continue
    return result


class SettingsStore:
    """保留原组织、应用名和键，升级后无需重新设置窗口位置。"""

    def __init__(self, settings=None) -> None:
        self.settings = settings if settings is not None else QSettings(ORG_NAME, APP_ID)

    def load(self) -> dict:
        return normalize_settings({name: self.settings.value(name, default)
                                   for name, default in DEFAULT_SETTINGS.items()})

    def save(self, values: dict, geometry: QByteArray) -> None:
        # 旧版置顶选项已移除，只清理该键，不影响其他设置和窗口位置。
        self.settings.remove("always_on_top")
        for name, value in normalize_settings(values).items():
            self.settings.setValue(name, value)
        self.save_geometry("geometry", geometry)

    def load_geometry(self, key: str) -> QByteArray:
        value = self.settings.value(key)
        return value if isinstance(value, QByteArray) else QByteArray()

    def save_geometry(self, key: str, geometry: QByteArray) -> None:
        self.settings.setValue(key, geometry)
        self._sync()

    def reset_settings_position(self) -> None:
        self.settings.remove("settings_geometry")
        self._sync()

    def _sync(self) -> None:
        """写入失败时保留内存状态并给出诊断，不因无权限关闭监控窗口。"""
        self.settings.sync()
        if self.settings.status() != QSettings.NoError:
            logging.warning("配置未能正常持久化：%s", self.settings.fileName())
