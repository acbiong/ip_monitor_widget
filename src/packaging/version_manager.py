"""维护语义化基础版本及每次编译递增的构建后缀。"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re


VERSION_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def version_file() -> Path:
    """返回源代码目录中的版本状态文件。"""
    return Path(__file__).resolve().parent.parent / "VERSION.json"


def read_info() -> dict:
    """读取并校验版本状态。"""
    path = version_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    base_version = str(data.get("base_version", ""))
    if not VERSION_PATTERN.fullmatch(base_version):
        raise ValueError(f"基础版本号无效：{base_version}")
    return data


def write_info(data: dict) -> None:
    """以稳定格式写回版本状态。"""
    version_file().write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_base_version(base_version: str) -> dict:
    """设置 major/minor/patch 基础版本，并从新的版本线重新计数。"""
    if not VERSION_PATTERN.fullmatch(base_version):
        raise ValueError("基础版本号必须符合 MAJOR.MINOR.PATCH，例如 0.5.0")
    data = read_info()
    data.update({
        "base_version": base_version,
        "build_number": 0,
        "build_suffix": "",
        "version": base_version,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    write_info(data)
    return data


def bump_build() -> dict:
    """每次编译递增构建号，并生成可追踪的 SemVer build metadata。"""
    data = read_info()
    build_number = int(data.get("build_number", 0)) + 1
    build_suffix = f"build.{datetime.now(timezone.utc):%Y%m%d}.{build_number}"
    data.update({
        "build_number": build_number,
        "build_suffix": build_suffix,
        "version": f"{data['base_version']}+{build_suffix}",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    write_info(data)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="管理本机状态监视器版本号")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bump-build", action="store_true", help="递增编译后缀")
    group.add_argument("--set-base-version", metavar="VERSION", help="设置 MAJOR.MINOR.PATCH 基础版本")
    group.add_argument("--show", action="store_true", help="显示当前版本")
    arguments = parser.parse_args()
    if arguments.bump_build:
        data = bump_build()
    elif arguments.set_base_version:
        data = set_base_version(arguments.set_base_version)
    else:
        data = read_info()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
