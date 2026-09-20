"""deepin 25 x86_64 单文件构建，资源和原生 ip 工具一起内置。"""

from pathlib import Path
import os
import shutil
import subprocess

from PyInstaller.utils.hooks import copy_metadata


source = Path(SPECPATH).resolve().parent
build_info_path = Path(os.environ.get("IP_MONITOR_BUILD_INFO", ""))
if not build_info_path.is_file():
    raise SystemExit("构建环境缺少 BUILD_INFO.json，请先由 build.sh 生成")
ip_command = shutil.which("ip")
if not ip_command:
    raise SystemExit("构建机缺少 iproute2 的 ip 命令")

metadata = []
for package in ("PyQt5", "PyQt5-Qt5", "PyQt5-sip", "psutil", "requests", "dnspython",
                "certifi", "urllib3", "charset-normalizer", "idna"):
    metadata.extend(copy_metadata(package))

# PyInstaller 默认不收集部分桌面图形库；本包面向相同 deepin 25 ABI，显式内置。
native_libraries = []
for name in ("libEGL.so.1", "libGL.so.1", "libGLX.so.0", "libGLdispatch.so.0",
             "libdrm.so.2", "libwayland-client.so.0", "libwayland-cursor.so.0",
             "libwayland-egl.so.1", "libxcb.so.1"):
    path = Path("/usr/lib/x86_64-linux-gnu") / name
    if not path.is_file():
        raise SystemExit(f"构建机缺少原生库：{path}")
    native_libraries.append((str(path), "."))

analysis = Analysis(
    [str(source / "main.py")],
    pathex=[str(source)],
    binaries=[(ip_command, "bin")] + native_libraries,
    datas=[(str(source / "resources"), "resources"), (str(source / "VERSION.json"), "."),
           (str(build_info_path), ".")] + metadata,
    hiddenimports=["PyQt5.QtSvg"],
    hookspath=[],
    runtime_hooks=[str(source / "packaging" / "runtime_env.py")],
    excludes=["tkinter", "PyQt5.QtQml", "PyQt5.QtQuick", "PyQt5.QtWebEngineWidgets"],
    noarchive=False,
)
# 同时归档原生组件随系统提供的许可声明，并嵌入可执行文件。
notices = source.parent / "docs" / "third_party_licenses" / "system"
owners = set()
for destination, origin, kind in analysis.binaries:
    if kind != "BINARY":
        continue
    result = subprocess.run(["dpkg-query", "-S", str(Path(origin).resolve())],
                            capture_output=True, text=True, check=False)
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            owners.add(line.split(": ", 1)[0].split(":", 1)[0])
for owner in sorted(owners):
    copyright_file = Path("/usr/share/doc") / owner / "copyright"
    if copyright_file.is_file():
        target = notices / owner / "copyright"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(copyright_file, target)
        analysis.datas.append((f"licenses/system/{owner}/copyright", str(target), "DATA"))
archive = PYZ(analysis.pure)
executable = EXE(
    archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="DesktopMonitor-deepin25-x86_64",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
