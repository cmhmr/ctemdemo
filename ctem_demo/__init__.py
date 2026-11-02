"""CTEM Demo Store - a small Flask inventory portal used for CTEM / AppSec demos.

TRAINING / LAB USE ONLY. This package intentionally contains insecure patterns
(tagged with "CTEM-<CATEGORY>-<NN>" comments) so that security scanners such as
Checkmarx One can discover them. See docs/security-scenarios.md.
"""

import logging
import secrets

from flask import Flask, abort, render_template, request, session

from ..AVAL.ctem_demo import admin, auth, catalog, datasheets, db
from .config import load_config


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(load_config())
    if overrides:
        app.config.update(overrides)

    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    db.init_app(app)
    app.register_blueprint(catalog.bp)
    app.register_blueprint(datasheets.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    _register_csrf(app)
    _register_error_handlers(app)

    @app.context_processor
    def inject_globals():
        return {
            "app_name": app.config["APP_NAME"],
            "app_version": app.config["APP_VERSION"],
            "current_user": auth.current_user(),
        }

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

    return app


def _register_csrf(app: Flask) -> None:
    """Minimal synchronizer-token CSRF protection for HTML forms."""

    def csrf_token() -> str:
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_urlsafe(32)
        return session["_csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def check_csrf():
        if app.config.get("CSRF_DISABLED"):
            return
        if request.method == "POST":
            sent = request.form.get("_csrf", "")
            expected = session.get("_csrf", "")
            if not expected or not secrets.compare_digest(sent, expected):
                abort(400)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(_err):
        return render_template("error.html", code=400, message="Bad request."), 400

    @app.errorhandler(403)
    def forbidden(_err):
        return render_template("error.html", code=403, message="You do not have access to this page."), 403

    @app.errorhandler(404)
    def not_found(_err):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(500)
    def server_error(_err):
        return render_template("error.html", code=500, message="Unexpected error."), 500
