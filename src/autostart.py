"""用户级 XDG 登录自启动：独立管理 desktop 文件，不提权、不修改系统服务。"""

import configparser
import io
import os
from pathlib import Path
import sys
import tempfile

from config import APP_NAME
from launcher_refresh import refresh_application_cache


ENTRY_NAME = "org.biong.IPMonitorWidget.desktop"


def launch_command():
    """冻结程序使用外部可执行文件，源码保留虚拟环境解释器路径而不解析符号链接。"""
    executable = str(Path(sys.executable).absolute())
    if getattr(sys, "frozen", False):
        return [executable]
    return [executable, str(Path(__file__).resolve().with_name("main.py"))]


def quote_exec_argument(argument):
    """按 desktop Exec 两层转义编码，不通过 shell 解释；百分号转成字面值。"""
    if not argument or any(character in argument for character in ("\0", "\n", "\r")):
        raise ValueError("启动路径为空或包含不支持的换行字符")
    quoted = argument.replace("%", "%%")
    for character in ("\\", '"', "`", "$"):
        quoted = quoted.replace(character, "\\" + character)
    quoted = quoted.replace("\\", "\\\\").replace("\t", "\\t")
    return '"' + quoted + '"'


class AutostartManager:
    """以实际用户启动项为状态来源，默认不创建文件；支持注入临时配置目录。"""

    def __init__(self, config_home=None, command=None, refresh_callback=None):
        home = Path(config_home or os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        if not home.is_absolute():
            home = Path.home() / ".config"
        self.path = home / "autostart" / ENTRY_NAME
        self.command = list(command) if command is not None else launch_command()
        self._refresh_cache = (refresh_callback if refresh_callback is not None else
                               refresh_application_cache if config_home is None else lambda: None)

    def is_enabled(self):
        """读取当前桌面启动项；格式/权限异常交给设置窗口提示，不能伪装成功。"""
        if self.path.is_symlink():
            raise ValueError("启动项是符号链接，请先在系统启动设置中处理")
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return False
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_string(text)
            section = parser["Desktop Entry"]
            return (section.get("Type") == "Application" and bool(section.get("Exec", "").strip())
                    and not section.getboolean("Hidden", False)
                    and section.getboolean("X-GNOME-Autostart-enabled", True))
        except (configparser.Error, KeyError, ValueError) as error:
            raise ValueError("无法解析本软件的自启动项") from error

    def set_enabled(self, enabled):
        """仅在保存时原子写入；关闭保留 Hidden 覆盖项，避免系统同名项继续启动。"""
        current = self.is_enabled()
        if not enabled and not current and not self.path.exists():
            return
        if enabled:
            if (not self.command or not Path(self.command[0]).is_absolute()
                    or not Path(self.command[0]).is_file() or not os.access(self.command[0], os.X_OK)):
                raise ValueError("当前启动程序不可执行，请先将软件放到固定位置")
            if any(not Path(argument).is_absolute() or not Path(argument).is_file()
                   for argument in self.command[1:]):
                raise ValueError("源码启动文件不存在或不是绝对路径")
            entry = ("[Desktop Entry]\nType=Application\n"
                     f"Name={APP_NAME}\nComment=登录桌面后启动本机状态监视器\n"
                     f"Exec={' '.join(quote_exec_argument(argument) for argument in self.command)}\n"
                     "Terminal=false\nNoDisplay=true\nHidden=false\nX-GNOME-Autostart-enabled=true\n")
        else:
            entry = ("[Desktop Entry]\nType=Application\n"
                     f"Name={APP_NAME}\nNoDisplay=true\nHidden=true\nX-GNOME-Autostart-enabled=false\n")
        self._write_entry(entry)

    def repair_visibility(self):
        """升级时修补已有启动项，保留启停状态与原启动命令；首次运行不创建文件。"""
        self.is_enabled()
        if not self.path.exists():
            return
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        try:
            parser.read_string(self.path.read_text(encoding="utf-8"))
            section = parser["Desktop Entry"]
        except (configparser.Error, KeyError) as error:
            raise ValueError("无法解析待修复的自启动项") from error
        keys = [key for key in section if key.lower() == "nodisplay"]
        if len(keys) == 1 and section[keys[0]].lower() == "true":
            self._refresh_cache()
            return
        for key in keys:
            del section[key]
        section["NoDisplay"] = "true"
        stream = io.StringIO()
        parser.write(stream, space_around_delimiters=False)
        self._write_entry(stream.getvalue())

    def _write_entry(self, entry):
        """原子保存成功后再通知应用缓存；注入配置目录时默认不碰真实桌面。"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".ip-monitor-", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(entry)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, 0o644)
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        self._refresh_cache()
