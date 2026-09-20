# 项目文件与目录清单

> 生成日期：2026-09-20；共 187 个文件夹、206 个文件。

覆盖项目文件、资源、报告、发布产物和 Git 顶层目录；`.git` 内部对象及忽略的编译缓存不展开。

| 相对路径 | 名称 | 类型 | 文件/目录说明 |
|---|---|---|---|
| . | ip_monitor_widget | 文件夹 | 项目根目录，包含源代码、文档、测试清单和发布产物。 |
| .git | .git | 文件夹 | Git 本地版本库元数据目录；表格不展开其中的对象文件。 |
| .gitignore | .gitignore | 文件 | Git 忽略规则，排除 Python 缓存、构建缓存、临时文件和 dist 发布输出。 |
| AGENTS.md | AGENTS.md | 文件 | 项目协作规则，要求独立任务分支、提交、验证与真实构建快照。 |
| README.md | README.md | 文件 | 项目总入口，提供目录导航和核心文档链接。 |
| dist | dist | 文件夹 | 可转移的单文件程序、压缩包和校验和目录。 |
| dist/DesktopMonitor-deepin25-x86_64 | DesktopMonitor-deepin25-x86_64 | 文件 | 面向 deepin 25 x86_64 的 PyInstaller 单文件可执行程序。 |
| dist/DesktopMonitor-deepin25-x86_64.tar.gz | DesktopMonitor-deepin25-x86_64.tar.gz | 文件 | 保留执行权限的单文件传输压缩包。 |
| dist/SHA256SUMS | SHA256SUMS | 文件 | 单文件和传输压缩包的 SHA256 校验值。 |
| docs | docs | 文件夹 | 软件说明、接口、开发规范、审查记录和构建清单目录。 |
| docs/AI_PROGRAMMING_STANDARD.md | AI_PROGRAMMING_STANDARD.md | 文件 | AI 辅助开发、编码、测试和交付规范。 |
| docs/BUILD_MANIFEST.json | BUILD_MANIFEST.json | 文件 | 本次构建版本、平台、依赖和产物校验清单。 |
| docs/CHANGELOG.md | CHANGELOG.md | 文件 | 版本规则和历史变更记录。 |
| docs/CODE_REVIEW.md | CODE_REVIEW.md | 文件 | 代码审查结论、优化记录、回归结果和限制。 |
| docs/GIT_WORKFLOW.md | GIT_WORKFLOW.md | 文件 | 本地仓库、分支提交、忽略规则及构建前 Git 快照流程。 |
| docs/NATIVE_DEPENDENCIES.json | NATIVE_DEPENDENCIES.json | 文件 | 单文件 ELF 原生依赖和 GLIBC 审计结果。 |
| docs/PACKAGING.md | PACKAGING.md | 文件 | 单文件交付方式、依赖范围、兼容边界和打包说明。 |
| docs/README.md | README.md | 文件 | 详细构建、运行、使用、版本和故障排查指南。 |
| docs/SOFTWARE_DEVELOPMENT_SPEC.md | SOFTWARE_DEVELOPMENT_SPEC.md | 文件 | 软件功能、非功能、架构和质量门禁规格。 |
| docs/SOFTWARE_INTERFACE.md | SOFTWARE_INTERFACE.md | 文件 | 软件原理、流程图、模块输入输出和进程协议。 |
| docs/images | images | 文件夹 | README 使用的架构和流程图资源目录。 |
| docs/images/architecture.svg | architecture.svg | 文件 | 软件分层架构图。 |
| docs/images/build-and-use.svg | build-and-use.svg | 文件 | 软件构建、传输和使用流程图。 |
| docs/test_plan | test_plan | 文件夹 | 测试计划目录，与测试报告分离。 |
| docs/test_plan/TEST_PLAN.md | TEST_PLAN.md | 文件 | 模块、集成、回归和交付测试计划。 |
| docs/test_reports | test_reports | 文件夹 | 测试执行结果和交付验证报告目录。 |
| docs/test_reports/GIT_ABOUT_REPORT.md | GIT_ABOUT_REPORT.md | 文件 | Git 元数据、关于页生命周期与构建快照验证结果。 |
| docs/test_reports/PACKAGE_SELF_TEST.json | PACKAGE_SELF_TEST.json | 文件 | 单文件无 GUI 依赖与内部入口自检报告。 |
| docs/test_reports/PACKAGE_SMOKE_TEST.json | PACKAGE_SMOKE_TEST.json | 文件 | 隔离图形会话中的窗口和后台链路冒烟报告。 |
| docs/test_reports/PUBLIC_IP_DNS_REPORT.md | PUBLIC_IP_DNS_REPORT.md | 文件 | Tailscale DNS 环境公网 IP 查询修复、回归和实机验证记录。 |
| docs/test_reports/PUBLIC_IP_INTERVAL_REPORT.md | PUBLIC_IP_INTERVAL_REPORT.md | 文件 | 公网 IP 定时获取间隔功能及模拟变化更新验证记录。 |
| docs/test_reports/ROUTE_POLICY_REPORT.md | ROUTE_POLICY_REPORT.md | 文件 | 默认出口策略误禁用修复、回归和当前网络只读验证报告。 |
| docs/test_reports/ROUTE_SWITCH_REPORT.md | ROUTE_SWITCH_REPORT.md | 文件 | 默认出口菜单及切换功能测试结果和未实机切换边界。 |
| docs/test_reports/SETTINGS_DIALOG_REPORT.md | SETTINGS_DIALOG_REPORT.md | 文件 | 设置页黑字浅底、固定尺寸及预览保存回归报告。 |
| docs/test_reports/VALIDATION_REPORT.md | VALIDATION_REPORT.md | 文件 | 单文件验证范围、结果和兼容边界报告。 |
| docs/third_party_licenses | third_party_licenses | 文件夹 | 第三方 Python、Qt 和系统库许可归档目录。 |
| docs/third_party_licenses/PyQt5-Qt5 | PyQt5-Qt5 | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/PyQt5-Qt5/pyqt5_qt5-5.15.19.dist-info | pyqt5_qt5-5.15.19.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/PyQt5-Qt5/pyqt5_qt5-5.15.19.dist-info/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/PyQt5_sip | PyQt5_sip | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/PyQt5_sip/pyqt5_sip-12.19.0.dist-info | pyqt5_sip-12.19.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/PyQt5_sip/pyqt5_sip-12.19.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/PyQt5_sip/pyqt5_sip-12.19.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/altgraph | altgraph | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/altgraph/altgraph-0.17.5.dist-info | altgraph-0.17.5.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/altgraph/altgraph-0.17.5.dist-info/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/certifi | certifi | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/certifi/certifi-2026.7.22.dist-info | certifi-2026.7.22.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/certifi/certifi-2026.7.22.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/certifi/certifi-2026.7.22.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/charset-normalizer | charset-normalizer | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/charset-normalizer/charset_normalizer-3.5.1.dist-info | charset_normalizer-3.5.1.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/charset-normalizer/charset_normalizer-3.5.1.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/charset-normalizer/charset_normalizer-3.5.1.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/dbus-next | dbus-next | 文件夹 | 第三方组件许可证目录。 |
| docs/third_party_licenses/dbus-next/dbus_next-0.2.3.dist-info | dbus_next-0.2.3.dist-info | 文件夹 | 第三方组件许可证目录。 |
| docs/third_party_licenses/dbus-next/dbus_next-0.2.3.dist-info/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/dnspython | dnspython | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/dnspython/dnspython-2.8.0.dist-info | dnspython-2.8.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/dnspython/dnspython-2.8.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/dnspython/dnspython-2.8.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/idna | idna | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/idna/idna-3.20.dist-info | idna-3.20.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/idna/idna-3.20.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/idna/idna-3.20.dist-info/licenses/LICENSE.md | LICENSE.md | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/packaging | packaging | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/packaging/packaging-26.3.dist-info | packaging-26.3.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/packaging/packaging-26.3.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/packaging/packaging-26.3.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/packaging/packaging-26.3.dist-info/licenses/LICENSE.APACHE | LICENSE.APACHE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/packaging/packaging-26.3.dist-info/licenses/LICENSE.BSD | LICENSE.BSD | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip | pip | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip | pip | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info | pip-26.2.1.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src | src | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip | pip | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor | _vendor | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/cachecontrol | cachecontrol | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/cachecontrol/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/certifi | certifi | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/certifi/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/distlib | distlib | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/distlib/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/distro | distro | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/distro/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/idna | idna | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/idna/LICENSE.md | LICENSE.md | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/msgpack | msgpack | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/msgpack/COPYING | COPYING | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/packaging | packaging | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/packaging/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/packaging/LICENSE.APACHE | LICENSE.APACHE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/packaging/LICENSE.BSD | LICENSE.BSD | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/pkg_resources | pkg_resources | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/pkg_resources/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/platformdirs | platformdirs | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/platformdirs/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/pygments | pygments | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/pygments/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/pyproject_hooks | pyproject_hooks | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/pyproject_hooks/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/requests | requests | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/requests/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/resolvelib | resolvelib | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/resolvelib/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/rich | rich | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/rich/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/tomli | tomli | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/tomli/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/tomli_w | tomli_w | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/tomli_w/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/truststore | truststore | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/truststore/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/urllib3 | urllib3 | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip-26.2.1.dist-info/licenses/src/pip/_vendor/urllib3/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor | _vendor | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/cachecontrol | cachecontrol | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/cachecontrol/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/certifi | certifi | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/certifi/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/distlib | distlib | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/distlib/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/distro | distro | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/distro/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/idna | idna | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/idna/LICENSE.md | LICENSE.md | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/msgpack | msgpack | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/msgpack/COPYING | COPYING | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/packaging | packaging | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/packaging/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/packaging/LICENSE.APACHE | LICENSE.APACHE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/packaging/LICENSE.BSD | LICENSE.BSD | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/pkg_resources | pkg_resources | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/pkg_resources/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/platformdirs | platformdirs | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/platformdirs/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/pygments | pygments | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/pygments/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/pyproject_hooks | pyproject_hooks | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/pyproject_hooks/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/requests | requests | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/requests/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/resolvelib | resolvelib | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/resolvelib/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/rich | rich | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/rich/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/tomli | tomli | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/tomli/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/tomli_w | tomli_w | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/tomli_w/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/truststore | truststore | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/truststore/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pip/pip/_vendor/urllib3 | urllib3 | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pip/pip/_vendor/urllib3/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/psutil | psutil | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/psutil/psutil-7.2.2.dist-info | psutil-7.2.2.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/psutil/psutil-7.2.2.dist-info/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pyinstaller | pyinstaller | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pyinstaller-hooks-contrib | pyinstaller-hooks-contrib | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pyinstaller-hooks-contrib/pyinstaller_hooks_contrib-2026.7.dist-info | pyinstaller_hooks_contrib-2026.7.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pyinstaller-hooks-contrib/pyinstaller_hooks_contrib-2026.7.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pyinstaller-hooks-contrib/pyinstaller_hooks_contrib-2026.7.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/pyinstaller/pyinstaller-6.22.3.dist-info | pyinstaller-6.22.3.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pyinstaller/pyinstaller-6.22.3.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/pyinstaller/pyinstaller-6.22.3.dist-info/licenses/COPYING.txt | COPYING.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/requests | requests | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/requests/requests-2.34.2.dist-info | requests-2.34.2.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/requests/requests-2.34.2.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/requests/requests-2.34.2.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools | setuptools | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools | setuptools | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools-84.0.0.dist-info | setuptools-84.0.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools-84.0.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools-84.0.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor | _vendor | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/autocommand-2.2.2.dist-info | autocommand-2.2.2.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/autocommand-2.2.2.dist-info/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/backports.tarfile-1.2.0.dist-info | backports.tarfile-1.2.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/backports.tarfile-1.2.0.dist-info/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/importlib_metadata-8.7.1.dist-info | importlib_metadata-8.7.1.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/importlib_metadata-8.7.1.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/importlib_metadata-8.7.1.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco.text-4.0.0.dist-info | jaraco.text-4.0.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco.text-4.0.0.dist-info/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco_context-6.1.0.dist-info | jaraco_context-6.1.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco_context-6.1.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco_context-6.1.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco_functools-4.4.0.dist-info | jaraco_functools-4.4.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco_functools-4.4.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/jaraco_functools-4.4.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/more_itertools-10.8.0.dist-info | more_itertools-10.8.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/more_itertools-10.8.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/more_itertools-10.8.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/packaging-26.0.dist-info | packaging-26.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/packaging-26.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/packaging-26.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/packaging-26.0.dist-info/licenses/LICENSE.APACHE | LICENSE.APACHE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/packaging-26.0.dist-info/licenses/LICENSE.BSD | LICENSE.BSD | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/platformdirs-4.4.0.dist-info | platformdirs-4.4.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/platformdirs-4.4.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/platformdirs-4.4.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/tomli-2.4.0.dist-info | tomli-2.4.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/tomli-2.4.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/tomli-2.4.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/wheel-0.46.3.dist-info | wheel-0.46.3.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/wheel-0.46.3.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/wheel-0.46.3.dist-info/licenses/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/zipp-3.23.0.dist-info | zipp-3.23.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/zipp-3.23.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/setuptools/setuptools/_vendor/zipp-3.23.0.dist-info/licenses/LICENSE | LICENSE | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system | system | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/system/iproute2 | iproute2 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/iproute2/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libatomic1 | libatomic1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libatomic1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libbpf1 | libbpf1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libbpf1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libbrotli1 | libbrotli1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libbrotli1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libbz2-1.0 | libbz2-1.0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libbz2-1.0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libcap2 | libcap2 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libcap2/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libdbus-1-3 | libdbus-1-3 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libdbus-1-3/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libdrm2 | libdrm2 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libdrm2/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libelf1 | libelf1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libelf1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libexpat1 | libexpat1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libexpat1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libffi8 | libffi8 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libffi8/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libfontconfig1 | libfontconfig1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libfontconfig1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libfreetype6 | libfreetype6 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libfreetype6/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libgcc-s1 | libgcc-s1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libgcc-s1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libgcrypt20 | libgcrypt20 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libgcrypt20/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libglib2.0-0 | libglib2.0-0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libglib2.0-0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libglvnd0 | libglvnd0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libglvnd0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libglx0 | libglx0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libglx0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libgpg-error0 | libgpg-error0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libgpg-error0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libgssapi-krb5-2 | libgssapi-krb5-2 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libgssapi-krb5-2/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libk5crypto3 | libk5crypto3 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libk5crypto3/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libkeyutils1 | libkeyutils1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libkeyutils1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libkrb5-3 | libkrb5-3 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libkrb5-3/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libkrb5support0 | libkrb5support0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libkrb5support0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/liblz4-1 | liblz4-1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/liblz4-1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/liblzma5 | liblzma5 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/liblzma5/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libmnl0 | libmnl0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libmnl0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libpcre2-8-0 | libpcre2-8-0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libpcre2-8-0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libpng16-16 | libpng16-16 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libpng16-16/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libpython3.12 | libpython3.12 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libpython3.12/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libreadline8 | libreadline8 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libreadline8/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libselinux1 | libselinux1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libselinux1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libssl3 | libssl3 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libssl3/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libstdc++6 | libstdc++6 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libstdc++6/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libsystemd0 | libsystemd0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libsystemd0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libtinfo6 | libtinfo6 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libtinfo6/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libwayland-client0 | libwayland-client0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libwayland-client0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libwayland-cursor0 | libwayland-cursor0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libwayland-cursor0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libwayland-egl1 | libwayland-egl1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libwayland-egl1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libx11-6 | libx11-6 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libx11-6/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libx11-xcb1 | libx11-xcb1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libx11-xcb1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxau6 | libxau6 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxau6/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-glx0 | libxcb-glx0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-glx0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-icccm4 | libxcb-icccm4 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-icccm4/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-image0 | libxcb-image0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-image0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-keysyms1 | libxcb-keysyms1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-keysyms1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-randr0 | libxcb-randr0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-randr0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-render-util0 | libxcb-render-util0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-render-util0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-render0 | libxcb-render0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-render0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-shape0 | libxcb-shape0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-shape0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-shm0 | libxcb-shm0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-shm0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-sync1 | libxcb-sync1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-sync1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-util1 | libxcb-util1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-util1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-xfixes0 | libxcb-xfixes0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-xfixes0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-xinerama0 | libxcb-xinerama0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-xinerama0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb-xkb1 | libxcb-xkb1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb-xkb1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcb1 | libxcb1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcb1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxcomposite1 | libxcomposite1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxcomposite1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxdmcp6 | libxdmcp6 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxdmcp6/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxext6 | libxext6 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxext6/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxkbcommon-x11-0 | libxkbcommon-x11-0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxkbcommon-x11-0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxkbcommon0 | libxkbcommon0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxkbcommon0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libxxhash0 | libxxhash0 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libxxhash0/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/libzstd1 | libzstd1 | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/libzstd1/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/system/zlib1g | zlib1g | 文件夹 | 随单文件打包的系统原生库许可归档目录。 |
| docs/third_party_licenses/system/zlib1g/copyright | copyright | 文件 | 第三方组件许可证或版权声明文件。 |
| docs/third_party_licenses/urllib3 | urllib3 | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/urllib3/urllib3-2.8.0.dist-info | urllib3-2.8.0.dist-info | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/urllib3/urllib3-2.8.0.dist-info/licenses | licenses | 文件夹 | 对应第三方 Python/Qt 组件的许可归档目录。 |
| docs/third_party_licenses/urllib3/urllib3-2.8.0.dist-info/licenses/LICENSE.txt | LICENSE.txt | 文件 | 第三方组件许可证或版权声明文件。 |
| src | src | 文件夹 | 源代码、资源和构建脚本目录。 |
| src/VERSION.json | VERSION.json | 文件 | 版本状态，保存基础版本、构建号、构建后缀和完整版本。 |
| src/about_dialog.py | about_dialog.py | 文件 | 固定尺寸、名称居中的关于页面，显示版本、开发者、Git 和编译信息。 |
| src/build_info.py | build_info.py | 文件 | 运行时读取源码 Git 信息或单文件内置编译信息。 |
| src/config.py | config.py | 文件 | 应用常量、默认设置、公网服务地址和超时参数。 |
| src/cpu_temperature.py | cpu_temperature.py | 文件 | 识别并读取 CPU 温度传感器。 |
| src/default_route.py | default_route.py | 文件 | 读取 IPv4/IPv6 默认路由并选择默认出口网卡。 |
| src/interface_dns.py | interface_dns.py | 文件 | 设备绑定 DNS 解析及限时系统解析回退，兼容 VPN DNS 代理。 |
| src/main.py | main.py | 文件 | 应用入口，处理 GUI、诊断、后台查询和版本命令行模式。 |
| src/monitor_widget.py | monitor_widget.py | 文件 | 桌面监视器主窗口、布局、拖动、置底和内容刷新。 |
| src/network.py | network.py | 文件 | 枚举在线网卡、过滤有效地址并生成网卡快照。 |
| src/package_diagnostics.py | package_diagnostics.py | 文件 | 单文件依赖自检、版本自检和图形冒烟测试入口。 |
| src/packaging | packaging | 文件夹 | PyInstaller 构建、版本管理、依赖审计和发布脚本目录。 |
| src/packaging/audit.py | audit.py | 文件 | 审计单文件 ELF 依赖、动态库闭包和最低 GLIBC。 |
| src/packaging/build-requirements.txt | build-requirements.txt | 文件 | 冻结构建所需的锁定 Python 依赖。 |
| src/packaging/build.sh | build.sh | 文件 | 版本递增、PyInstaller 构建、依赖审计、自检和发布文件生成脚本。 |
| src/packaging/generate_build_info.py | generate_build_info.py | 文件 | 构建时生成嵌入单文件的 Git 和编译信息快照。 |
| src/packaging/monitor.spec | monitor.spec | 文件 | PyInstaller 单文件构建配置和内置资源清单。 |
| src/packaging/release.py | release.py | 文件 | 生成传输包、SHA256、构建清单和第三方许可归档。 |
| src/packaging/runtime_env.py | runtime_env.py | 文件 | 冻结程序运行时 Qt 插件和图形环境隔离钩子。 |
| src/packaging/version_manager.py | version_manager.py | 文件 | 设置基础 SemVer 版本并递增每次编译的 build 后缀。 |
| src/public_ip_lookup.py | public_ip_lookup.py | 文件 | 公网 IP 查询子进程，负责绑定网卡并输出 JSON。 |
| src/public_ip_service.py | public_ip_service.py | 文件 | 公网查询队列、并发限制、超时、重试和结果隔离。 |
| src/requirements.txt | requirements.txt | 文件 | 源码运行依赖清单。 |
| src/resources | resources | 文件夹 | 程序图标等运行时资源目录。 |
| src/resources/icon.svg | icon.svg | 文件 | 系统托盘和窗口使用的 SVG 图标。 |
| src/route_menu.py | route_menu.py | 文件 | 默认出口二级菜单、真实勾选、禁用原因与切换通知。 |
| src/route_policy.py | route_policy.py | 文件 | 只读评估策略路由是否接管默认出口，兼容 Tailscale 普通组网规则。 |
| src/route_switch_service.py | route_switch_service.py | 文件 | 默认出口控制 QProcess 服务，负责并发限制、超时与退出清理。 |
| src/route_switch_worker.py | route_switch_worker.py | 文件 | NetworkManager 临时默认路由切换与检查点回滚后台模块。 |
| src/run.sh | run.sh | 文件 | 源码启动脚本。 |
| src/settings_dialog.py | settings_dialog.py | 文件 | 黑字浅底、固定尺寸的设置窗口及实时预览、取消回滚和默认值恢复。 |
| src/settings_store.py | settings_store.py | 文件 | 校验并持久化用户设置、窗口位置和锁定状态。 |
| src/system_metrics.py | system_metrics.py | 文件 | 采集 CPU、内存、磁盘、流量和温度等系统指标。 |
| src/tests | tests | 文件夹 | 源代码回归测试；网络写操作均使用模拟对象。 |
| src/tests/test_interface_dns.py | test_interface_dns.py | 文件 | DNS 代理回退、超时预算和 HTTPS 网卡隔离回归测试。 |
| src/tests/test_public_ip_interval.py | test_public_ip_interval.py | 文件 | 公网刷新间隔配置、持久化、预览回滚及自动更新回归测试。 |
| src/tests/test_route_policy.py | test_route_policy.py | 文件 | 策略路由分类、默认接管保护和 Tailscale 兼容回归测试。 |
| src/tests/test_route_switch.py | test_route_switch.py | 文件 | 默认出口规划、授权回滚、菜单与安全边界的隔离单元测试。 |
| src/tray_controller.py | tray_controller.py | 文件 | 系统托盘菜单、设置窗口、位置恢复和退出清理。 |
| src/utils.py | utils.py | 文件 | 速率格式化、网络签名和通用辅助函数。 |
| src/version.py | version.py | 文件 | 运行时读取 VERSION.json 并提供当前完整版本字符串。 |
| tables | tables | 文件夹 | 项目结构和文件说明表格目录。 |
| tables/PROJECT_FILE_INVENTORY.csv | PROJECT_FILE_INVENTORY.csv | 文件 | 项目所有目录和文件的 CSV 清单，可导入表格软件。 |
| tables/PROJECT_FILE_INVENTORY.md | PROJECT_FILE_INVENTORY.md | 文件 | 项目所有目录和文件的可读 Markdown 清单。 |
| tables/README.md | README.md | 文件 | 表格目录说明和清单文件用途。 |
