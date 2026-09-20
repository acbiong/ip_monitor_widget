"""默认出口回归：全部写操作使用模拟对象，绝不修改真实路由。"""

import asyncio
import copy
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dbus_next import Variant
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMenu

from route_menu import RouteMenu
from route_switch_worker import NetworkManagerClient, changed_settings, switch_plan, unpack, run
from route_switch_worker import read_kernel_routes


def route(name, metric):
    return {"dst": "default", "dev": name, "metric": metric}


def settings(uuid="ethernet"):
    return {"connection": {"uuid": Variant("s", uuid)},
            "ipv4": {"route-metric": Variant("x", -1), "method": Variant("s", "auto")},
            "ipv6": {"route-metric": Variant("x", -1), "method": Variant("s", "auto")}}


def choice(name, defaults=None, enabled=True):
    return {"name": name, "uuid": name, "ips": ["192.0.2.10"], "families": ["ipv4"],
            "default_for": defaults or [], "enabled": enabled, "reason": "" if enabled else "无默认路由"}


class PlanTests(unittest.TestCase):
    def test_lower_target_only(self):
        plan, families = switch_plan({"ipv4": [route("wifi", 100), route("ethernet", 600)]}, "ethernet")
        self.assertEqual(plan, {"ethernet": {"ipv4": 1}})
        self.assertEqual(families, ["ipv4"])

    def test_competing_zero_and_one(self):
        plan, unused = switch_plan({"ipv4": [route("wifi", 0), route("vpn", 1), route("ethernet", 600)]}, "ethernet")
        self.assertEqual(plan, {"ethernet": {"ipv4": 1}, "wifi": {"ipv4": 100}, "vpn": {"ipv4": 100}})

    def test_current_noop(self):
        self.assertEqual(switch_plan({"ipv4": [route("wifi", 100)]}, "wifi"), ({}, ["ipv4"]))

    def test_ipv6_unchanged_if_target_has_no_route(self):
        plan, families = switch_plan({"ipv4": [route("wifi", 100), route("ethernet", 600)],
                                      "ipv6": [route("wifi", 100)]}, "ethernet")
        self.assertEqual(families, ["ipv4"])
        self.assertNotIn("ipv6", plan["ethernet"])

    def test_dual_stack(self):
        routes = {family: [route("wifi", 100), route("ethernet", 600)] for family in ("ipv4", "ipv6")}
        self.assertEqual(switch_plan(routes, "ethernet")[0], {"ethernet": {"ipv4": 1, "ipv6": 1}})

    def test_missing_gateway(self):
        with self.assertRaises(ValueError):
            switch_plan({"ipv4": [route("wifi", 100)]}, "vmnet1")

    def test_linkdown(self):
        with self.assertRaises(ValueError):
            switch_plan({"ipv4": [{**route("ethernet", 100), "flags": ["linkdown"]}]}, "ethernet")

    def test_settings_not_mutated(self):
        original = settings()
        snapshot = copy.deepcopy(original)
        updated = changed_settings(original, {"ipv4": 1})
        self.assertEqual(original, snapshot)
        self.assertEqual(unpack(updated)["ipv4"]["route-metric"], 1)
        self.assertEqual(updated["ipv6"], original["ipv6"])

    def test_static_default_route(self):
        original = settings()
        original["ipv4"]["route-data"] = Variant("aa{sv}", [
            {"dest": Variant("s", "0.0.0.0"), "prefix": Variant("u", 0), "metric": Variant("u", 900)},
            {"dest": Variant("s", "192.0.2.0"), "prefix": Variant("u", 24), "metric": Variant("u", 500)}])
        original["ipv4"]["routes"] = Variant("aau", [])
        updated = unpack(changed_settings(original, {"ipv4": 1}))["ipv4"]
        self.assertEqual(updated["route-data"][0]["metric"], 1)
        self.assertEqual(updated["route-data"][1]["metric"], 500)
        self.assertNotIn("routes", updated)

    def test_refuse_policy_and_never_default(self):
        for key, value in [("never-default", Variant("b", True)), ("route-table", Variant("u", 100)),
                           ("routing-rules", Variant("aa{sv}", [{"priority": Variant("u", 100)}]))]:
            with self.subTest(key=key):
                original = settings()
                original["ipv4"][key] = value
                with self.assertRaises(ValueError):
                    changed_settings(original, {"ipv4": 1})

    def test_rule_guard(self):
        responses = [
            '[{"dst":"default","dev":"wifi"}]',
            '[{"priority":0,"src":"all","table":"local"},'
            '{"priority":100,"src":"all","table":100}]',
            '[]', '[{"priority":32766,"src":"all","table":"main"}]']
        with patch("route_switch_worker.subprocess.run") as command:
            from types import SimpleNamespace
            command.side_effect = [SimpleNamespace(stdout=text) for text in responses]
            self.assertFalse(read_kernel_routes()[1])

    def test_explicit_non_main_table_is_rejected(self):
        original = settings()
        original["ipv4"]["route-data"] = Variant("aa{sv}", [
            {"prefix": Variant("u", 0), "table": Variant("u", 100)}])
        with self.assertRaises(ValueError):
            changed_settings(original, {"ipv4": 1})


