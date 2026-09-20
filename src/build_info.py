"""读取运行时 Git 和编译信息，供关于页面使用。"""

from __future__ import annotations

import json
from pathlib import Path
import platform
import subprocess
import sys

from config import DEVELOPER_NAME


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUILD_INFO = {
    "developer": DEVELOPER_NAME,
    "git": {
        "branch": "未知",
        "commit": "未知",
        "commit_short": "未知",
        "dirty": None,
    },
    "build": {
        "built_at": "源码运行（未冻结编译）",
        "target": "源码运行环境",
        "architecture": platform.machine(),
        "python": sys.version.split()[0],
        "packager": "未冻结",
    },
}


def _run_git(project: Path, *arguments: str) -> str | None:
    """保留 Git 输出前导空格；失败与空工作树分别返回 None 和空字符串。"""
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *arguments],
            capture_output=True,
            text=True,
            timeout=1.5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.rstrip("\n") if result.returncode == 0 else None


def read_git_info(project: Path = PROJECT_ROOT) -> dict:
    """读取指定项目的完整 Git 状态，不过滤任何已跟踪修改或未跟踪文件。"""
    commit = _run_git(project, "rev-parse", "HEAD") or "未知"
    branch = _run_git(project, "branch", "--show-current")
    if branch == "":
        branch = "分离 HEAD" if commit != "未知" else "未知"
    status = _run_git(project, "status", "--porcelain=v1", "--untracked-files=normal")
    return {
        "branch": branch or "未知",
        "commit": commit,
        "commit_short": commit[:12] if commit != "未知" else "未知",
        "dirty": bool(status) if commit != "未知" and status is not None else None,
    }


def load_build_info() -> dict:
    """优先加载冻结包内的编译快照，否则实时读取源码 Git 信息。"""
    result = json.loads(json.dumps(DEFAULT_BUILD_INFO, ensure_ascii=False))
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    packaged_file = bundle_root / "BUILD_INFO.json"
    if getattr(sys, "frozen", False):
        result["build"].update({"built_at": "编译信息缺失或损坏", "target": "未知", "packager": "冻结运行"})
        try:
            packaged = json.loads(packaged_file.read_text(encoding="utf-8"))
            if not isinstance(packaged, dict):
                raise ValueError("编译元数据必须为对象")
            for section in ("git", "build"):
                values = packaged.get(section)
                if isinstance(values, dict):
                    result[section].update(values)
            for key in ("developer", "application_version"):
                if isinstance(packaged.get(key), str):
                    result[key] = packaged[key]
        except (OSError, ValueError, TypeError):
            result["build"]["built_at"] = "编译信息缺失或损坏"
        return result
    result["git"] = read_git_info()
    return result
