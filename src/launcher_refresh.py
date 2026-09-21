"""通知 deepin 重读应用目录，清除自启动文件留下的启动器缓存。"""

from PyQt5.QtDBus import QDBusConnection, QDBusMessage


def refresh_application_cache() -> None:
    """尽力异步刷新；不启动缺席的服务，不退出桌面或卸载任何应用。"""
    connection = QDBusConnection.sessionBus()
    if not connection.isConnected():
        return
    message = QDBusMessage.createMethodCall(
        "org.desktopspec.ApplicationManager1", "/org/desktopspec/ApplicationManager1",
        "org.desktopspec.ApplicationManager1", "ReloadApplications")
    message.setAutoStartService(False)
    connection.asyncCall(message, 1500)
