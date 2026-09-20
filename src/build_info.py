"""读取运行时 Git 和编译信息，供关于页面使用。"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUILD_INFO = {
    "developer": "Biong",
    "git": {
        "branch": "未知",
        "commit": "未知",
        "commit_short": "未知",
        "dirty": None,
    },
    "build": {
        "built_at": "源码运行（未冻结编译）",
        "target": "源码运行环境",
        "architecture": "未知",
        "python": sys.version.split()[0],
        "packager": "未冻结",
    },
}


def _run_git(*arguments: str) -> str:
    """读取 Git 信息；目标环境没有 Git 时返回空字符串。"""
    try:
        result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), *arguments],
            capture_output=True,
            text=True,
            timeout=1.5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _source_git_info() -> dict:
    """源码运行时实时读取当前分支、提交和工作树状态。"""
    branch = _run_git("branch", "--show-current") or _run_git("rev-parse", "--short", "HEAD") or "未知"
    commit = _run_git("rev-parse", "HEAD") or "未知"
    short_commit = _run_git("rev-parse", "--short", "HEAD") or "未知"
    status = _run_git("status", "--porcelain")
    return {
        "branch": branch,
        "commit": commit,
        "commit_short": short_commit,
        "dirty": bool(status) if commit != "未知" else None,
    }


def load_build_info() -> dict:
    """优先加载冻结包内的编译快照，否则实时读取源码 Git 信息。"""
    result = json.loads(json.dumps(DEFAULT_BUILD_INFO, ensure_ascii=False))
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    packaged_file = bundle_root / "BUILD_INFO.json"
    if packaged_file.is_file():
        try:
            packaged = json.loads(packaged_file.read_text(encoding="utf-8"))
            result.update(packaged)
            return result
        except (OSError, ValueError, TypeError):
            pass
    result["git"] = _source_git_info()
    return result
