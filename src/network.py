"""在线网卡枚举：只读取本机信息，不请求网络，也不操作界面。"""

import ipaddress
import socket

import psutil


def get_network_interfaces() -> list[dict]:
    """返回按名称排序的 [{name: str, ips: list[str]}]；链路断开的网卡隐藏。"""
    try:
        stats = psutil.net_if_stats()
        addresses = psutil.net_if_addrs()
    except (OSError, psutil.Error):
        return []
    interfaces = []
    for name, entries in addresses.items():
        if name not in stats or not stats[name].isup:
            continue
        usable_ips = set()
        for entry in entries:
            if entry.family not in (socket.AF_INET, socket.AF_INET6):
                continue
            try:
                address = ipaddress.ip_address(entry.address.split("%", 1)[0])
            except ValueError:
                continue
            if not (address.is_loopback or address.is_link_local
                    or address.is_multicast or address.is_unspecified):
                usable_ips.add(str(address))
        if usable_ips:
            interfaces.append({"name": name, "ips": sorted(usable_ips)})
    return sorted(interfaces, key=lambda item: item["name"])
