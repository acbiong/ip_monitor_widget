# 公网运营商测试报告

日期：2026-09-21；基础版本：0.10.0；分支：feature/public-ip-operator。

## 源码验证

- 离线回归：`QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_PLUGIN_PATH= QT_QPA_PLATFORM_PLUGIN_PATH= PYTHONDONTWRITEBYTECODE=1 <构建虚拟环境>/bin/python -B -m unittest discover -s src/tests -v`。
- 结果：112 项通过，新增运营商 22 项；全部网络响应由模拟服务或本地临时 worker 提供。
- 覆盖中文别名、非法地址拒绝、IPv6、请求 IP/ASN 校验、多源 ASN、TLS 请求选项、响应限长、缓存过期/容量/去重、失败恢复、异步队列、看门狗与退出。
- Qt 界面模拟验证：多网卡不串结果、地址变化不沿用旧运营商、热插拔清理标签、双栈分行、放大字体后标签宽高不小于内容尺寸。
- 当前 X11 桌面运行源码 `--smoke-test`：设置实时预览/取消、固定尺寸、黑字、关于、托盘、只读默认路由及进程清理通过；使用临时配置，无用户配置修改。

## 授权联网验证

- RIPE 官方接口公开测试地址返回预期 JSON 协议；AS4134 登记名称为 CHINANET-BACKBONE，映射中国电信。
- 使用原有网卡绑定查询获取当前公网地址，再通过真实 `OperatorService`/QProcess 查询元数据：`wlp0s20f3` 的 IPv4 出口成功标注“中国电信”。
- `tailscale0`、`vmnet1`、`vmnet8` 本次未取得有效公网 IP，不请求归属、不借用无线结果。
- 公开电信 IPv4 测试地址识别为中国电信；公开 IPv6 测试地址取得归属但不在中文别名表，按设计显示其他运营商。
- 不记录本机公网 IP，不修改路由、DNS、VPN、自启动或用户配置。

## 验证边界

- 电信为真实联网结果；联通、移动等别名及公网地址变化为模拟验证，不冒充不同宽带实测。
- ASN 是公网出口归属，不保证等于签约宽带运营商。未收录机构、服务故障和限流均有明确降级。
- 目标为本机 deepin 25 x86_64；未在另一台电脑或其他架构上验证。
- 单文件构建及后续测试结果在本报告的交付验证节、`PACKAGE_SELF_TEST.json`、`PACKAGE_SMOKE_TEST.json` 和 `VALIDATION_REPORT.md` 中记录。


## 交付验证

- 构建命令：`SKIP_INSTALL=1 PYTHONDONTWRITEBYTECODE=1 ./src/packaging/build.sh`。
- 构建版本：`0.10.0+build.20260921.1`；源码快照：`95160e9a5ab72c901637a3ac18401d100ead5365`；构建前 Git 工作树干净。
- 新增 `operator_entry` 自检及 `operator_row` 图形检查均通过；退出后包含运营商在内的全部工作进程已回收。
- 临时目录中清空外部 Python/Qt 环境、设 `PATH=/nonexistent`，单文件 `--self-test` 与 X11 `--smoke-test` 均通过。
- 同样在不依赖系统 Python 的环境中，冻结入口 `--operator-lookup` 成功取得公开电信测试地址 ASN 4134 并输出“中国电信”。
- `(cd dist && sha256sum -c SHA256SUMS)` 两项通过；传输包中文件保留 755 执行权限。
- 本次未启动常驻新版窗口或关闭用户正在运行的旧版，退出旧版后运行新文件即可使用。
