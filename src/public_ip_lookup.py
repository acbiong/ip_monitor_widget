"""公网 IP 子进程：通过标准输入/输出交换 JSON，不导入 Qt。

requests 的超时不覆盖所有 DNS 阻塞，最终截止时间由父进程负责强制执行。
"""

from __future__ import annotations

import ipaddress
import json
import socket
import sys
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError

from interface_dns import resolve_interface_host

from config import (
    PUBLIC_IP_CONNECT_SECONDS,
    PUBLIC_IP_ENDPOINTS,
    PUBLIC_IP_LOOKUP_SECONDS,
    PUBLIC_IP_READ_SECONDS,
)


class SourceAddressAdapter(HTTPAdapter):
    """绑定本地源地址；Linux 同时绑定设备，避免被其他网卡的默认路由接管。"""

    def __init__(self, source_address: str, interface_name: str | None = None) -> None:
        self.source_address = (source_address, 0)
        self.interface_name = interface_name
        super().__init__(max_retries=0)

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs) -> None:
        kwargs["source_address"] = self.source_address
        if self.interface_name and sys.platform.startswith("linux"):
            kwargs["socket_options"] = HTTPConnection.default_socket_options + [
                (socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
                 self.interface_name.encode("utf-8") + b"\0"),
            ]
        super().init_poolmanager(connections, maxsize, block, **kwargs)
        if self.interface_name and sys.platform.startswith("linux"):
            interface_name = self.interface_name
            local_ip = self.source_address[0]

            class InterfaceHTTPSConnection(HTTPSConnection):
                """仅替换 TCP 建连时的解析结果，TLS/SNI/Host 始终保留原域名。"""

                def _new_conn(self):
                    hostname = self._dns_host
                    try:
                        addresses = resolve_interface_host(hostname, local_ip, interface_name,
                                                           float(self.timeout))
                    except OSError as error:
                        raise NewConnectionError(self, "网卡 DNS 解析失败") from error
                    last_error = None
                    for address in addresses:
                        try:
                            self._dns_host = address
                            return super()._new_conn()
                        except (NewConnectionError, ConnectTimeoutError) as error:
                            last_error = error
                        finally:
                            self._dns_host = hostname
                    raise NewConnectionError(self, "网卡连接失败") from last_error

            class InterfaceHTTPSConnectionPool(HTTPSConnectionPool):
                ConnectionCls = InterfaceHTTPSConnection

            # 不修改 urllib3 的全局池类型，默认出口仍使用普通系统解析与路由。
            self.poolmanager.pool_classes_by_scheme = dict(self.poolmanager.pool_classes_by_scheme)
            self.poolmanager.pool_classes_by_scheme["https"] = InterfaceHTTPSConnectionPool


def parse_public_ip(body: str) -> str | None:
    """只接受单个全局单播 IP，拒绝 HTML、私网地址和多行混合内容。"""
    try:
        address = ipaddress.ip_address(body.strip())
    except ValueError:
        return None
    if address.is_global and not address.is_multicast:
        return str(address)
    return None


def query_endpoints(local_ip: str, deadline: float, attempt: int = 0,
                    interface_name: str | None = None) -> str | None:
    """仅通过指定源地址和设备直连，不使用默认出口或环境代理。"""
    if not local_ip or not interface_name:
        raise ValueError("公网查询必须指定本机地址和网卡")
    with requests.Session() as session:
        session.trust_env = False
        session.mount("https://", SourceAddressAdapter(local_ip, interface_name))
        # 重试轮换首选服务，避免同一个 DNS/服务故障反复耗尽整轮预算。
        offset = attempt % len(PUBLIC_IP_ENDPOINTS)
        endpoints = PUBLIC_IP_ENDPOINTS[offset:] + PUBLIC_IP_ENDPOINTS[:offset]
        for endpoint in endpoints:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                with session.get(
                    endpoint,
                    timeout=(min(PUBLIC_IP_CONNECT_SECONDS, remaining),
                             min(PUBLIC_IP_READ_SECONDS, remaining)),
                    stream=True,
                    allow_redirects=False,
                ) as response:
                    if response.status_code != 200:
                        continue
                    # 防止异常服务返回无限正文；完整 IP 文本远小于此限制。
                    body = bytearray()
                    for chunk in response.iter_content(chunk_size=257):
                        body.extend(chunk)
                        if len(body) > 256:
                            break
                    if len(body) > 256:
                        continue
                    address = parse_public_ip(body.decode("ascii"))
                    if address:
                        return address
            except (requests.RequestException, OSError, ValueError):
                continue
    return None


def lookup_interface(interface: dict) -> dict:
    """独立查询指定网卡的公网地址，不将其他出口地址当作该网卡结果。"""
    if not isinstance(interface.get("name"), str) or not interface["name"]:
        raise ValueError("缺少网卡名称")
    deadline = time.monotonic() + PUBLIC_IP_LOOKUP_SECONDS
    addresses = []
    # 每个地址族最多选择一个源地址，避免大量临时 IPv6 地址耗尽查询预算。
    sources = {}
    for local_ip in interface["ips"]:
        parsed = ipaddress.ip_address(local_ip)
        sources.setdefault(parsed.version, str(parsed))
    for version in sorted(sources):
        if time.monotonic() >= deadline:
            break
        address = query_endpoints(sources[version], deadline, interface.get("attempt", 0),
                                  interface["name"])
        if address and address not in addresses:
            addresses.append(address)
    if addresses:
        return {"status": "ok", "addresses": addresses}
    return {"status": "failed", "addresses": []}


def main() -> int:
    """读取单网卡任务，输出且仅输出一行 JSON 结果。"""
    try:
        interface = json.loads(sys.stdin.read(65536))
        result = lookup_interface(interface)
    except Exception as error:
        # 将不可预期的第三方库错误隔离在子进程内；错误诊断不污染 stdout 协议。
        print(f"公网查询异常：{type(error).__name__}", file=sys.stderr)
        result = {"status": "failed", "addresses": []}
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
