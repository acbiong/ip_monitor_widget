#!/usr/bin/env bash
set -euo pipefail
# 构建缓存放到用户缓存目录，项目内只保留源码、文档和交付文件。
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd -- "$script_dir/../.." && pwd)"
cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/ip-monitor-widget"
python="$cache_dir/build-venv/bin/python"
if [[ "$(uname -m)" != x86_64 ]]; then
    printf '该构建配置仅适用于 x86_64。\n' >&2
    exit 1
fi
source /etc/os-release
if [[ "${ID:-}" != deepin || "${VERSION_ID:-}" != 25 ]]; then
    printf '该构建配置的 ABI 基线为 deepin 25，请勿用它误标其他系统的产物。\n' >&2
    exit 1
fi
if [[ ! -x "$python" ]]; then
    python3 -m venv --without-pip "$cache_dir/build-venv"
fi
if [[ "${SKIP_INSTALL:-0}" != 1 ]]; then
    python3 -m pip --python "$python" install -r "$script_dir/build-requirements.txt"
fi
mkdir -p "$project_dir/dist" "$cache_dir/work"
"$python" "$script_dir/version_manager.py" --bump-build
"$python" -m PyInstaller --noconfirm --clean \
    --distpath "$project_dir/dist" --workpath "$cache_dir/work" \
    "$script_dir/monitor.spec"
chmod 755 "$project_dir/dist/DesktopMonitor-deepin25-x86_64"
"$python" "$script_dir/audit.py" "$project_dir/dist/DesktopMonitor-deepin25-x86_64" \
    "$project_dir/docs/NATIVE_DEPENDENCIES.json"
"$project_dir/dist/DesktopMonitor-deepin25-x86_64" --self-test | tee "$project_dir/docs/test_reports/PACKAGE_SELF_TEST.json"
"$python" "$script_dir/release.py" "$project_dir"
