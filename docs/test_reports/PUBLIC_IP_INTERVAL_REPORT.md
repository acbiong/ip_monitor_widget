# 公网 IP 获取间隔验证报告

日期：2026-09-20；版本：0.8.0；分支：`feature/public-ip-refresh-interval`。

## 修改范围

原公网定时器固定 60 秒，现改为 `public_ip_interval` 配置驱动，默认仍为 60 秒。
修改 config、settings_store、settings_dialog、monitor_widget；同步 package_diagnostics 和接口文档。
不改变网络协议、出口切换、DNS 或用户配置命名空间，不增加真实网络操作。

## 自动测试

`src/tests/test_public_ip_interval.py` 新增 10 项，全套 70 项 unittest 通过：
- 旧配置默认兼容、10–3600 边界和非法值、持久化重载及启动间隔。
- 预览生效、取消回滚、保存、还原默认一次信号、其他设置不重置公网计时器。
- 模拟公网服务，在本机 IP/网卡签名不变的情况下，通过加速后的真实 QTimer 自动发起第二次查询并更新公网显示。
- 退出停止调度，预览未保存时退出仅持久化原间隔。

命令：`QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_PLUGIN_PATH= QT_QPA_PLATFORM_PLUGIN_PATH= PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s src/tests -v`，使用项目构建虚拟环境。

## 源码图形验证

真实 X11 `--smoke-test` 通过。托盘打开设置两次，修改间隔至 10 秒确认计时器为 10000ms，还原默认为 60000ms；取消还原原值，保存 120 秒确认临时配置和计时器均更新。
新增字段 `public_ip_interval_preview`、`public_ip_interval_default` 均 true；黑色文字、固定尺寸、独立样式、关于页、默认出口读取及退出仍通过。

## 验证边界

测试使用临时 QSettings 和模拟/空地址查询，不改变真实用户配置、不访问公网或修改网络。公网 IP 变化更新通过模拟服务返回不同公网地址验证，未人为修改真实运营商/NAT 出口。
用户配置的是触发周期；在途查询/重试会跳过重叠触发，公网服务响应延迟可能超过周期。不承诺实时发现运营商变化。
单文件构建、自检和图形验证见 BUILD_MANIFEST、PACKAGE_SELF_TEST、PACKAGE_SMOKE_TEST 与 VALIDATION_REPORT。
