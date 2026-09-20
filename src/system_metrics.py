"""连续采样系统指标；单项失败不影响其余指标和界面定时器。"""

import time

import psutil

from cpu_temperature import get_cpu_temperature


def _read_metric(reader):
    """平台不支持、传感器离线或无权限时返回 None。"""
    try:
        return reader()
    except (OSError, psutil.Error, RuntimeError, AttributeError):
        return None


class SystemMetricsSampler:
    """在同一线程保存 CPU 基线和网络字节计数，使用单调时钟计算差值。"""

    def __init__(self) -> None:
        self.last_network = _read_metric(psutil.net_io_counters)
        self.last_time = time.monotonic()
        _read_metric(lambda: psutil.cpu_percent(interval=None))

    def sample(self) -> dict:
        """返回速率、使用率和温度快照；负计数差钳制为零，避免重置后显示负速率。"""
        now = time.monotonic()
        network = _read_metric(psutil.net_io_counters)
        elapsed = max(0.001, now - self.last_time)
        upload_bps = download_bps = 0.0
        if network is not None and self.last_network is not None:
            upload_bps = max(0.0, (network.bytes_sent - self.last_network.bytes_sent) / elapsed)
            download_bps = max(0.0, (network.bytes_recv - self.last_network.bytes_recv) / elapsed)
        self.last_network, self.last_time = network, now
        return {
            "upload_bps": upload_bps,
            "download_bps": download_bps,
            "cpu_percent": _read_metric(lambda: psutil.cpu_percent(interval=None)),
            "memory_percent": _read_metric(lambda: psutil.virtual_memory().percent),
            "disk_percent": _read_metric(lambda: psutil.disk_usage("/").percent),
            "temperature": get_cpu_temperature(),
        }
