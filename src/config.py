"""应用常量与默认配置。

本模块只保存静态配置，不执行系统调用，也不依赖 Qt 窗体，便于其他模块复用和测试。
"""

from pathlib import Path


APP_NAME = "本机状态监视器"
ORG_NAME = "Biong"
APP_ID = "IPMonitorWidget"
ICON_PATH = Path(__file__).resolve().parent / "resources" / "icon.svg"

# 按固定顺序尝试 HTTPS 服务；各服务实时可用性由实际请求结果决定。
PUBLIC_IP_ENDPOINTS = (
    "https://api.ipify.org",
    "https://api64.ipify.org",
    "https://ifconfig.me/ip",
    "https://icanhazip.com",
    "https://checkip.amazonaws.com",
)
PUBLIC_IP_LOOKUP_SECONDS = 2.5
PUBLIC_IP_CONNECT_SECONDS = 0.6
PUBLIC_IP_READ_SECONDS = 1.0
PUBLIC_IP_PROCESS_TIMEOUT_MS = 6000
PUBLIC_IP_REFRESH_MS = 60_000
PUBLIC_IP_MAX_PROCESSES = 4
PUBLIC_IP_RETRY_MS = 3000
PUBLIC_IP_MAX_RETRIES = 2

# 这些值会保存到 QSettings；新增配置时需要同步更新接口文档。
DEFAULT_SETTINGS = {
    "font_size": 16,
    "opacity": 0.50,
    "interval": 1000,
    "locked": False,
}