class FakeClient(NetworkManagerClient):
    def __init__(self, failure="", verified=True, enabled=True):
        self.failure = failure
        self.verified = verified
        self.calls = []
        self.applied = False
        self.data = {"ok": True, "choices": [choice("wifi", ["ipv4"]), choice("ethernet", enabled=enabled)],
                     "current": {"ipv4": ["wifi"], "ipv6": []}}
        self.routes = {"ipv4": [route("wifi", 100), route("ethernet", 600)], "ipv6": []}

    async def snapshot(self):
        snapshot = copy.deepcopy(self.data)
        if self.applied and self.verified:
            snapshot["current"]["ipv4"] = ["ethernet"]
        devices = {name: {"path": "/" + name, "uuid": name} for name in ("wifi", "ethernet")}
        return snapshot, devices, self.routes

    async def call(self, path, interface, member, signature="", body=None, authorize=False):
        self.calls.append((member, body, authorize))
        if member == self.failure:
            raise RuntimeError("模拟拒绝或断开")
        if member == "GetAppliedConnection":
            return [settings(path[1:]), 5]
        if member == "CheckpointCreate":
            return ["/checkpoint/1"]
        if member == "Reapply":
            self.applied = True
        if member == "CheckpointRollback":
            return [{"/ethernet": 0}]
        return []


