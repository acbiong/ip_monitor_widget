"""在构建缓存中生成嵌入单文件的 Git 和编译信息快照。"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess


def run_git(project: Path, *arguments: str) -> str:
    """读取当前源代码提交信息。"""
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *arguments],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="生成单文件编译信息")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--version-file", required=True, type=Path)
    arguments = parser.parse_args()
    project = arguments.project.resolve()
    version = json.loads(arguments.version_file.read_text(encoding="utf-8"))
    commit = run_git(project, "rev-parse", "HEAD") or "未知"
    raw_status = run_git(project, "status", "--porcelain")
    # 构建脚本会自动递增 VERSION.json；该生成性改动不应掩盖源代码的 Git 状态。
    status = "\n".join(
        line for line in raw_status.splitlines()
        if line[3:].strip() != "src/VERSION.json"
    )
    branch = run_git(project, "branch", "--show-current") or "未知"
    try:
        packager = f"PyInstaller {importlib.metadata.version('pyinstaller')}"
    except importlib.metadata.PackageNotFoundError:
        packager = "PyInstaller"
    info = {
        "developer": "Biong",
        "application_version": version["version"],
        "git": {
            "branch": branch,
            "commit": commit,
            "commit_short": commit[:12] if commit != "未知" else "未知",
            "dirty": bool(status) if commit != "未知" else None,
        },
        "build": {
            "built_at": datetime.now(timezone.utc).isoformat(),
            "target": "deepin 25 x86_64, X11 or available XWayland",
            "architecture": platform.machine(),
            "python": platform.python_version(),
            "packager": packager,
        },
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
