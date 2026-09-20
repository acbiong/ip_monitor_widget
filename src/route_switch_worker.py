"""默认出口后台任务：通过 NetworkManager 临时重应用路由，检查点保护失败回滚。"""

import asyncio
import copy
import json
from pathlib import Path
import subprocess
import sys

from dbus_next import BusType, Message, MessageFlag, MessageType, Variant
from dbus_next.aio import MessageBus

from default_route import parse_default_interfaces
from network import get_network_interfaces


NM = "org.freedesktop.NetworkManager"
ROOT = "/org/freedesktop/NetworkManager"
DEVICE = NM + ".Device"
FAMILIES = {"ipv4": "-4", "ipv6": "-6"}


def unpack(value):
    """递归解包只读 D-Bus 数据；重应用时保留原始 Variant 类型。"""
    if isinstance(value, Variant):
        return unpack(value.value)
    if isinstance(value, dict):
        return {key: unpack(item) for key, item in value.items()}
    if isinstance(value, list):
        return [unpack(item) for item in value]
    return value


def read_kernel_routes():
    """读取主路由表和规则，拒绝将 VPN/策略路由误当普通默认出口。"""
    command = str(Path(__file__).parent / "bin/ip") if getattr(sys, "frozen", False) else "ip"
    routes = {}
    safe = True
    for family, option in FAMILIES.items():
        def query(arguments):
            result = subprocess.run([command, "-j", option, *arguments], capture_output=True,
                                    text=True, timeout=2, check=True)
            return json.loads(result.stdout)
        routes[family] = query(["route", "show", "table", "main", "default"])
        rules = query(["rule", "show"])
        expected = {0: "local", 32766: "main", 32767: "default"}
        safe &= all(rule.get("src", "all") == "all"
                    and rule.get("table") == expected.get(rule.get("priority"))
                    and not set(rule) - {"priority", "src", "table", "protocol"}
                    for rule in rules)
        safe &= all("dev" in route and not any(key in route for key in ("nexthops", "nhid"))
                    and route.get("type", "unicast") == "unicast"
                    and route.get("from", "all") in ("all", "0.0.0.0/0", "::/0")
                    for route in routes[family])
    return routes, safe


def switch_plan(routes, name):
    """仅调整目标已有默认路由的地址族；必要时提高竞争出口优先级数值。"""
    plan = {}
    families = []
    for family, entries in routes.items():
        active = [entry for entry in entries
                  if not set(entry.get("flags", [])) & {"dead", "linkdown"}]
        if not any(entry.get("dev") == name for entry in active):
            continue
        families.append(family)
        if parse_default_interfaces(entries) == [name]:
            continue
        plan.setdefault(name, {})[family] = 1
        for entry in active:
            other = entry["dev"]
            if other != name and int(entry.get("metric", 0)) <= 1:
                plan.setdefault(other, {})[family] = 100
    if not families:
        raise ValueError("该网卡没有可用默认路由，不能推测网关。请先在系统网络设置中配置。")
    return plan, families


def changed_settings(settings, metrics):
    """保留应用配置，仅更新路由 metric，兼容显式静态默认路由。"""
    updated = copy.deepcopy(settings)
    for family, metric in metrics.items():
        section = updated[family]
        plain = unpack(section)
        if (plain.get("never-default", False) or plain.get("route-table", 0) not in (0, 254)
                or plain.get("routing-rules")):
            raise ValueError("该连接禁止默认出口或使用策略路由，未修改网络。")
        section["route-metric"] = Variant("x", metric)
        if "route-data" in section:
            for route in section["route-data"].value:
                if unpack(route).get("prefix") == 0:
                    if unpack(route).get("table", 254) not in (0, 254):
                        raise ValueError("静态默认路由使用非主表，未修改网络。")
                    route["metric"] = Variant("u", metric)
            # 新格式携带完整路由属性，避免旧 routes 的重复数据覆盖新 metric。
            section.pop("routes", None)
        elif plain.get("routes"):
            raise ValueError("连接仅提供旧式静态路由，暂不支持安全切换。")
    return updated


