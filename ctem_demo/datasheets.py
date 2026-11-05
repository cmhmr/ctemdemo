"""Product datasheet viewer (plain-text spec sheets stored on disk)."""

import os

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
    base_dir = os.path.realpath(current_app.config["DATASHEET_DIR"])
    path = os.path.realpath(os.path.join(base_dir, filename))

    try:
        is_confined = os.path.commonpath((base_dir, path)) == base_dir
    except ValueError:
        is_confined = False

    if not filename or not is_confined or not os.path.isfile(path):
        abort(404)
    with open(path, encoding="utf-8", errors="replace") as handle:
        content = handle.read()
    return render_template("datasheet.html", product=product, filename=filename, content=content)
