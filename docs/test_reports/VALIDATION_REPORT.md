# 单文件验证报告

验证日期：2026-09-21

## 验证对象

- 文件：`dist/DesktopMonitor-deepin25-x86_64`
- 应用版本：`0.10.1+build.20260921.1`
- 构建源码分支：`fix/operator-row-launcher`
- 构建源码提交：`665a7df2bed925139aeaa41a6402a188c090f999`（自动递增构建号之前工作树干净）
- 目标：deepin 25、x86_64、glibc 2.38 或更高、X11 或可用的 XWayland
- 传输包：`dist/DesktopMonitor-deepin25-x86_64.tar.gz`
- 校验值：见 `dist/SHA256SUMS` 和 `docs/BUILD_MANIFEST.json`

## 已完成检查

| 检查项 | 结果 | 说明 |
|---|---|---|
| 公网运营商 | 通过 | 无地址整行隐藏、恢复显示、字体与热插拔回归通过；本轮未重新查询真实公网归属 |
| 自启动菜单隔离 | 通过 | 新增 12 项回归；真实启用时 NoDisplay=true/AutoStart=true，关闭后目录及排列残留移除；已恢复原关闭状态 |
| 单文件依赖自检 | 通过 | `--self-test` 检查内置 Python、PyQt5、Qt xcb 插件、CA 证书、`ip` 工具和后台查询入口 |
| Git/编译快照 | 通过 | 包内版本与 manifest 一致；临时目录且 PATH=/nonexistent 时不依赖目标 Git |
| 关于页面 | 通过 | 从真实托盘动作连续两次打开/关闭，字段、图标、样式、固定尺寸、名称居中、标题仅“关于”和对象释放均通过 |
| 设置窗口 | 通过 | 黑字浅底、字号/透明度隔离、固定尺寸、实时预览、默认恢复、取消回滚、保存与对象释放均通过 |
| 默认出口菜单 | 通过（只读） | 内置 dbus-next 和控制入口可用；实际系统枚举正确，未执行真实路由写操作 |
| 公网 DNS 兼容 | 回归通过 | 本次 13 项 DNS/HTTPS 隔离测试通过；0.7.1 的既往实机查询结果见 PUBLIC_IP_DNS_REPORT.md，本次未重复访问公网回显服务 |
| 策略路由兼容 | 回归通过 | 19 项策略判定测试通过；0.7.2 的无线菜单实机结果见 ROUTE_POLICY_REPORT.md，本轮只读默认出口为有线网卡 |
| 公网获取间隔 | 通过 | 10 项配置/定时更新测试及单文件预览、默认恢复、保存/取消同步检查通过 |
| 用户自启动 | 通过（临时目录） | 默认关闭、待保存提交、保存启用、取消及禁用检查通过；desktop 格式与特殊路径启动解析通过，未执行真实注销登录 |
| 清空外部环境自检 | 通过 | 清空 `PATH`、`PYTHONPATH`、`PYTHONHOME`、外部 Qt 插件路径后运行，结果保存在 `docs/test_reports/PACKAGE_SELF_TEST.json` |
| 图形启动冒烟测试 | 通过 | 在隔离临时目录中运行 `--smoke-test`，验证图标、窗口可见、默认路由检测、后台进程链路和退出清理，结果保存在 `docs/test_reports/PACKAGE_SMOKE_TEST.json` |
| 原生依赖审计 | 通过 | `NATIVE_DEPENDENCIES.json` 中记录的 ELF 依赖无缺失外部库，最低 GLIBC 为 2.38 |
| 传输包权限 | 通过 | 压缩包解压后保留单文件执行权限 |

## 冒烟测试结果

`docs/test_reports/PACKAGE_SMOKE_TEST.json` 的关键结果为：

