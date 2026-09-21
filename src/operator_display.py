"""运营商显示协议：仅使用当前网卡已确认的公网地址，支持双栈独立标注。"""

from operator_lookup import canonical_public_ip


def operator_text(addresses, service) -> tuple[str, str]:
    """返回中文显示值及原始登记信息提示；无公网地址时绝不查询归属。"""
    public = [address for value in addresses if (address := canonical_public_ip(value))]
    explanation = ("按公网出口 ASN 登记名称识别，并非一定是本地宽带签约运营商。"
                   "VPN、代理或云出口可能不同；未收录的名称显示其他运营商。")
    if not public:
        return "", explanation
    lines, details = [], [explanation]
    for address in public:
        result = service.get(address)
        prefix = ("IPv6：" if ":" in address else "IPv4：") if len(public) > 1 else ""
        lines.append(prefix + result["name"])
        asns = ", ".join(f"AS{number}" for number in result.get("asns", []))
        details.append(f'{address}：{result.get("holder") or result["name"]} {asns}'.strip())
    return "\n".join(lines), "\n".join(details)
