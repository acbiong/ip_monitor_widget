# Git 版本管理流程

## 仓库与分支

本项目已初始化为本地 Git 仓库。`main` 保存初始化基线；本次功能位于
`feature/tray-about-git-info`。当前未配置远程仓库，也未执行推送。
本地提交身份为 `Biong <biong@localhost>`，其中邮箱只是本机提交占位值，不作为联系邮箱。

每次用户修改请求创建一个独立分支；同一任务可以有实现、修复、测试、构建记录等多个提交。
下次任务从当前已交付提交开始，避免从尚未合并功能的旧 main 丢失改动：

```bash
git status --short --branch
git switch -c feature/下一项功能
# 修改代码、测试，更新版本和文档
git add src docs tables README.md AGENTS.md .gitignore
git diff --cached --check
git commit -m "feat: 描述变更"
```

BUG 修复用 `fix/描述` 分支和 `fix:` 提交；文档用 `docs/描述` 和 `docs:`。
不自动合并 main，不重写已有提交，不自动推送。确认验收后可由维护者决定合并方式。
修改提交身份仅配置本仓库：`git config --local user.name` / `user.email`。

## 忽略规则

`.gitignore` 排除 Python 字节码、测试缓存、虚拟环境、编辑器临时文件、构建缓存、日志、
临时文件、core dump、`.env` 本地配置和 `dist/` 的单文件及压缩包。
PyInstaller `.spec`、锁定依赖、源码版本状态、图标和文档仍然跟踪。
`dist/` 产物保留在磁盘，不因 Git 忽略而被删除；不要使用 `git add -f dist`。

## Git 信息与构建号

1. 先完成源码提交并确认工作树状态。
2. `build.sh` 调用 `generate_build_info.py --bump-build`：先快照 Git，再调用版本管理器递增构建号。
3. 快照包含分支、完整提交和全部未提交变更状态；不通过忽略已跟踪文件伪造干净状态。
4. 生成的 `BUILD_INFO.json` 只放在用户构建缓存中，并随单文件内置。包含 UTC 编译时间、目标、架构、Python 和 PyInstaller 版本。
5. 构建后将 `src/VERSION.json`、构建清单和实测报告另行提交到同一分支。

因此，关于页面里的提交是**构建输入源码提交**，不一定是构建后记录测试报告的最新提交。
包内 Git 状态指**自动递增构建号之前的快照**，不会因目标电脑没有 `.git` 或 Git 命令而改变。
源码运行则读取当前工作树；Git 不存在、命令失败或元数据损坏时明确显示未知，而不冒充干净状态。

## 开发者显示名

关于页面的开发者显示名沿用项目中的 `Biong`，统一由 `src/config.py` 的
`DEVELOPER_NAME` 定义；未提供网站、邮箱或个人身份资料，不虚构这些字段。
