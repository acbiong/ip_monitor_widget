# 单文件验证报告

验证日期：2026-09-20

## 验证对象

- 文件：`dist/DesktopMonitor-deepin25-x86_64`
- 应用版本：`0.6.0+build.20260920.3`
- 构建源码分支：`feature/tray-about-git-info`
- 构建源码提交：`7781062e6d2315b75b8bd3c7ac6c66f6f94127dc`（自动递增构建号之前工作树干净）
- 目标：deepin 25、x86_64、glibc 2.38 或更高、X11 或可用的 XWayland
- 传输包：`dist/DesktopMonitor-deepin25-x86_64.tar.gz`
- 校验值：见 `dist/SHA256SUMS` 和 `docs/BUILD_MANIFEST.json`

## 已完成检查

| 检查项 | 结果 | 说明 |
|---|---|---|
| 单文件依赖自检 | 通过 | `--self-test` 检查内置 Python、PyQt5、Qt xcb 插件、CA 证书、`ip` 工具和后台查询入口 |
| Git/编译快照 | 通过 | 包内版本与 manifest 一致；临时目录且 PATH=/nonexistent 时不依赖目标 Git |
| 关于页面 | 通过 | 从真实托盘动作连续两次打开/关闭，字段、图标、样式和对象释放均通过 |
| 清空外部环境自检 | 通过 | 清空 `PATH`、`PYTHONPATH`、`PYTHONHOME`、外部 Qt 插件路径后运行，结果保存在 `docs/test_reports/PACKAGE_SELF_TEST.json` |
| 图形启动冒烟测试 | 通过 | 在隔离临时目录中运行 `--smoke-test`，验证图标、窗口可见、默认路由检测、后台进程链路和退出清理，结果保存在 `docs/test_reports/PACKAGE_SMOKE_TEST.json` |
| 原生依赖审计 | 通过 | `NATIVE_DEPENDENCIES.json` 中记录的 ELF 依赖无缺失外部库，最低 GLIBC 为 2.38 |
| 传输包权限 | 通过 | 压缩包解压后保留单文件执行权限 |

## 冒烟测试结果

`docs/test_reports/PACKAGE_SMOKE_TEST.json` 的关键结果为：

- `icon_rendered: true`
- `window_visible: true`
- `route_detection: true`
- `background_query: true`
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
