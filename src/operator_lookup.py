"""按已确认的公网地址查询出口 ASN，并保守转换为中文运营商名称。"""

from __future__ import annotations

import ipaddress
import json
import re
import sys

import requests


def canonical_public_ip(value) -> str:
    """拒绝本地、保留、组播地址及带作用域的 IPv6，统一缓存键。"""
    if not isinstance(value, str) or "%" in value:
        return ""
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return ""
    return str(address) if address.is_global and not address.is_multicast else ""


def chinese_operator(holder: str) -> str:
    """仅依据自治系统登记名称识别，不用网卡名称或本地地址猜测。"""
    normalized = re.sub(r"[^A-Z0-9\u4e00-\u9fff]+", " ", holder.upper())
    aliases = (
        ("中国电信", ("CHINANET", "CHINATELECOM", "CHINA TELECOM", "中国电信")),
        ("中国联通", ("CHINA UNICOM", "CHINAUNICOM", "CNCGROUP", "CHINA169", "中国联通")),
        ("中国移动", ("CHINA MOBILE", "CHINAMOBILE", "CMNET", "CMCC", "中国移动")),
        ("中国教育网", ("CERNET", "中国教育")),
        ("中国科技网", ("CSTNET", "中国科技网")),
    )
    matches = {name for name, patterns in aliases
               if any(re.search(r"(?:^| )" + re.escape(pattern) + r"(?: |$)", normalized)
                      for pattern in patterns)}
    return matches.pop() if len(matches) == 1 else "其他运营商"


def _query(session, endpoint: str, resource: str) -> dict:
    """验证 TLS，禁止重定向，限制响应体；阻塞 DNS 由父进程看门狗终止。"""
    with session.get(f"https://stat.ripe.net/data/{endpoint}/data.json",
                     params={"resource": resource}, timeout=(2, 2),
                     stream=True, allow_redirects=False) as response:
        if response.status_code != 200:
            raise ValueError("运营商接口 HTTP 状态异常")
        body = bytearray()
        for chunk in response.iter_content(4096):
            body.extend(chunk)
            if len(body) > 65536:
                raise ValueError("运营商接口响应过大")
        payload = json.loads(body)
        if not isinstance(payload, dict) or payload.get("status") != "ok":
            raise ValueError("运营商接口返回失败")
        data = payload.get("data")
        if not isinstance(data, dict):
            raise ValueError("运营商接口协议异常")
        return data


def lookup_operator(value) -> dict:
    """输出地址、状态、中文名、登记名与 ASN；失败不影响公网 IP 状态。"""
    address = canonical_public_ip(value)
    result = {"address": address, "status": "failed", "name": "暂未识别",
              "holder": "", "asns": []}
    if not address:
        return result
    try:
        with requests.Session() as session:
            session.trust_env = False
            network = _query(session, "network-info", address)
            prefix = ipaddress.ip_network(network.get("prefix", ""))
            if ipaddress.ip_address(address) not in prefix:
                raise ValueError("返回前缀不属于查询地址")
            raw_asns = network.get("asns")
            if not isinstance(raw_asns, list) or not 1 <= len(raw_asns) <= 32:
                raise ValueError("无有效自治系统")
            if any(isinstance(number, bool) or not re.fullmatch(r"[0-9]{1,10}", str(number))
                   or not 1 <= int(number) <= 4294967295 for number in raw_asns):
                raise ValueError("自治系统编号异常")
            asns = sorted({int(number) for number in raw_asns})
            if len(asns) != 1:
                return {**result, "status": "ok", "name": "多运营商（归属不唯一）", "asns": asns}
            overview = _query(session, "as-overview", f"AS{asns[0]}")
            holder = overview.get("holder")
            if str(overview.get("resource")) != str(asns[0]):
                raise ValueError("自治系统编号不匹配")
            if not isinstance(holder, str) or not holder.strip() or len(holder) > 512:
                raise ValueError("缺少有效登记名称")
            holder = " ".join(holder.split())
            return {**result, "status": "ok", "name": chinese_operator(holder),
                    "holder": holder, "asns": asns}
    except (requests.RequestException, ValueError, TypeError):
        return result


def main() -> int:
    """独立工作进程入口，标准输入输出各一份 JSON，不导入 GUI。"""
    try:
        request = json.loads(sys.stdin.buffer.read(4097))
        address = request.get("address") if isinstance(request, dict) else None
    except (ValueError, TypeError):
        address = None
    print(json.dumps(lookup_operator(address), ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
