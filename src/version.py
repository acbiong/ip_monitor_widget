"""读取应用版本信息；版本文件由 packaging/version_manager.py 统一维护。"""

from __future__ import annotations

import json
from pathlib import Path


VERSION_FILE = Path(__file__).resolve().with_name("VERSION.json")
DEFAULT_VERSION_INFO = {
    "product": "本机状态监视器",
    "base_version": "0.5.0",
    "build_number": 0,
    "build_suffix": "",
    "version": "0.5.0",
}


def load_version_info() -> dict:
    """加载版本信息；开发目录缺少版本文件时使用安全默认值。"""
    try:
        data = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return dict(DEFAULT_VERSION_INFO)
    result = dict(DEFAULT_VERSION_INFO)
    result.update(data)
    return result


VERSION_INFO = load_version_info()
BASE_VERSION = str(VERSION_INFO["base_version"])
BUILD_SUFFIX = str(VERSION_INFO.get("build_suffix", ""))
APP_VERSION = str(VERSION_INFO.get("version") or BASE_VERSION)