- `route_menu_readonly: true`
- `public_ip_interval_preview: true`
- `public_ip_interval_default: true`
- `autostart_default_off: true`
- `autostart_saved: true`
- `autostart_cancelled: true`
- `autostart_disabled: true`
- `settings_black_text: true`
- `settings_style_isolated: true`
- `settings_fixed_size: true`
- `settings_open_close: true`
- `about_title: true`
- `about_name_centered: true`
- `about_fixed_size: true`
- `about_open_close: true`
- `icon_rendered: true`
- `window_visible: true`
- `route_detection: true`
- `background_query: true`
- `operator_row_hidden: true`
- `autostart_menu_hidden: true`
- `no_remaining_workers: true`
- `ok: true`

测试使用空地址 fixture，不向公网发送请求；默认出口检测读取当前系统路由，测试结束后关闭全部后台任务并退出 Qt 事件循环。

## 可复现命令

在目标桌面会话中执行：

```bash
./DesktopMonitor-deepin25-x86_64 --self-test
./DesktopMonitor-deepin25-x86_64 --smoke-test
```

若文件管理器丢失执行权限：

```bash
chmod +x DesktopMonitor-deepin25-x86_64
```

## 验证边界

本报告验证的是当前构建环境和目标 ABI，不代表已经在所有 deepin 版本、CPU 架构、显示服务器、网卡型号和安全策略中逐一验证。该产物不保证 deepin 20/23 等较旧版本、ARM64/LoongArch、纯 Wayland 且没有 XWayland 的环境。

公网 IP 查询还会受到目标电脑的 DNS、路由、防火墙、代理和网卡实际连通性的影响；查询失败时软件按设计显示“未连接公网”，不等同于单文件依赖缺失。

默认出口真实切换、认证及回滚未在本机执行，以免中断用户网络；28 项模拟测试通过，详情见 `ROUTE_SWITCH_REPORT.md`。目标系统需 NetworkManager 1.42+ 和 Polkit 服务；无此服务时仅切换功能不可用。

0.7.1 DNS 修复新增 13 项回归，与出口切换测试合计 41 项通过。真实公网查询仅在用户授权后访问现有回显服务，不修改路由、DNS、VPN 或用户设置，不在报告保存实际公网 IP。

0.7.2 策略路由评估新增 19 项回归，总计 60 项测试通过；当前网络只读验证无线菜单解除误禁用。未进行真实双网卡切换，不把此前 0.7.1 的公网实测冒充本轮重测。详情见 ROUTE_POLICY_REPORT.md。

0.8.0 全部 70 项测试通过。公网地址变化使用模拟服务和加速 Qt 定时器验证，不修改真实公网出口。单文件新增间隔设置测试使用临时配置，无公网请求；详情见 PUBLIC_IP_INTERVAL_REPORT.md。

0.9.0 全部 90 项回归通过。自启动仅在临时配置目录验证；系统 Gio 实际解析并启动特殊字符路径测试脚本成功。未注册用户真实自启动、未注销/重启桌面；详情见 AUTOSTART_REPORT.md。


0.10.0 全部 112 项回归通过。新增运营商进程、缓存与双栈标签离线验证；当前无线出口真实查询识别为中国电信，另验证 IPv4/IPv6 公共测试地址。单文件自检和图形冒烟在临时目录、PATH=/nonexistent 且清空外部 Python/Qt 路径的环境中通过；SHA256 校验及传输包执行权限检查通过。归属结果来自公网出口 ASN，不保证等于签约宽带机构。未在另一台 deepin 电脑实机验证；详见 OPERATOR_REPORT.md。


0.10.1 全部 124 项回归通过。新增无公网运营商行隐藏和自启动菜单隔离；修补本机旧启动项并刷新缓存，开始屏幕排列中的本软件 ID 已消除。授权临时启用确认自动启动与菜单隐藏同时生效，结束后恢复关闭。源码和冻结程序图形冒烟均通过，单文件在 PATH=/nonexistent 且清空外部 Python/Qt 环境下自检通过；SHA256 与传输执行权限检查通过。未注销/重启、未在其他电脑测试，也未重复此前公网联网验证。详情见 LAUNCHER_VISIBILITY_REPORT.md。
