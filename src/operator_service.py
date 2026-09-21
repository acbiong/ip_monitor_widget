"""运营商异步调度：按公网 IP 去重缓存，有界并发及快速退出。"""

from __future__ import annotations

from collections import OrderedDict
import json
from pathlib import Path
import sys
import time

from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal

from operator_lookup import canonical_public_ip, chinese_operator


class OperatorService(QObject):
    """仅查询已确认的公网地址；元数据与网卡公网连通性互不替代。"""

    result = pyqtSignal()
    MAX_PROCESSES = 2
    MAX_CACHE = 128
    TIMEOUT_MS = 8000
    SUCCESS_TTL = 3600
    FAILURE_TTL = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cache = OrderedDict()
        self._wanted = set()
        self._pending = []
        self._active = {}
        self._stopped = False

    def get(self, address: str) -> dict:
        """缓存只按规范化公网地址读取；刷新过程中不借用旧地址的结果。"""
        entry = self._cache.get(canonical_public_ip(address))
        return entry[1] if entry else {"name": "查询中…", "holder": "", "asns": []}

    def request(self, addresses) -> None:
        """替换当前关心的地址集合，同 IP 多网卡只发一次请求。"""
        if self._stopped:
            return
        self._wanted = {parsed for address in addresses if (parsed := canonical_public_ip(address))}
        active_addresses = set()
        for process, job in list(self._active.items()):
            if job["address"] not in self._wanted:
                self._abort(process)
            else:
                active_addresses.add(job["address"])
        now = time.monotonic()
        self._pending = sorted(address for address in self._wanted - active_addresses
                               if address not in self._cache or self._cache[address][0] <= now)
        self._launch()

    def _launch(self):
        while not self._stopped and self._pending and len(self._active) < self.MAX_PROCESSES:
            address = self._pending.pop(0)
            process = QProcess(self)
            timer = QTimer(process)
            timer.setSingleShot(True)
            self._active[process] = {"address": address, "timer": timer,
                                     "output": bytearray(), "aborted": False}
            process.readyReadStandardOutput.connect(lambda proc=process: self._read(proc))
            process.readyReadStandardError.connect(lambda proc=process: proc.readAllStandardError())
            process.finished.connect(lambda code, status, proc=process:
                                     self._finish(proc, code if status == QProcess.NormalExit else -1))
            process.errorOccurred.connect(lambda error, proc=process:
                                          self._finish(proc, -1) if error == QProcess.FailedToStart else None)
            timer.timeout.connect(lambda proc=process: self._abort(proc))
            arguments = (["--operator-lookup"] if getattr(sys, "frozen", False)
                         else [str(Path(__file__).with_name("operator_lookup.py"))])
            timer.start(self.TIMEOUT_MS)
            process.start(sys.executable, arguments)
            process.write(json.dumps({"address": address}).encode("utf-8"))
            process.closeWriteChannel()

    def _read(self, process):
        job = self._active.get(process)
        if job is not None:
            job["output"].extend(bytes(process.readAllStandardOutput()))
            if len(job["output"]) > 8192:
                self._abort(process)

    def _abort(self, process):
        job = self._active.get(process)
        if job is not None:
            job["aborted"] = True
            process.kill()

    def _finish(self, process, exit_code):
        """拒绝错误地址及异常协议，失效任务不污染当前结果。"""
        self._read(process)
        job = self._active.pop(process, None)
        if job is None:
            return
        job["timer"].stop()
        process.deleteLater()
        address = job["address"]
        if not self._stopped and address in self._wanted:
            result = {"address": address, "status": "failed", "name": "暂未识别",
                      "holder": "", "asns": []}
            if exit_code == 0 and not job["aborted"]:
                try:
                    candidate = json.loads(job["output"])
                    holder, asns = candidate["holder"], candidate["asns"]
                    if (candidate["address"] == address and candidate["status"] == "ok"
                            and isinstance(holder, str) and len(holder) <= 512
                            and isinstance(asns, list) and 1 <= len(asns) <= 32
                            and all(type(number) is int and 1 <= number <= 4294967295 for number in asns)
                            and (holder.strip() or len(set(asns)) > 1)):
                        result.update(status="ok", holder=holder, asns=asns,
                                      name=("多运营商（归属不唯一）" if len(set(asns)) > 1
                                            else chinese_operator(holder)))
                except (ValueError, TypeError, KeyError):
                    pass
            ttl = self.SUCCESS_TTL if result["status"] == "ok" else self.FAILURE_TTL
            self._cache[address] = (time.monotonic() + ttl, result)
            self._cache.move_to_end(address)
            while len(self._cache) > self.MAX_CACHE:
                self._cache.popitem(last=False)
            self.result.emit()
        self._launch()

    def shutdown(self):
        """先同时终止所有进程，不等待网络超时。"""
        self._stopped = True
        self._pending.clear()
        processes = list(self._active)
        for process in processes:
            self._active[process]["timer"].stop()
            self._abort(process)
        for process in processes:
            process.waitForFinished(200)
