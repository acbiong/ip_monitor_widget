"""策略路由只读评估：区分专用网段/标记流量与接管普通公网的路由。"""

import ipaddress


def table_name(value):
    """统一 ip JSON 中内置表的名称与数字表示。"""
    return {"255": "local", "254": "main", "253": "default"}.get(str(value), str(value))


def table_preserves_default(routes, version):
    """专用网段路由保持原状；拒绝默认路由、半网段及合并后覆盖全网的路由。"""
    if not isinstance(routes, list):
        return False
    networks = []
    for route in routes:
        if not isinstance(route, dict):
            return False
        kind = route.get("type", "unicast")
        if kind == "throw":
            continue
        if kind not in ("unicast", "blackhole", "unreachable", "prohibit", "local", "broadcast"):
            return False
        try:
            network = ipaddress.ip_network(route.get("dst", "default"), strict=False)
        except ValueError:
            return False
        if network.version != version or network.prefixlen <= 1:
            return False
        networks.append(network)
    return not any(network.prefixlen == 0 for network in ipaddress.collapse_addresses(networks))


def policy_allows_main(rules, read_table, version):
    """仅评估未标记流量到主表的路径，不改动规则、VPN 或任何专用路由表。"""
    if not isinstance(rules, list) or not rules:
        return False
    allowed_keys = {"priority", "src", "table", "protocol", "fwmark", "fwmask", "action"}
    tables = {}
    try:
        if any(not isinstance(rule, dict) or not isinstance(rule.get("priority"), int)
               or rule["priority"] < 0 for rule in rules):
            return False
        for rule in sorted(rules, key=lambda item: item["priority"]):
            # 否定、接口/用户/源网段等条件需单独求值，不能误当普通无标记流量。
            if set(rule) - allowed_keys or rule.get("src", "all") not in ("all", "0.0.0.0/0", "::/0"):
                return False
            if "fwmark" in rule:
                mark = int(str(rule["fwmark"]), 0)
                mask = int(str(rule.get("fwmask", "0xffffffff")), 0)
                if not (0 <= mark <= 0xffffffff and 0 <= mask <= 0xffffffff):
                    return False
                if mark & mask:
                    # Tailscale 等的非零标记规则不匹配普通流量，原规则仍完整保留。
                    continue
            elif "fwmask" in rule:
                return False
            if rule.get("action", "lookup") not in ("lookup", "to_tbl", "unicast"):
                return False
            if "table" not in rule:
                return False
            table = table_name(rule["table"])
            if table == "local":
                if rule["priority"] != 0:
                    return False
                continue
            if table == "main":
                return True
            if table not in tables:
                if len(tables) >= 8:
                    return False
                tables[table] = read_table(table)
            if not table_preserves_default(tables[table], version):
                return False
    except (TypeError, ValueError, KeyError):
        return False
    # 没有可达的主表 lookup 时，调整主表不能代表默认出口切换。
    return False
