"""公网查询调度：Qt 异步子进程、有界并发、超时终止和过期结果隔离。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal

from config import (
    PUBLIC_IP_MAX_PROCESSES,
    PUBLIC_IP_MAX_RETRIES,
    PUBLIC_IP_PROCESS_TIMEOUT_MS,
    PUBLIC_IP_RETRY_MS,
)
from public_ip_lookup import parse_public_ip
from utils import network_signature


class PublicIPService(QObject):
    """每次 request 对应独立代次；结果信号在 GUI 线程发出。"""

    result = pyqtSignal(object, object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._generation = 0
        self._signature = ()
        self._pending = []
        self._active = {}
        self._results = {}
        self._interfaces = []
        self._retry_count = 0
        self._retry_timer = QTimer(self)
        self._retry_timer.setSingleShot(True)
        self._retry_timer.timeout.connect(self._retry_failed)
        self._stopped = False

    def request(self, interfaces: list[dict]) -> None:
        """新快照替换旧批次；同一快照仍有任务时不重复排队。"""
        if self._stopped:
            return
        signature = network_signature(interfaces)
        if signature == self._signature and (
                self._active or self._pending or self._retry_timer.isActive()):
            return
        self._retry_timer.stop()
        self._generation += 1
        self._signature = signature
        self._interfaces = [{"name": item["name"], "ips": list(item["ips"])}
                            for item in interfaces]
        self._pending = list(self._interfaces)
        self._results = {}
        self._retry_count = 0
        for process, job in list(self._active.items()):
            job["timer"].stop()
            process.kill()
        if not interfaces:
            self.result.emit(signature, {})
        self._launch_pending()

    def _launch_pending(self) -> None:
        """仅保留最多四个进程，排队网卡在旧进程释放后启动。"""
        while not self._stopped and self._pending and len(self._active) < PUBLIC_IP_MAX_PROCESSES:
            interface = self._pending.pop(0)
            process = QProcess(self)
            timer = QTimer(process)
            timer.setSingleShot(True)
            self._active[process] = {
                "generation": self._generation, "name": interface["name"],
                "timer": timer, "output": bytearray(), "timed_out": False,
            }
            process.readyReadStandardOutput.connect(lambda proc=process: self._read_output(proc))
            process.readyReadStandardError.connect(lambda proc=process: proc.readAllStandardError())
            process.finished.connect(
                lambda code, status, proc=process:
                self._finish(proc, code if status == QProcess.NormalExit else -1)
            )
            process.errorOccurred.connect(lambda error, proc=process: self._error(proc, error))
            timer.timeout.connect(lambda proc=process: self._timeout(proc))
            arguments = (["--public-ip-lookup"] if getattr(sys, "frozen", False)
                         else [str(Path(__file__).with_name("public_ip_lookup.py"))])
            process.start(sys.executable, arguments)
            process.write(json.dumps({**interface, "attempt": self._retry_count}).encode("utf-8"))
            process.closeWriteChannel()
            timer.start(PUBLIC_IP_PROCESS_TIMEOUT_MS)
        if (not self._stopped and not self._active and not self._pending
                and self._retry_count < PUBLIC_IP_MAX_RETRIES
                and any(item["status"] == "failed" for item in self._results.values())
                and not self._retry_timer.isActive()):
            self._retry_timer.start(PUBLIC_IP_RETRY_MS)

    def _retry_failed(self) -> None:
        """只重试未取得公网地址的网卡，不查询默认出口或借用其他网卡结果。"""
        if self._stopped:
            return
        failed = [item for item in self._interfaces
                  if self._results.get(item["name"], {}).get("status") == "failed"]
        if not failed:
            return
        self._retry_count += 1
        self._pending = failed
        self._launch_pending()

    def _read_output(self, process: QProcess) -> None:
        job = self._active.get(process)
        if job is None:
            return
        job["output"].extend(bytes(process.readAllStandardOutput()))
        if len(job["output"]) > 16384:
            self._timeout(process)

    def _timeout(self, process: QProcess) -> None:
        job = self._active.get(process)
        if job is not None:
            job["timed_out"] = True
            process.kill()

    def _error(self, process: QProcess, error) -> None:
        if error == QProcess.FailedToStart:
            self._finish(process, -1)

    def _finish(self, process: QProcess, exit_code: int) -> None:
        """先回收资源，再提交当前代次结果；旧进程结束不得覆盖新 IP。"""
        self._read_output(process)
        job = self._active.pop(process, None)
        if job is None:
            return
        job["timer"].stop()
        process.deleteLater()
        if not self._stopped and job["generation"] == self._generation:
            result = {"status": "failed", "addresses": []}
            if exit_code == 0 and not job["timed_out"]:
                try:
                    candidate = json.loads(job["output"])
                    status = candidate["status"]
                    addresses = candidate["addresses"]
                    if (status == "ok" and isinstance(addresses, list)
                            and addresses and all(isinstance(address, str) and parse_public_ip(address)
                                                  for address in addresses)):
                        result = {"status": status, "addresses": list(dict.fromkeys(addresses))}
                except (ValueError, TypeError, KeyError):
                    pass
            self._results[job["name"]] = result
            self.result.emit(self._signature, dict(self._results))
        self._launch_pending()

    def shutdown(self) -> None:
        """停止接单并终止子进程，不再等待阻塞 DNS/HTTP 的 Python 线程。"""
        self._stopped = True
        self._retry_timer.stop()
        self._pending.clear()
        processes = list(self._active)
        for process in processes:
            self._active[process]["timer"].stop()
            process.kill()
        for process in processes:
            process.waitForFinished(500)
