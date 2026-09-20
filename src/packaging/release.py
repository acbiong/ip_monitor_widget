"""生成发布校验和、可保留执行权限的传输包及构建依赖记录。"""

import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import sys
import tarfile


def main() -> None:
    project = Path(sys.argv[1]).resolve()
    output = project / "dist"
    executable = output / "DesktopMonitor-deepin25-x86_64"
    transport = output / f"{executable.name}.tar.gz"
    with tarfile.open(transport, "w:gz") as archive:
        archive.add(executable, arcname=executable.name)
    hashes = {}
    for path in (executable, transport):
        with path.open("rb") as stream:
            hashes[path.name] = hashlib.file_digest(stream, "sha256").hexdigest()
    (output / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for name, digest in hashes.items()))
    version_info = json.loads((project / "src" / "VERSION.json").read_text(encoding="utf-8"))
    manifest = {
        "application_version": version_info["version"],
        "base_version": version_info["base_version"],
        "build_number": version_info["build_number"],
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target": "deepin 25 x86_64, X11 or available XWayland",
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "libc": platform.libc_ver(),
        "os_release": platform.freedesktop_os_release(),
        "sha256": hashes,
        "packages": {distribution.metadata["Name"]: distribution.version
                     for distribution in importlib.metadata.distributions()},
    }
    (project / "docs" / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    notices = project / "docs" / "third_party_licenses"
    notices.mkdir(exist_ok=True)
    for distribution in importlib.metadata.distributions():
        for file in distribution.files or []:
            if any(token in file.name.lower() for token in ("license", "licence", "copying")):
                origin = Path(distribution.locate_file(file))
                if origin.is_file():
                    target = notices / distribution.metadata["Name"] / str(file)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(origin, target)
    print(f"单文件输出：{executable}")
    print(f"保留执行权限的传输包：{transport}")


if __name__ == "__main__":
    main()
