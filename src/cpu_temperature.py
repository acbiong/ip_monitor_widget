"""CPU 温度采集：只选择明确的 CPU 传感器，避免将显卡/硬盘温度误当 CPU。"""

import math
from pathlib import Path

import psutil


def _valid_temperature(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and -20 < value < 150


def get_cpu_temperature() -> str:
    """优先 CPU 封装温度，其次最高核心温度；不支持时返回“不可用”。"""
    try:
        temperatures = psutil.sensors_temperatures(fahrenheit=False)
    except (AttributeError, RuntimeError, OSError, psutil.Error):
        temperatures = {}
    for name in ("coretemp", "k10temp", "cpu_thermal", "zenpower"):
        entries = [entry for entry in temperatures.get(name, [])
                   if _valid_temperature(entry.current)]
        if entries:
            packages = [entry.current for entry in entries
                        if any(label in entry.label.lower() for label in ("package", "tdie", "tctl"))]
            value = max(packages or [entry.current for entry in entries])
            return f"{value:.0f} °C"
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        try:
            sensor_type = (zone / "type").read_text().strip().lower()
            if "cpu" not in sensor_type and sensor_type != "x86_pkg_temp":
                continue
            value = float((zone / "temp").read_text().strip()) / 1000
            if _valid_temperature(value):
                return f"{value:.0f} °C"
        except (OSError, ValueError):
            continue
    return "不可用"
