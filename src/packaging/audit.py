"""审计单文件内部 ELF 依赖及 GLIBC 版本，不依赖构建目录运行程序。"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from PyInstaller.archive.readers import CArchiveReader


def main() -> int:
    executable = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    archive = CArchiveReader(str(executable))
    versions = set()
    missing = {}
    external = set()
    native_paths = []
    allowed_system = {"libc.so.6", "libm.so.6", "libdl.so.2", "libpthread.so.0", "librt.so.1",
                      "libutil.so.1", "libresolv.so.2", "ld-linux-x86-64.so.2"}
    with tempfile.TemporaryDirectory(prefix="ip-monitor-elf-audit-") as directory:
        root = Path(directory)
        for name, entry in archive.toc.items():
            target = root / name
            if target.is_absolute() and not target.resolve().is_relative_to(root):
                raise ValueError("打包条目超出审计目录")
            if entry[-1] not in ("b", "n"):
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            data = archive.extract(name)
            if entry[-1] == "n":
                target.symlink_to(data.rstrip(b"\0").decode())
            else:
                target.write_bytes(data)
                target.chmod(0o755)
                if data.startswith(b"\x7fELF"):
                    native_paths.append(target)
        environment = dict(os.environ)
        environment["LD_LIBRARY_PATH"] = str(root) + ":" + str(root / "PyQt5" / "Qt5" / "lib")
        for path in [executable] + native_paths:
            label = path.name if path == executable else str(path.relative_to(root))
            result = subprocess.run(["ldd", str(path)], env=environment, capture_output=True, text=True, timeout=15)
            absent = [line.strip() for line in result.stdout.splitlines() if "not found" in line]
            if absent:
                missing[label] = absent
            for match in re.finditer(r"=>\s+(/\S+)", result.stdout):
                dependency = Path(match.group(1))
                if not dependency.is_relative_to(root):
                    external.add(dependency.name)
            info = subprocess.run(["readelf", "--version-info", str(path)], capture_output=True, text=True, timeout=15)
            versions.update(tuple(map(int, value.split("."))) for value in re.findall(r"GLIBC_(\d+\.\d+(?:\.\d+)?)", info.stdout))
    report = {
        "binary": executable.name,
        "elf_files_checked": len(native_paths) + 1,
        "archive_entries": len(archive.toc),
        "uncompressed_bytes": sum(entry[2] for entry in archive.toc.values()),
        "minimum_glibc_from_symbols": ".".join(map(str, max(versions))) if versions else None,
        "external_libraries": sorted(external),
        "unexpected_external_libraries": sorted(external - allowed_system),
        "missing_libraries": missing,
    }
    report["ok"] = not missing and not report["unexpected_external_libraries"]
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