class TransactionTests(unittest.IsolatedAsyncioTestCase):
    async def test_success(self):
        client = FakeClient()
        result = await client.switch("ethernet", "ethernet")
        self.assertTrue(result["ok"])
        self.assertEqual([member for member, body, auth in client.calls],
                         ["GetAppliedConnection", "CheckpointCreate", "Reapply", "CheckpointDestroy"])
        self.assertEqual(client.calls[2][1][2], 1)
        self.assertEqual(client.calls[1][1][1], 90)

    async def test_denied_checkpoint_does_not_modify(self):
        client = FakeClient(failure="CheckpointCreate")
        with self.assertRaises(RuntimeError):
            await client.switch("ethernet", "ethernet")
        self.assertFalse(client.applied)

    async def test_denied_reapply_rolls_back(self):
        client = FakeClient(failure="Reapply")
        with self.assertRaisesRegex(RuntimeError, "已回滚"):
            await client.switch("ethernet", "ethernet")
        self.assertEqual(client.calls[-1][0], "CheckpointRollback")

    async def test_verification_failure_rolls_back(self):
        client = FakeClient(verified=False)
        with patch("route_switch_worker.asyncio.sleep", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "已回滚"):
                await client.switch("ethernet", "ethernet")
        self.assertEqual(client.calls[-1][0], "CheckpointRollback")

    async def test_rollback_failure_is_not_hidden(self):
        client = FakeClient(failure="CheckpointRollback", verified=False)
        with patch("route_switch_worker.asyncio.sleep", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "回滚未确认"):
                await client.switch("ethernet", "ethernet")

    async def test_connection_replaced(self):
        client = FakeClient()
        with self.assertRaises(ValueError):
            await client.switch("ethernet", "old-uuid")
        self.assertEqual(client.calls, [])

    async def test_disconnected(self):
        client = FakeClient()
        with self.assertRaises(ValueError):
            await client.switch("missing", "missing")
        self.assertEqual(client.calls, [])

    async def test_disabled(self):
        client = FakeClient(enabled=False)
        with self.assertRaises(ValueError):
            await client.switch("ethernet", "ethernet")
        self.assertEqual(client.calls, [])

    async def test_noop_no_auth_or_checkpoint(self):
        client = FakeClient()
        result = await client.switch("wifi", "wifi")
        self.assertTrue(result["ok"])
        self.assertEqual(client.calls, [])

    async def test_invalid_request_never_connects(self):
        with self.assertRaises(ValueError):
            await run({"action": "shell"})

    async def test_cancel_during_reapply_rolls_back(self):
        client = FakeClient()
        original_call = client.call

        async def cancel_reapply(path, interface, member, *arguments):
            if member == "Reapply":
                raise asyncio.CancelledError()
            return await original_call(path, interface, member, *arguments)

        client.call = cancel_reapply
        with self.assertRaisesRegex(RuntimeError, "已回滚"):
            await client.switch("ethernet", "ethernet")
        self.assertEqual(client.calls[-1][0], "CheckpointRollback")

    async def test_connection_changed_before_reapply(self):
        client = FakeClient()
        original_call = client.call

        async def changed_connection(path, interface, member, *arguments):
            if member == "GetAppliedConnection":
                return [settings("replacement"), 6]
            return await original_call(path, interface, member, *arguments)

        client.call = changed_connection
        with self.assertRaises(ValueError):
            await client.switch("ethernet", "ethernet")
        self.assertEqual(client.calls, [])


class FakeService(QObject):
    result = pyqtSignal(object)
    finished = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.switching = False
        self.requests = []

    def refresh(self):
        pass

    def switch(self, name, uuid):
        self.requests.append((name, uuid))
        self.switching = True
        return True

    def shutdown(self):
        pass


class MenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.parent = QMenu()
        self.service = FakeService()
        self.menu = RouteMenu(self.parent, None, None, service=self.service)

    def tearDown(self):
        self.menu.shutdown()
        self.parent.deleteLater()
        self.app.processEvents()

    def test_actual_checks_and_disabled_virtual(self):
        self.service.result.emit({"ok": True, "choices": [choice("wifi", ["ipv4"]),
                                 choice("ethernet"), choice("vmnet1", enabled=False)]})
        actions = self.menu.menu.actions()
        self.assertEqual([action.isChecked() for action in actions], [True, False, False])
        self.assertFalse(actions[2].isEnabled())
        actions[1].trigger()
        self.assertEqual(self.service.requests, [("ethernet", "ethernet")])
        self.assertFalse(actions[1].isChecked())

    def test_split_ipv4_ipv6_checks(self):
        self.service.result.emit({"ok": True, "choices": [choice("wifi", ["ipv4"]), choice("ethernet", ["ipv6"])]})
        self.assertTrue(all(action.isChecked() for action in self.menu.menu.actions()))

    def test_removed_adapter_disappears(self):
        self.service.result.emit({"ok": True, "choices": [choice("wifi"), choice("ethernet")]})
        self.service.result.emit({"ok": True, "choices": [choice("wifi")]})
        self.assertEqual(len(self.menu.menu.actions()), 1)

    def test_error_disables_menu(self):
        self.service.result.emit({"ok": False, "message": "NetworkManager 不可用"})
        self.assertFalse(self.menu.menu.actions()[0].isEnabled())


if __name__ == "__main__":
    unittest.main(verbosity=2)
