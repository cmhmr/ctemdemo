"""Product datasheet viewer (plain-text spec sheets stored on disk)."""

import os
import ntpath

from flask import Blueprint, abort, current_app, render_template, request

from .db import get_db

bp = Blueprint("datasheets", __name__)


@bp.get("/products/<int:product_id>/datasheet")
def view_datasheet(product_id: int):
    product = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        abort(404)

    # -----------------------------------------------------------------------
    # CTEM-SAST-02 | CWE-22 | Path traversal in datasheet viewer
    # Resolve the requested path and ensure it remains inside the datasheet
    # directory, including when a path traverses a symlink.
    # -----------------------------------------------------------------------
    filename = request.args.get("file", "")
    if not filename:
        abort(404)

    base_dir = os.path.realpath(current_app.config["DATASHEET_DIR"])

    # Reject absolute paths and any traversal attempts before resolving the user
    # supplied value against the datasheet directory.
    normalized = os.path.normpath(filename.replace("\\", "/")).replace("\\", "/")
    if (
        os.path.isabs(normalized)
        or ntpath.isabs(filename)
        or ntpath.splitdrive(filename)[0]
        or normalized in ("", ".", "..")
        or normalized.startswith("../")
        or "/../" in normalized
    ):
        abort(404)

    # Find the requested relative path under the trusted directory instead of
    # using untrusted input to construct a filesystem path.
    path = None
    for root, _, files in os.walk(base_dir):
        for entry in files:
            candidate = os.path.join(root, entry)
            relative = os.path.relpath(candidate, base_dir).replace(os.sep, "/")
            if relative == normalized:
                resolved = os.path.realpath(candidate)
                try:
                    is_confined = os.path.commonpath((base_dir, resolved)) == base_dir
                except ValueError:
                    is_confined = False
                if is_confined and os.path.isfile(resolved):
                    path = resolved
                break
        if path is not None:
            break

    if path is None:
        abort(404)
    with open(path, mode="r", encoding="utf-8", errors="replace") as handle:
        content = handle.read()
    return render_template("datasheet.html", product=product, filename=filename, content=content)
