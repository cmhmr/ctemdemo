"""Operational endpoints: health check and admin status page."""

import platform

from flask import Blueprint, current_app, jsonify, render_template

from .auth import admin_required
from .db import get_db
from .integrations import integration_status

bp = Blueprint("admin", __name__)


@bp.get("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
        db_ok = True
    except Exception:  # noqa: BLE001 - health endpoint must not raise
        db_ok = False
    status = "ok" if db_ok else "degraded"
    return jsonify(status=status, version=current_app.config["APP_VERSION"]), (200 if db_ok else 503)


@bp.get("/admin/status")
@admin_required
def status():
    db = get_db()
    info = {
        "Application": current_app.config["APP_NAME"],
        "Version": current_app.config["APP_VERSION"],
        "Environment": current_app.config["APP_ENV"],
        "Python": platform.python_version(),
        "Products": db.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        "Users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
    }
    return render_template("status.html", info=info, integration=integration_status())
