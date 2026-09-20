# Git 与关于页面验证报告

日期：2026-09-20；功能版本：0.6.0；工作分支：feature/tray-about-git-info。

## 已完成验证

| 范围 | 结果 | 实测说明 |
|---|---|---|
| 源码与构建脚本 | 通过 | Python 语法、Shell 语法、Git diff 空白检查 |
| Git 元数据 | 14 项通过 | 隔离临时 Git 仓库覆盖干净/修改/已暂存/未跟踪/忽略、分离 HEAD、无仓库、无 Git、超时、状态失败、版本文件不被过滤 |
| 冻结元数据读取 | 通过 | 模拟无 Git、缺失/损坏 JSON、错误字段类型时不崩溃、不调用目标 Git |
| 编译快照顺序 | 通过 | 临时项目中先记录干净提交，再自动递增版本；生成 JSON 版本等于递增结果 |
| 源码 X11 冒烟 | 通过 | 通过真实托盘动作打开/关闭关于页两次，内容、图标、样式和对象释放检查全部为 true |
| 本地异步服务 | 通过 | X11 冒烟检查默认路由、后台入口及退出清理；未发送公网查询 |

Git 元数据隔离测试执行脚本为本次临时文件 `/tmp/check_monitor_about_git.py`，执行命令
`PYTHONDONTWRITEBYTECODE=1 python3 /tmp/check_monitor_about_git.py`，14 项全部通过。
可随项目重新运行的关于页集成检查已写入 `src/package_diagnostics.py` 的 `--smoke-test`。

## 环境与限制

源码 X11 测试使用临时 QSettings，不覆盖原用户设置，不修改网络；DTK 输出托盘注册警告，
但应用侧各检查成功。此前沙箱 offscreen 测试的路由检测失败（routes 为空），
不作为通过证据；已使用真实图形会话复测通过。

Git 测试只使用临时本地仓库，不拉取或推送远程。关于页面开发者名沿用 Biong，
没有新增联系邮箱。任务栏策略未在本轮修改，未重新证明所有窗口管理器兼容性。

## 单文件交付验证

最终包：`0.6.0+build.20260920.3`；内置源码提交：
`7781062e6d2315b75b8bd3c7ac6c66f6f94127dc`；分支：`feature/tray-about-git-info`；
Git 快照 `dirty=false`，UTC 编译时间 `2026-09-20T05:40:51.136146+00:00`。

已将可执行文件单独复制到临时目录，设置 `PATH=/nonexistent`，清除 PYTHONPATH、
PYTHONHOME 及外部 Qt 插件路径，在真实 X11 会话执行 `--self-test` 和 `--smoke-test`。
两者退出码均为 0、`ok=true`；`build_metadata`、`about_fields`、`about_icon`、
`about_style`、`about_open_close` 均为 true。没有 Git/Python 外部命令也能读取完整编译信息。

最终单文件的版本、Git 提交和编译信息以 `../BUILD_MANIFEST.json` 为准；
自检与图形冒烟原始结果保存在本目录 `PACKAGE_SELF_TEST.json` 和 `PACKAGE_SMOKE_TEST.json`。
源码提交与后续构建/测试报告提交可以不同，包内快照保持不可变。
