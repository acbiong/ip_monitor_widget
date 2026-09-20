"""按设备解析公网服务域名；只在查询子进程内使用，不修改系统 DNS 配置。"""

import ipaddress
import socket
import time

import dns.exception
import dns.message
import dns.rdataclass
import dns.rdatatype
import dns.resolver
import dns.query


def resolve_interface_host(host: str, local_ip: str, interface_name: str,
                           timeout: float) -> list[str]:
    """通过绑定设备的 UDP 套接字查询系统配置的 DNS，返回同地址族的目标地址。"""
    source = ipaddress.ip_address(local_ip)
    family = socket.AF_INET if source.version == 4 else socket.AF_INET6
    record_type = dns.rdatatype.A if source.version == 4 else dns.rdatatype.AAAA
    resolver = dns.resolver.Resolver()
    servers = []
    for server in resolver.nameservers:
        address = ipaddress.ip_address(str(server))
        if address.version == source.version and not address.is_loopback:
            servers.append(str(address))
    if not servers:
        # 本机 DNS 代理必须经回环访问，不能将回环包强制发送到物理设备。
        entries = socket.getaddrinfo(host, 443, family, socket.SOCK_STREAM)
        return list(dict.fromkeys(entry[4][0] for entry in entries))

    deadline = time.monotonic() + timeout
    query = dns.message.make_query(host, record_type)
    for index, server in enumerate(servers):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            with socket.socket(family, socket.SOCK_DGRAM) as transport:
                transport.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
                                     interface_name.encode("utf-8") + b"\0")
                transport.bind((local_ip, 0))
                transport.setblocking(False)
                # 给后续 DNS 服务器预留机会，防止第一个有线 DNS 吞掉全部预算。
                response = dns.query.udp(query, server, sock=transport,
                                         timeout=remaining / (len(servers) - index),
                                         ignore_unexpected=True, raise_on_truncation=True)
                answer = dns.resolver.Answer(query.question[0].name, record_type,
                                             dns.rdataclass.IN, response)
                addresses = list(dict.fromkeys(str(record.address) for record in answer))
                if addresses:
                    return addresses
        except (OSError, dns.exception.DNSException):
            continue
    raise socket.gaierror(socket.EAI_AGAIN, "所选网卡的 DNS 查询失败")
