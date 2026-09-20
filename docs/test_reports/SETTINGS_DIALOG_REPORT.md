# 设置窗口样式与尺寸验证报告

日期：2026-09-20；修复版本：0.6.2；分支：`fix/settings-dialog-style-size`。

## 修改范围与风险

- `src/settings_dialog.py`：空样式表无法隔离父窗口白字，改为局部黑字浅底样式，根布局按内容固定尺寸。
- `src/package_diagnostics.py`：增加真实托盘设置动作的回归检查。
- 保持主窗口白字半透明、关于页、预览信号、保存/取消以及位置存储协议不变。
- 风险：父窗口预览更换样式后污染设置页；尺寸固定后控件被裁切。通过最大预览字号下的样式和固定尺寸检查覆盖主要风险。

## 源码验证

命令：`PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=xcb python3 src/main.py --smoke-test`。

真实 X11 会话测试退出码 0，`ok=true`：

| 检查 | 结果 |
|---|---|
| 标签、数值框、按钮黑色文字 | `settings_black_text=true` |
| 不透明浅底、设置页字体隔离 | `settings_style_isolated=true` |
| 实际放大/缩小尝试被限制 | `settings_fixed_size=true` |
| 最大字号、透明度及间隔预览 | `settings_preview=true` |
| 按钮还原默认设置 | `settings_restore_defaults=true` |
| 取消还原、保存至临时配置 | `settings_cancelled=true`、`settings_saved=true` |
| 两次托盘打开/关闭及对象释放 | `settings_open_close=true` |
| 关于页面、默认路由、后台进程及退出清理 | 全部通过 |

测试仅使用临时 QSettings 和空地址 fixture，不修改用户设置，不向公网发送请求。
系统 DTK 输出托盘注册提示，未影响上述检查。未覆盖所有系统主题和显示缩放比例。

## 单文件交付

最终构建信息见 `../BUILD_MANIFEST.json`，自检与 X11 冒烟结果见
`PACKAGE_SELF_TEST.json`、`PACKAGE_SMOKE_TEST.json` 和 `VALIDATION_REPORT.md`。

最终单文件 `0.6.2+build.20260920.1` 在临时工作目录、`PATH=/nonexistent` 且清除外部 Python/Qt 插件路径的真实 X11 环境下，`--self-test` 和 `--smoke-test` 均返回 0，全部设置项检查及总结果均为 true。版本与干净源码 Git 快照一致；SHA256 校验和与压缩包执行权限检查通过。
