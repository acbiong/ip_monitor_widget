#!/usr/bin/env bash
set -euo pipefail
# 从脚本所在目录启动，保证相对模块导入不受调用位置影响。
cd "$(dirname "$0")"
exec python3 main.py
