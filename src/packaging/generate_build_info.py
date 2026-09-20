"""在构建缓存中生成嵌入单文件的 Git 和编译信息快照。"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_info import read_git_info
from config import DEVELOPER_NAME
from version_manager import bump_build, version_file


def main() -> int:
    parser = argparse.ArgumentParser(description="生成单文件编译信息")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--version-file", required=True, type=Path)
    parser.add_argument("--bump-build", action="store_true", help="记录 Git 快照后递增编译后缀")
    arguments = parser.parse_args()
    project = arguments.project.resolve()
    if arguments.bump_build and arguments.version_file.resolve() != version_file().resolve():
        parser.error("递增构建号时只能使用项目 src/VERSION.json")
    git_info = read_git_info(project)
    version = (bump_build() if arguments.bump_build else
               json.loads(arguments.version_file.read_text(encoding="utf-8")))
    try:
        packager = f"PyInstaller {importlib.metadata.version('pyinstaller')}"
    except importlib.metadata.PackageNotFoundError:
        packager = "PyInstaller"
    info = {
        "developer": DEVELOPER_NAME,
        "application_version": version["version"],
        "git": git_info,
        "build": {
            "git_snapshot_stage": "自动递增构建号之前（包括全部未提交修改）",
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
