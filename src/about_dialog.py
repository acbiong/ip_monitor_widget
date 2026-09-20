"""关于对话框：展示版本、开发者、Git 和编译信息。"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFormLayout, QLabel, QLayout, QVBoxLayout

from build_info import load_build_info
from config import APP_NAME, DEVELOPER_NAME, ICON_PATH
from version import APP_VERSION


class AboutDialog(QDialog):
    """以只读方式呈现当前应用和构建元数据。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setModal(True)
        self.setMinimumWidth(520)
        font = QApplication.font()
        font_size = f"{font.pixelSize()}px" if font.pixelSize() > 0 else f"{font.pointSizeF()}pt"
        self.setFont(font)
        self.setWindowOpacity(1.0)
        self.setObjectName("AboutDialog")
        self.setStyleSheet(
            "QDialog#AboutDialog { background-color: palette(window); }"
            "QDialog#AboutDialog QLabel { color: palette(window-text); "
            f"font-size: {font_size}; font-weight: normal; }}"
        )
        self._build_ui()

    def _build_ui(self) -> None:
        """创建图标、基本信息和关闭按钮。"""
        info = load_build_info()
        git_info = info.get("git", {})
        build_info = info.get("build", {})

        icon = QLabel()
        icon.setPixmap(QPixmap(str(ICON_PATH)).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setAlignment(Qt.AlignCenter)

        title = QLabel(f"<h2>{APP_NAME}</h2><p>Linux/deepin 桌面状态监视器</p>")
        title.setTextFormat(Qt.RichText)
        title.setAlignment(Qt.AlignCenter)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.addRow("软件版本", QLabel(APP_VERSION))
        form.addRow("开发者", QLabel(str(info.get("developer") or DEVELOPER_NAME)))
        form.addRow("Git 分支", QLabel(str(git_info.get("branch", "未知"))))
        form.addRow("Git 提交", QLabel(str(git_info.get("commit", "未知"))))
        dirty = git_info.get("dirty")
        status = "工作树干净" if dirty is False else "工作树有未提交修改" if dirty is True else "状态未知"
        form.addRow("Git 状态（构建前快照）" if info.get("application_version") else "Git 状态", QLabel(status))
        form.addRow("编译时间", QLabel(str(build_info.get("built_at", "未知"))))
        form.addRow("编译目标", QLabel(str(build_info.get("target", "未知"))))
        form.addRow("编译架构", QLabel(str(build_info.get("architecture", "未知"))))
        form.addRow("Python", QLabel(str(build_info.get("python", "未知"))))
        form.addRow("打包器", QLabel(str(build_info.get("packager", "未知"))))
        for index in range(form.rowCount()):
            value = form.itemAt(index, QFormLayout.FieldRole).widget()
            value.setTextFormat(Qt.PlainText)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        # 根据内容固定窗口尺寸，避免手动缩放，同时适应系统字体大小。
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(buttons)
