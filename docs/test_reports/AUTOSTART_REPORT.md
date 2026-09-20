# 用户登录自启动验证报告

日期：2026-09-20；版本：0.9.0；分支：`feature/login-autostart`。

## 范围

新增 src/autostart.py，设置页增加复选开关，MonitorWidget 提供测试注入，package_diagnostics 覆盖开关状态与文件提交。
默认关闭，仅保存时写当前用户 desktop 启动项；无需 root，不修改其他启动文件、路由或 DNS。

## 自动测试

src/tests/test_autostart.py 新增 20 项：默认无写入、启停及状态重读、XDG 路径、冻结/源码路径、安全转义、非法路径、文件校验、原子失败、其他项/符号链接保护、取消、保存、默认恢复及错误反馈。
与原测试合计 90 项通过，无跳过项。首次特殊路径夹具采用 shlex 时未处理其保留美元符/反引号转义的差异，修正夹具后复测通过，并追加真实 Gio 解析验证而非只依赖模拟。
命令：`QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_PLUGIN_PATH= QT_QPA_PLATFORM_PLUGIN_PATH= PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s src/tests -v`，使用项目构建环境。

## 桌面格式和真实解析

- desktop-file-validate 检查启用及 Hidden 禁用文件通过。
- 系统 Gio.DesktopAppInfo 在临时目录解析并实际运行测试脚本，中文、空格、百分号、双引号、美元符、反引号和反斜杠路径保持原样，没有 shell 展开。
- 真实 X11 源码 --smoke-test 全部通过，autostart_* 检查全 true；设置黑字、固定尺寸、预览/取消和关于页等未回归。

## 隔离和边界

测试只写临时配置目录，不写 ~/.config/autostart，不为用户启用真实开机启动，不注销或重启系统。
实际桌面重新登录启动尚未执行；用户启用保存后可自行验证。源码启动依赖保留源码及 Python 环境，单文件依赖保留启用时路径；软件移动后需重新保存启用。
这里只管理固定文件名的本软件用户启动项；不清理其他工具创建的不同名称条目，不新增单实例机制。
最终单文件及图形结果见 BUILD_MANIFEST、PACKAGE_SELF_TEST、PACKAGE_SMOKE_TEST、VALIDATION_REPORT。

## 最终单文件验证

`0.9.0+build.20260920.1` 在临时目录、`PATH=/nonexistent` 且清除外部 Python/Qt 路径的真实 X11 环境执行 `--self-test` 和 `--smoke-test`，均退出 0、`ok=true`。
全部 autostart_* 字段为 true；默认关闭、保存启用、取消不写及关闭启动项通过，设置字体/固定尺寸、关于页、公网间隔和退出清理仍正常。
版本和干净源码快照一致，传输包执行权限与 SHA256 校验通过；用户真实自启动目录未改动。实际重新登录验收仍由用户启用后进行。
