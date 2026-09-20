"""默认出口检测：异步读取 Linux 主路由表，不发起网络请求或修改路由。"""

import json
import sys
from pathlib import Path

from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal


def parse_default_interfaces(routes: list[dict]) -> list[str]:
    """选择最低 metric 的有效默认路由；同优先级多路径保留全部设备。"""
    if not isinstance(routes, list):
        raise ValueError("路由响应必须是数组")
    candidates = []
    for route in routes:
        if not isinstance(route, dict):
            raise ValueError("路由条目必须是对象")
        if (route.get("dst") not in ("default", "0.0.0.0/0", "::/0")
                or route.get("type", "unicast") != "unicast"
                or route.get("from", "all") not in ("all", "0.0.0.0/0", "::/0")
                or set(route.get("flags", [])) & {"dead", "linkdown"}):
            continue
        priority = (int(route.get("metric", 0)),
                    {"high": 0, "medium": 1, "low": 2}.get(route.get("pref"), 1))
        if "nhid" in route and "dev" not in route and "nexthops" not in route:
            raise ValueError("独立下一跳对象尚未解析，不能误报为无默认路由")
        for path in route.get("nexthops", [route]):
            name = path.get("dev")
            if (isinstance(name, str) and name
                    and not set(path.get("flags", [])) & {"dead", "linkdown"}):
                candidates.append((priority, name))
    if not candidates:
        return []
    best = min(priority for priority, name in candidates)
    return sorted({name for priority, name in candidates if priority == best})


class DefaultRouteService(QObject):
    """有界异步查询 IPv4/IPv6 默认路由，失败与无默认路由分别返回 None 和 []。"""

    result = pyqtSignal(object)

    def __init__(self, parent=None, command: str | None = None) -> None:
        super().__init__(parent)
        bundled_ip = Path(__file__).resolve().parent / "bin" / "ip"
        self._command = command or (str(bundled_ip) if getattr(sys, "frozen", False) else "ip")
        self._active = {}
        self._results = {}
        self._stopped = False

    def refresh(self) -> None:
        """已有查询时跳过，不在 GUI 线程等待外部命令。"""
        if self._stopped or self._active:
            return
        self._results = {}
        for family, option in (("ipv4", "-4"), ("ipv6", "-6")):
            process = QProcess(self)
            timer = QTimer(process)
            timer.setSingleShot(True)
            self._active[process] = {"family": family, "timer": timer,
                                     "output": bytearray(), "failed": False}
            process.readyReadStandardOutput.connect(lambda proc=process: self._read_output(proc))
            process.readyReadStandardError.connect(lambda proc=process: proc.readAllStandardError())
            process.finished.connect(lambda code, status, proc=process:
                                     self._finish(proc, code if status == QProcess.NormalExit else -1))
            process.errorOccurred.connect(lambda error, proc=process: self._error(proc, error))
            timer.timeout.connect(lambda proc=process: self._timeout(proc))
            timer.start(1500)
            process.start(self._command, ["-j", option, "route", "show", "table", "main", "default"])

    def _read_output(self, process) -> None:
        job = self._active.get(process)
        if job is not None:
            job["output"].extend(bytes(process.readAllStandardOutput()))
            if len(job["output"]) > 65536:
                self._timeout(process)

    def _timeout(self, process) -> None:
        job = self._active.get(process)
        if job is not None:
            job["failed"] = True
            process.kill()

    def _error(self, process, error) -> None:
        if error == QProcess.FailedToStart:
            self._finish(process, -1)

    def _finish(self, process, exit_code) -> None:
        self._read_output(process)
        job = self._active.pop(process, None)
        if job is None:
            return
        job["timer"].stop()
        process.deleteLater()
        interfaces = None
        if exit_code == 0 and not job["failed"]:
            try:
                interfaces = parse_default_interfaces(json.loads(job["output"]))
            except (ValueError, TypeError, AttributeError):
                pass
        self._results[job["family"]] = interfaces
        if not self._stopped and len(self._results) == 2:
            self.result.emit(dict(self._results))

    def shutdown(self) -> None:
        """退出时终止命令及看门狗，不遗留路由查询进程。"""
        self._stopped = True
        processes = list(self._active)
        for process in processes:
            self._active[process]["timer"].stop()
            process.kill()
        for process in processes:
            process.waitForFinished(500)
