# 单文件交付与目录说明

更新日期：2026-09-21。当前基础版本：`0.10.1`。构建目标：**deepin 25、x86_64、glibc 2.38 或更高、X11 桌面或可用的 XWayland**。

## 1. 项目分类

```text
ip_monitor_widget/
├── src/                         源代码和资源
│   ├── main.py                  源码/冻结程序共用入口
│   ├── version.py、VERSION.json  版本读取和版本状态
│   ├── about_dialog.py、build_info.py 关于页面和编译信息
│   ├── *.py                     独立功能模块
│   ├── resources/icon.svg       程序图标
│   ├── requirements.txt         源码运行依赖
│   ├── run.sh                   源码启动脚本
│   └── packaging/               构建脚本、锁定依赖、spec、运行时钩子及依赖审计
├── docs/                        相关文档、图示和测试
│   ├── README.md                功能和源码运行说明
│   ├── SOFTWARE_INTERFACE.md    原理、流程图和模块/进程接口
│   ├── CODE_REVIEW.md           历次修改与验证记录
│   ├── PACKAGING.md             本文
│   ├── BUILD_MANIFEST.json      构建环境、准确依赖版本及校验和
│   ├── NATIVE_DEPENDENCIES.json  原生库依赖和 GLIBC 符号审计
│   ├── SOFTWARE_DEVELOPMENT_SPEC.md  软件开发规格书
│   ├── AI_PROGRAMMING_STANDARD.md    AI 编程规范
│   ├── CHANGELOG.md               版本规则和变更履历
│   ├── test_plan/                 测试计划
│   ├── images/                    README 架构和流程图
│   ├── test_reports/              测试报告和交付验证结果
│   └── third_party_licenses/    第三方组件随包附带的许可文本
├── tables/                      项目文件夹和文件表格清单
└── dist/                        打包交付文件
    ├── DesktopMonitor-deepin25-x86_64          单个可执行文件
    ├── DesktopMonitor-deepin25-x86_64.tar.gz   保留执行权限的传输包
    └── SHA256SUMS                             上述两个文件的校验和
```

构建虚拟环境、中间文件和日志位于 `~/.cache/ip-monitor-widget/`，不会混入项目目录。压缩包只是传输用，解压后只有一个可执行文件；两个产物任选一种转移即可。

## 2. 转移到另一台电脑

1. 确认目标是 **deepin 25 x86_64**，不是 ARM64、LoongArch 或较旧 deepin 系统。
2. 推荐复制 `dist/DesktopMonitor-deepin25-x86_64.tar.gz`，在目标电脑解压。它保留执行权限，解压出的唯一程序文件可以单独放在任意目录。
3. 双击 `DesktopMonitor-deepin25-x86_64`；若文件管理器询问是否运行，确认运行即可。**不需要安装 Python、pip、PyQt5、requests、psutil 或 dnspython，也不需要复制 src/docs 文件夹。**
4. 程序固定置底且不抢焦点。启动后请显示桌面查看；托盘图标提供设置、锁定、还原位置和退出。

也可只复制裸可执行文件。若聊天软件、浏览器下载或某些文件系统丢失 Linux 执行权限，在文件属性中勾选“允许作为程序执行”，或运行：

```bash
chmod +x DesktopMonitor-deepin25-x86_64
./DesktopMonitor-deepin25-x86_64
```

文件校验（与 SHA256SUMS 放在同一目录时）：

```bash
sha256sum -c SHA256SUMS
```

这是原生 Linux ELF 单文件，不是安装器、脚本或 AppImage，不依赖 FUSE，不需要管理员权限。启动时会自动将内置环境释放到临时目录，正常退出后清理；临时目录需可写、允许加载可执行文件，并建议至少留有 250 MB 空闲空间。

## 3. 包含哪些环境

- CPython 3.12 运行时、标准库及所需扩展模块。
- PyQt5、Qt 5 库、xcb/offscreen 等平台插件、SVG 图标支持及程序图标。
- requests、urllib3、certifi CA 证书、psutil、dnspython 及其必要依赖。
- 原生 `ip` 路由查询工具及所需共享库，不调用目标机器 PATH 中的 ip。
- 原生库审计中确认需要的 X11/xcb/图形接口库；相关组件的许可文本随资源内置，另在 docs 归档。

准确版本见 `BUILD_MANIFEST.json`、`src/VERSION.json` 和关于页面。本次包固定依赖版本，构建脚本不会静默升级到未记录的版本。

### 版本管理

