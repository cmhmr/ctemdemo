"""Runtime configuration loaded from environment variables.

No real secrets are required to run the demo locally. When a value is not
provided, a safe local default is used (for example, a random session key).
"""

import os
import secrets
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> dict:
    instance_dir = Path(os.environ.get("CTEM_INSTANCE_DIR", PROJECT_DIR / "instance"))
    return {
        "APP_NAME": "CTEM Demo Store",
        "APP_ENV": os.environ.get("CTEM_APP_ENV", "lab"),
        "APP_VERSION": os.environ.get("CTEM_APP_VERSION", "0.1.0-demo-vulnerable"),
        "SECRET_KEY": os.environ.get("CTEM_SECRET_KEY") or secrets.token_hex(32),
        "DATABASE_PATH": os.environ.get("CTEM_DATABASE_PATH", str(instance_dir / "ctem_demo.db")),
        "DATASHEET_DIR": os.environ.get("CTEM_DATASHEET_DIR", str(PACKAGE_DIR / "data" / "datasheets")),
        "LOG_LEVEL": os.environ.get("CTEM_LOG_LEVEL", "INFO"),
        "MAX_REORDER_QUANTITY": int(os.environ.get("CTEM_MAX_REORDER_QUANTITY", "500")),
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": _bool(os.environ.get("CTEM_SECURE_COOKIES"), False),
    }
