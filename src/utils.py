"""通用工具函数。

本模块不包含界面代码，负责格式化和生成网络状态签名等纯逻辑操作。
"""


def format_rate(bytes_per_second: float) -> str:
    """将字节/秒转换为适合界面显示的速率文本。"""
    units = ("B/s", "KB/s", "MB/s", "GB/s")
    value = max(0.0, float(bytes_per_second))
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{value:.0f} {units[unit_index]}"
    return f"{value:.1f} {units[unit_index]}"


def network_signature(interfaces: list[dict]) -> tuple:
    """将网卡列表转换为可比较的稳定签名，用于检测网络变化。"""
    return tuple(sorted((item["name"], tuple(sorted(set(item["ips"])))) for item in interfaces))