基础版本遵循 SemVer：不兼容变更递增 `MAJOR`，新增兼容功能递增 `MINOR`，BUG 修复/性能/文档/打包修复递增 `PATCH`。每次执行 `src/packaging/build.sh` 通过 `generate_build_info.py --bump-build` 先快照 Git 状态，再调用版本管理器自动递增 `src/VERSION.json` 的构建号。版本后缀示例为 `0.6.0+build.20260920.3`。需要开始新的版本线时执行 `python3 src/packaging/version_manager.py --set-base-version X.Y.Z`，不要手工修改构建后缀。Git 快照和报告提交的关系见 `GIT_WORKFLOW.md`。

### 兼容边界

单文件打包不能内置或替换整台电脑的内核、显示服务器、系统 glibc、显卡驱动和桌面会话。ELF 符号审计确定本包最低需要 **glibc 2.38**，因此**不能保证在 deepin 20/23 等较旧系统运行**，也不能用于不同 CPU 架构。不能通过复制 libc 或强行更换系统 glibc 来解决兼容问题，应在对应旧系统/架构的构建环境中另做发布包。

目标机需有正常可用的桌面和系统托盘。无图形会话、纯 Wayland 且无 XWayland、禁止执行的临时分区、安全策略禁止运行下载程序等，不是 Python 依赖缺失，可能仍阻止启动。系统提供字体、桌面服务和显卡驱动，包不替换它们。

公网查询依然受目标网络、DNS、防火墙及网卡绑定权限影响；有网络问题时显示“未连接公网”，不代表程序缺少依赖。

## 4. 自检及故障信息

```bash
./DesktopMonitor-deepin25-x86_64 --self-test
./DesktopMonitor-deepin25-x86_64 --smoke-test
```

- `--version`：输出当前基础版本及构建后缀。
- `--self-test`：不打开窗口，输出 JSON，检查资源、证书/TLS、Qt 插件、内置 ip 和后台查询专用入口。成功退出码为 0。构建脚本会将结果保存到 `docs/test_reports/PACKAGE_SELF_TEST.json`。
- `--smoke-test`：使用临时配置显示约三秒并退出，检查图标、窗口、真实本地路由读取和冻结后的 QProcess 查询链路。后台测试任务没有源地址，不发起公网请求；成功退出码为 0。不会覆盖用户原配置。结果归档到 `docs/test_reports/PACKAGE_SMOKE_TEST.json`。
- `--public-ip-lookup`：内部后台入口，通过 stdin/stdout 交换网卡 JSON，不启动 GUI；不应当作普通启动参数使用。

运行中的设置仍保存到用户的 `Biong / IPMonitorWidget` QSettings 命名空间，与源码运行兼容；不会写到可执行文件旁边。转移程序不会携带原电脑的网卡地址、窗口位置或个人设置。

## 5. 从源码运行与重新构建

源码运行：

```bash
cd /home/biong/Documents/code/ip_monitor_widget/src
python3 -m pip install -r requirements.txt
./run.sh
```

重新构建（在 deepin 25 x86_64 上）：

```bash
cd /home/biong/Documents/code/ip_monitor_widget
./src/packaging/build.sh
```

构建需要 Python 3.12、pip、iproute2、binutils、dpkg 查询工具及本机桌面共享库。首次会联网下载锁定的构建依赖到用户缓存目录的独立虚拟环境；不修改系统 Python。构建脚本会校验平台、执行 PyInstaller、审计原生依赖、运行自检，然后生成压缩包和校验和。已准备好相同虚拟环境时可设置 `SKIP_INSTALL=1` 跳过下载。

PyInstaller 构建环境和系统原生库也影响产物，因此锁定 Python 软件包并不意味着不同系统上生成的二进制逐字节一致；每次发布以生成的 manifest、依赖审计和 SHA256SUMS 为准。

第三方组件的原始许可声明见 `third_party_licenses/` 及单文件内置元数据/许可资源。本次没有替用户源代码新增或选择许可证。

## 0.7.0 默认出口控制依赖

单文件新增内置 `dbus-next==0.2.3`，不依赖目标电脑安装 Python、nmcli 或 dbus-next。
切换依赖目标系统的 NetworkManager 1.42+、系统 D-Bus 与桌面 Polkit 认证代理；没有这些主机服务时明确提示不可用，其他监测功能仍可使用。
`--self-test` 使用无效操作验证控制子进程入口，不连接系统总线、不改变路由；`--smoke-test` 额外只读枚举真实网卡。

## 0.9.0 自启动路径

无需新增打包依赖。单文件自启动使用 sys.executable 的绝对路径，不引用 PyInstaller 临时解包目录。
目标桌面需要支持用户级 XDG autostart，当前实现面向 deepin 图形登录会话；不安装系统服务或依赖 root。
移动发布文件后应从新位置重新保存启用状态。单文件自检/冒烟使用临时配置目录验证启动项，不能据此宣称所有桌面登录流程均已实测。
