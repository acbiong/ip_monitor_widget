# 默认出口策略路由兼容验证报告

日期：2026-09-20；修复版本：0.7.2；分支：`fix/default-route-policy-compatibility`。

## 根因与范围

旧版只允许三个内置规则的固定形式，任何额外规则都使 safe=false。当前 Tailscale 添加了标记流量规则和 table 52 组网/DNS 路由，但该表没有默认或全网接管路由，旧版因规则存在便把 wlp0s20f3 禁用，属于误判。

新增 `src/route_policy.py`，由 `route_switch_worker.py` 读取相关表并评估普通未标记流量；`route_menu.py` 说明只切换主表。没有移除对真正默认接管、未知选择器、多路径及活动 VPN 的保护，不修改系统规则或 Tailscale 配置。

## 自动回归

- 新增 `src/tests/test_route_policy.py`：19 项，覆盖 Tailscale 双栈、默认/分拆全网、局部路由、标记/否定/源规则、缺少 main、缓存、读取错误及非法输入。
- 原策略规则测试补充真实接管表数据，不再以“存在额外规则”本身作为拒绝依据。
- 与原路由事务 28 项及 DNS/HTTPS 隔离 13 项合计 60 项全部通过。
- 命令：`QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_PLUGIN_PATH= QT_QPA_PLATFORM_PLUGIN_PATH= PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s src/tests -v`，使用项目构建虚拟环境。
- Python 语法、Git 空白检查及真实 X11 源码 `--smoke-test` 通过；设置、关于、默认出口读取、后台及退出未回归。

## 当前网络只读验证

修复后的 `--default-route-control` list 返回：

| 网卡 | 可选 | 当前默认族/原因 |
|---|---|---|
| wlp0s20f3 | true | ipv4，禁用原因清空 |
| tailscale0 | false | 无主表默认路由 |
| vmnet1 / vmnet8 | false | 不受 NetworkManager 管理 |
| USB 有线网卡 | 不列出 | 检查时未连接、无有效地址 |

另使用只允许 GetAll/GetPermissions 的只读客户端调用选择当前无线出口路径，返回“已是主路由表默认出口”，未创建检查点、未调用 Reapply 或任何授权方法。
这验证了菜单禁用问题确已修复，但不代表存在第二个可用出口。当前只能在接通并配置有默认网关的另一张网卡后，进行真正的不同出口切换。

## 边界

没有执行真实双网卡切换，未修改路由、VPN、DNS 或用户配置。实际写入和回滚仍由模拟事务测试覆盖。
非零标记流量/专用目的网段仍遵循原策略；主表切换不等于全流量改道。表读取失败、未知选择条件或 VPN 接管默认时继续保守拒绝。
不代表支持所有策略路由组合或所有 VPN 客户端。最终单文件记录见 BUILD_MANIFEST、PACKAGE_SELF_TEST、PACKAGE_SMOKE_TEST 与 VALIDATION_REPORT。

## 最终单文件验证

版本 `0.7.2+build.20260920.1`，在临时工作目录、`PATH=/nonexistent` 且清除外部 Python/Qt 插件路径的真实 X11 环境：
- `--self-test`、`--smoke-test` 均退出 0、`ok=true`；路由菜单读取、设置、关于及退出检查全部通过。
- 单文件 `--default-route-control` list 实测 wlp0s20f3：`enabled=true`、`default_for=["ipv4"]`、`reason=""`。
- tailscale0 无主表默认路由、vmnet1/vmnet8 未由 NetworkManager 管理，仍正确禁用。
- 包内版本和干净源码快照一致，SHA256 校验及传输包执行权限检查通过。
- 未执行实际路由写入，未在本轮重复访问公网回显服务。
