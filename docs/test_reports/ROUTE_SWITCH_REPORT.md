# 默认出口切换验证报告

日期：2026-09-20；功能版本：0.7.0；分支：`feature/default-route-switch`。

## 范围

新增 `route_menu.py`、`route_switch_service.py`、`route_switch_worker.py`，托盘和内部命令入口接入。
不改变桌面置底、设置预览/回滚或网卡独立公网查询逻辑；网络修改仅由用户点击触发。

## 已完成

- Python 语法及 Git 空白检查通过。
- 28 项 unittest 全部通过：路由规划、同优先级竞争、IPv4/IPv6、静态路由、规则保护、连接变化、授权拒绝、验证失败/取消回滚、回滚失败反馈和菜单勾选/隐藏。
- 命令：`QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_PLUGIN_PATH= QT_QPA_PLATFORM_PLUGIN_PATH= PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s src/tests -v`；使用安装了构建依赖的项目虚拟环境。
- 真实系统只读枚举正确识别 wlp0s20f3 为 IPv4 默认出口；vmnet1/vmnet8 显示为未受 NetworkManager 管理且禁用，不包含公网 IP。
- 对真实活动连接执行只读 GetAppliedConnection，配置版本和 Variant 数据在内存转换成功；未调用 Reapply 或创建检查点。
- 真实 X11 源码 `--smoke-test` 全部通过，新增 `route_menu_readonly=true`；原关于、设置预览/保存/取消、路由读取及退出检查仍通过。
- 首次测试受外部 Qt 插件环境影响而未启动，清除外部插件路径并显式使用 offscreen 后复测 28 项通过；不将首次失败计为成功。

## 验证边界

为避免中断用户现有网络，**未在真实网卡上执行路由切换或认证/回滚**；全部写事务通过模拟 D-Bus 验证。
当前实机只有一个受管理且带默认路由的连接；双物理网卡、多系统认证代理及真实断网回滚仍需用户在受控环境验收。
菜单切换是临时配置，不保证目标网卡能联网，也不承诺所有 NetworkManager/Polkit 策略都可授权。
系统无 NetworkManager 1.42+ 时切换不可用，其他监测不受影响。源代码需安装新增 dbus-next；单文件内置它。

## 构建记录

最终版本、依赖和源码快照见 `../BUILD_MANIFEST.json`；单文件自检/图形结果见
`PACKAGE_SELF_TEST.json`、`PACKAGE_SMOKE_TEST.json` 和 `VALIDATION_REPORT.md`。

最终单文件版本：`0.7.0+build.20260920.1`。在临时工作目录、`PATH=/nonexistent` 且清除外部 Python/Qt 路径的真实 X11 环境中：
- `--self-test` 返回 0，`route_control_entry=true`，内置 dbus-next 0.2.3。
- `--smoke-test` 返回 0，`route_menu_readonly=true`，关于页、设置页、默认路由、后台进程及退出检查全部通过。
- 单独执行 `--default-route-control` 的 list 请求正确返回真实候选网卡、IPv4 勾选和 vmnet 禁用状态；没有依赖 PATH 中的 Python、Git、nmcli 或 ip 命令。
- 包内版本与干净源码 Git 快照一致，SHA256 校验及压缩包执行权限检查通过。
