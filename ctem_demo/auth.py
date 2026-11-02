"""Session-based login, logout and user profile."""

import functools
import logging

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from .db import get_db
from .passwords import verify_password

bp = Blueprint("auth", __name__)
log = logging.getLogger("ctem_demo.auth")


def current_user():
    if "user" not in g:
        user_id = session.get("user_id")
        g.user = (
            get_db().execute("SELECT id, username, full_name, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
            if user_id is not None
            else None
        )
    return g.user


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @functools.wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user()["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def _safe_next(target: str | None) -> str:
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("catalog.index")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # -------------------------------------------------------------------
        # CTEM-SAST-04 | CWE-532 | Sensitive information written to logs
        # TRAINING EXAMPLE: the plaintext password is logged. Anyone with log
        # access (SIEM, support, log shipping) can harvest credentials.
        # Remediation: never log secrets; log only the event and outcome.
        # -------------------------------------------------------------------
        log.info("Login attempt username=%s password=%s", username, password)

        row = get_db().execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if row is not None and verify_password(password, row["password_hash"]):
            session.clear()
            session["user_id"] = row["id"]
            flash("Signed in.", "success")
            return redirect(_safe_next(request.args.get("next")))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@bp.post("/logout")
def logout():
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("catalog.index"))


@bp.get("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user())
