"""公网服务域名解析：优先设备 DNS、限时系统回退，不修改系统配置。"""

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
    """优先绑定设备解析，失败后限时使用系统 DNS；HTTPS 仍绑定原网卡。"""
    deadline = time.monotonic() + timeout
    if timeout <= 0:
        raise socket.gaierror(socket.EAI_AGAIN, "DNS 查询预算已耗尽")
    source = ipaddress.ip_address(local_ip)
    family = socket.AF_INET if source.version == 4 else socket.AF_INET6
    record_type = dns.rdatatype.A if source.version == 4 else dns.rdatatype.AAAA
    try:
        resolver = dns.resolver.Resolver()
    except dns.exception.DNSException as error:
        raise socket.gaierror(socket.EAI_AGAIN, "无法读取系统 DNS 配置") from error
    servers = []
    for server in resolver.nameservers:
        try:
            address = ipaddress.ip_address(str(server))
        except ValueError:
            continue
        if address.version == source.version and not address.is_loopback:
            servers.append(str(address))

    # 给系统解析预留预算：VPN DNS 代理并非一定是回环地址，不能强制经物理网卡访问。
    bound_deadline = min(deadline, time.monotonic() + timeout / 2)
    query = dns.message.make_query(host, record_type)
    for index, server in enumerate(servers):
        remaining = bound_deadline - time.monotonic()
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

    remaining = deadline - time.monotonic()
    if remaining > 0:
        try:
            # 仅 DNS 允许遵循系统路由，获取目标地址不代表公网出口；后续 TCP/TLS 仍绑源地址和设备。
            answer = resolver.resolve(host, record_type, lifetime=remaining, search=False)
            addresses = list(dict.fromkeys(str(record.address) for record in answer))
            if addresses:
                return addresses
        except (OSError, dns.exception.DNSException):
            pass
    raise socket.gaierror(socket.EAI_AGAIN, "设备及系统 DNS 查询均未成功")