class NetworkManagerClient:
    """单次任务使用独立系统总线连接，不调用 shell、sudo 或永久配置接口。"""

    def __init__(self, bus):
        self.bus = bus

    async def call(self, path, interface, member, signature="", body=None, authorize=False):
        reply = await asyncio.wait_for(self.bus.call(Message(
            destination=NM, path=path, interface=interface, member=member,
            signature=signature, body=body or [],
            flags=MessageFlag.ALLOW_INTERACTIVE_AUTHORIZATION if authorize else MessageFlag.NONE)),
            timeout=40 if authorize else 5)
        if reply.message_type == MessageType.ERROR:
            raise RuntimeError(f"{reply.error_name}: {'; '.join(str(item) for item in reply.body)}")
        return reply.body

    async def properties(self, path, interface):
        return unpack((await self.call(path, "org.freedesktop.DBus.Properties", "GetAll", "s", [interface]))[0])

    async def snapshot(self):
        manager = await self.properties(ROOT, NM)
        routes, safe = await asyncio.to_thread(read_kernel_routes)
        version = tuple(int(part) for part in manager["Version"].split(".")[:2])
        reason = "" if safe else "存在策略路由或多路径路由，请使用系统网络设置"
        if version < (1, 42):
            reason = "安全切换需要 NetworkManager 1.42 或更新版本"
        for path in manager.get("ActiveConnections", []):
            active = await self.properties(path, NM + ".Connection.Active")
            if active.get("Vpn") or active.get("Type") in ("vpn", "wireguard"):
                reason = "VPN 正在运行，请先在系统网络设置中处理出口"
        permissions = (await self.call(ROOT, NM, "GetPermissions"))[0]
        if any(permissions.get(NM + "." + permission) not in ("yes", "auth")
               for permission in ("network-control", "checkpoint-rollback")):
            reason = "系统策略不允许当前用户切换默认出口"
        devices = {}
        for path in manager.get("Devices", []):
            props = await self.properties(path, DEVICE)
            name = props.get("IpInterface") or props["Interface"]
            props["path"] = path
            if props.get("ActiveConnection", "/") != "/":
                active = await self.properties(props["ActiveConnection"], NM + ".Connection.Active")
                props["uuid"] = active.get("Uuid", "")
            devices[name] = props
        if any(not devices.get(route.get("dev"), {}).get("Managed")
               for entries in routes.values() for route in entries):
            reason = "默认路由包含非 NetworkManager 管理网卡，暂不修改"
        current = {family: parse_default_interfaces(entries) for family, entries in routes.items()}
        choices = []
        for item in get_network_interfaces():
            name = item["name"]
            device = devices.get(name, {})
            families = [family for family, entries in routes.items()
                        if any(route.get("dev") == name and not set(route.get("flags", []))
                               & {"dead", "linkdown"} for route in entries)]
            unavailable = reason
            if not device.get("Managed"):
                unavailable = "不受 NetworkManager 管理"
            elif device.get("State") != 100:
                unavailable = "连接未就绪"
            elif not families:
                unavailable = "没有默认网关/默认路由"
            choices.append({**item, "uuid": device.get("uuid", ""), "families": families,
                            "default_for": [family for family in FAMILIES if name in current[family]],
                            "enabled": not unavailable, "reason": unavailable})
        return {"ok": True, "choices": choices, "current": current}, devices, routes

    async def switch(self, name, expected_uuid):
        snapshot, devices, routes = await self.snapshot()
        selected = next((item for item in snapshot["choices"] if item["name"] == name), None)
        if not selected or not selected["enabled"]:
            raise ValueError(selected["reason"] if selected else "网卡已断开，请刷新菜单")
        if not expected_uuid or selected["uuid"] != expected_uuid:
            raise ValueError("网卡连接已变化，请重新打开菜单后再选择")
        plan, families = switch_plan(routes, name)
        if not plan:
            return {**snapshot, "message": "所选网卡已是默认出口"}
        changes = []
        for interface, metrics in plan.items():
            device = devices[interface]
            settings, version = await self.call(device["path"], DEVICE, "GetAppliedConnection", "u", [0], True)
            if unpack(settings).get("connection", {}).get("uuid") != device.get("uuid"):
                raise ValueError("准备切换时连接已变化，未修改网络")
            changes.append((device["path"], changed_settings(settings, metrics), version))
        checkpoint = (await self.call(ROOT, NM, "CheckpointCreate", "aouu",
                                     [[path for path, settings, version in changes], 90, 0], True))[0]
        try:
            # 先提升目标网卡，再处理相同优先级的竞争出口，尽量减少业务中断。
            for path, settings, version in changes:
                await self.call(path, DEVICE, "Reapply", "a{sa{sv}}tu", [settings, version, 1], True)
            for attempt in range(12):
                latest, unused_devices, unused_routes = await self.snapshot()
                target = next((item for item in latest["choices"] if item["name"] == name), None)
                if (target and target["enabled"] and target["uuid"] == expected_uuid
                        and all(latest["current"][family] == [name] for family in families)):
                    break
                await asyncio.sleep(0.25)
            else:
                raise RuntimeError("实际默认路由未切换至所选网卡")
            await self.call(ROOT, NM, "CheckpointDestroy", "o", [checkpoint], True)
        except (Exception, asyncio.CancelledError) as error:
            try:
                rollback = (await self.call(ROOT, NM, "CheckpointRollback", "o", [checkpoint]))[0]
                if any(value != 0 for value in rollback.values()):
                    raise RuntimeError("部分设备回滚失败")
            except Exception as rollback_error:
                raise RuntimeError(f"切换失败：{error}；回滚未确认：{rollback_error}。请检查系统网络设置。") from error
            raise RuntimeError(f"切换未完成，已回滚：{error}") from error
        labels = "/".join(family.upper() for family in families)
        return {**latest, "message": f"{labels} 默认出口已切换至 {name}（临时生效，重连后恢复系统配置）"}


async def run(request):
    """只接受枚举和按连接 UUID 选择网卡，不提供任意命令执行入口。"""
    if not isinstance(request, dict) or request.get("action") not in ("list", "switch"):
        raise ValueError("无效的默认出口操作")
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    try:
        client = NetworkManagerClient(bus)
        if request["action"] == "list":
            return (await client.snapshot())[0]
        return await client.switch(request.get("name"), request.get("uuid"))
    finally:
        bus.disconnect()


def main():
    """stdin/stdout 为有界 JSON；异常明确返回失败，不伪造切换成功。"""
    try:
        request = json.loads(sys.stdin.buffer.read(8193))
        timeout = 65 if isinstance(request, dict) and request.get("action") == "switch" else 10
        result = asyncio.run(asyncio.wait_for(run(request), timeout))
    except Exception as error:
        result = {"ok": False, "message": str(error) or "默认出口操作超时，请检查网络状态"}
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if result["ok"] else 1
