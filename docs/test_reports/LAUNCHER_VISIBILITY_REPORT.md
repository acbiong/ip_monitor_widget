# 运营商隐藏及启动器图标修复报告

日期：2026-09-21；基础版本：0.10.1；分支：fix/operator-row-launcher。

## 问题定位

- 原运营商渲染始终创建可见行，未取得公网 IP 也展示占位符。本轮改为隐藏包含标题和值的独立容器。
- 旧自启动文件没有 NoDisplay；取消自启动虽将磁盘文件改为 Hidden=true，deepin 应用管理器仍缓存旧 NoDisplay=false/AutoStart=true 记录，其 DesktopSourcePath 指向本软件自启动文件。
- 开始屏幕排列文件含本软件 desktop ID；未发现另行安装的本软件应用快捷方式。并非软件包卸载问题。

## 离线回归

命令：`QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_PLUGIN_PATH= QT_QPA_PLATFORM_PLUGIN_PATH= PYTHONDONTWRITEBYTECODE=1 <构建虚拟环境>/bin/python -B -m unittest discover -s src/tests -v`。

- 全部 124 项通过；新增启动器可见性 12 项，扩展已有运营商断网/恢复/布局测试。
- 运营商隐藏/恢复、可见标签尺寸、热插拔及空/非法地址不查询归属均通过。
- NoDisplay/Hidden 分离、旧文件保持开关与命令、幂等迁移、写失败不刷新、首次运行无副作用、符号链接拒绝、异步通知协议均通过。
- 初次布局测试误要求窗口高度在所有情况下都减少，offscreen 可用高度限制为 600 px，隐藏前后仍受屏幕限制；修正为验证内容高度减少、窗口不增长，不放宽实际隐藏断言。
- 离线测试的配置均在临时目录，真实 D-Bus 已隔离；不联网、不改真实路由或公网 IP。
- 源码 X11 图形 `--smoke-test` 通过，新增 `operator_row_hidden`、`autostart_menu_hidden` 均为 true，既有设置/关于/托盘与退出清理均通过。

## 当前电脑真实清理与验证

- 已将原启动项备份到用户缓存目录的 `ip-monitor-widget/launcher-repair.*` 下。
- 修补当前自启动项 NoDisplay 并请求 deepin 刷新后，应用目录的本软件 Application 接口消失；开始屏幕 `item-arrangement.ini` 中本软件 desktop ID 同步移除。
- 用户授权下暂时启用自启动：应用管理器返回 `NoDisplay=true` 且 `AutoStart=true`，证明隐藏菜单与自动启动相互独立；随后 finally 恢复原关闭状态。
- 恢复后应用目录不再登记本软件；当前自启动仍关闭。没有卸载软件、终止现有软件进程、强制重启桌面或改动其他自启动项。

## 边界

- 真实结果来自当前 deepin 25 x86_64 会话；未执行注销/重启登录，未在其他电脑验证。
- 缓存刷新是针对已存在 deepin 服务的异步通知，其他桌面依赖自身 XDG 刷新机制。
- 当前仍在运行的旧版实例需退出再使用新版，以免旧版设置再次写回旧格式。
- 本轮不改公网查询逻辑、不进行公网联网重测；此前运营商真实联网结果见 OPERATOR_REPORT.md，不能算作本轮重测。


## 单文件交付

- 构建：`SKIP_INSTALL=1 PYTHONDONTWRITEBYTECODE=1 ./src/packaging/build.sh`。
- 版本：`0.10.1+build.20260921.1`；源码快照：`665a7df2bed925139aeaa41a6402a188c090f999`；构建前工作树干净。
- 单文件和压缩包：`dist/DesktopMonitor-deepin25-x86_64`、`dist/DesktopMonitor-deepin25-x86_64.tar.gz`。
- 临时工作目录、`PATH=/nonexistent`、清空外部 Python/Qt 路径运行 `--self-test` 与 X11 `--smoke-test` 均通过。
- 打包程序的 `operator_row_hidden`、`autostart_menu_hidden`、`no_remaining_workers` 均为 true；既有设置预览/取消、关于、托盘与路由只读检测通过。
- 原生依赖审计无缺失；`(cd dist && sha256sum -c SHA256SUMS)` 两项通过；tar 中执行权限保持 755。
- 未停止当前旧版实例。使用者从托盘退出旧版后运行新版，避免旧版覆盖修复后的启动项。
