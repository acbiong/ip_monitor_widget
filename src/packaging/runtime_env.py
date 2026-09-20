"""冻结程序使用随包 Qt 插件，避免继承目标机器不兼容的插件路径。"""

import os
from pathlib import Path
import sys


if getattr(sys, "frozen", False):
    plugins = Path(sys._MEIPASS) / "PyQt5" / "Qt5" / "plugins"
    os.environ["QT_PLUGIN_PATH"] = str(plugins)
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugins / "platforms")
    os.environ["QT_QPA_PLATFORMTHEME"] = ""
    os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
    # 本工具只使用二维控件，避免因目标电脑显卡驱动不同加载多余的 GL 插件。
    os.environ["QT_XCB_GL_INTEGRATION"] = "none"
    if os.environ.get("QT_QPA_PLATFORM") not in ("xcb", "offscreen", "minimal"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"
