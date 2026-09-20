# 当前网络公网 IP 查询修复验证报告

日期：2026-09-20；版本：0.7.1；分支：`fix/public-ip-current-network`。

## 复现与根因

- 当前系统解析配置由 Tailscale 管理，使用非回环 DNS 代理；无线连接由 NetworkManager 管理。
- 旧实现将同地址族、非回环 DNS 一律绑定到查询网卡；代理 DNS 不能经物理无线设备访问，解析超时，导致所有回显服务请求失败。
- 旧实现对 wlp0s20f3 的单轮查询约 2.6 秒后失败。对比诊断中设备绑定 DNS 在 0.601 秒后失败，系统 DNS 在 0.005 秒成功。
- 仅在诊断进程中替换 DNS 解析路径、仍保持 HTTPS 源地址及设备绑定时，可成功获取公网 IP，确认故障点在 DNS 路径而非必须解绑 HTTP。

## 修复

`src/interface_dns.py` 先用至多一半预算尝试设备 DNS，失败后在剩余预算内调用系统 dnspython 解析器；回环代理或没有匹配 DNS 传输族时直接使用系统解析。移除无独立超时的 getaddrinfo 路径。
不修改 VPN/DNS/路由配置；HTTPS 仍绑定原网卡、验证 TLS，禁止环境代理和重定向，不跨网卡借用地址。

## 回归

- `src/tests/test_interface_dns.py` 新增 13 项测试，覆盖 DNS 代理、限时回退、IPv6/IPv4 DNS、配置及 socket 错误、TLS 主机名、设备/源地址和代理隔离。
- 与原默认出口 28 项测试合计 41 项通过。
- 真实 X11 源码 `--smoke-test` 全部通过，设置预览/取消/保存、关于页面、默认出口读取和退出清理均正常。
- 命令：`QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_PLUGIN_PATH= QT_QPA_PLATFORM_PLUGIN_PATH= PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s src/tests -v`，使用项目构建虚拟环境。
- 首次新测试夹具错误地把连接池 maxsize 参数传给连接对象；修正夹具后全部通过，生产连接代码未因此修改。

## 真实异步查询

使用 QCoreApplication + PublicIPService，在当前真实网络运行约 22 秒并保留原重试调度：

| 网卡 | 结果 | 说明 |
|---|---|---|
| wlp0s20f3 | ok，1 个公网地址 | 首次约 1.31 秒返回成功，无需重试 |
| vmnet1 / vmnet8 | failed，0 个地址 | 未借用无线出口结果 |
| tailscale0 | failed，0 个地址 | 本次绑定查询未取得公网地址，不将物理网卡结果标为隧道出口 |
| 退出 | 无剩余工作进程 | 保留异步退出机制 |

报告只记录状态/数量，不存储实际公网 IP、内部搜索域等环境敏感信息。没有修改用户设置或网络配置。

## 边界与构建

未验证所有 VPN/企业 DNS/代理策略。公网服务可达性仍可能波动，当前网络实测结果不代表所有网卡都能访问互联网。
DNS 回退允许遵循系统路由，但公网回显连接始终绑定指定设备；不把 failed 严格等同完整互联网断网诊断。
最终单文件的版本、自检和 GUI 结果见 `../BUILD_MANIFEST.json`、`PACKAGE_SELF_TEST.json`、`PACKAGE_SMOKE_TEST.json` 和 `VALIDATION_REPORT.md`。
