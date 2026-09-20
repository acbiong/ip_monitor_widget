"""出口控制异步进程边界：限制并发、超时和输出长度，避免阻塞托盘。"""

import json
from pathlib import Path
import sys

from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal


class RouteSwitchService(QObject):
    """每次只运行一个任务；切换结束返回真实状态，枚举不触发授权。"""

    result = pyqtSignal(object)
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.switching = False
        self._stopped = False
        self._output = bytearray()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._timeout)

    def refresh(self):
        self._start({"action": "list"})

    def switch(self, name, uuid):
        return self._start({"action": "switch", "name": name, "uuid": uuid})

    def _start(self, request):
        if self.process is not None or self._stopped:
            return False
        self.switching = request["action"] == "switch"
        self._output = bytearray()
        self._failure = ""
        process = QProcess(self)
        self.process = process
        process.readyReadStandardOutput.connect(self._read)
        process.readyReadStandardError.connect(lambda: process.readAllStandardError())
        process.finished.connect(lambda code, status: self._finish(process, code, status))
        process.errorOccurred.connect(lambda error: self._error(process, error))
        arguments = ["--default-route-control"]
        if not getattr(sys, "frozen", False):
            arguments.insert(0, str(Path(__file__).parent / "main.py"))
        process.start(sys.executable, arguments)
        process.write(json.dumps(request).encode())
        process.closeWriteChannel()
        self._timer.start(75000 if self.switching else 12000)
        return True

    def _read(self):
        if self.process is None:
            return
        self._output.extend(bytes(self.process.readAllStandardOutput()))
        if len(self._output) > 262144:
            self._timeout()

    def _timeout(self):
        self._failure = "默认出口操作超时或响应异常；若切换未完成，系统检查点将在 90 秒内尝试回滚。"
        if self.process is not None:
            self.process.kill()

    def _error(self, process, error):
        if error == QProcess.FailedToStart:
            self._failure = "无法启动默认出口控制进程"
            self._finish(process, -1, QProcess.CrashExit)

    def _finish(self, process, code, status):
        if self.process is not process:
            return
        self._read()
        self._timer.stop()
        try:
            report = json.loads(self._output)
            if not isinstance(report, dict) or not isinstance(report.get("ok"), bool):
                raise ValueError("响应格式错误")
        except (ValueError, UnicodeError):
            report = {"ok": False, "message": "出口控制响应无效，请检查依赖及 NetworkManager 服务"}
        if self._failure or status != QProcess.NormalExit or code != 0:
            report = {"ok": False, "message": self._failure or report.get("message", "出口操作失败")}
        was_switching = self.switching
        self.process = None
        self.switching = False
        process.deleteLater()
        if not self._stopped:
            self.result.emit(report)
            if was_switching:
                self.finished.emit(report)

    def shutdown(self):
        """退出不等待认证；未提交的系统检查点负责自动回滚。"""
        self._stopped = True
        self._timer.stop()
        if self.process is not None:
            self.process.kill()
            self.process.waitForFinished(500)
