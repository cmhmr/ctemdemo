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
    # TRAINING EXAMPLE: the "file" query parameter is joined to the datasheet
    # directory without normalization, so "../" sequences escape the folder.
    # Remediation: do not take paths from users; resolve and confine to base dir.
    # -----------------------------------------------------------------------
    filename = request.args.get("file", "")
    path = os.path.join(current_app.config["DATASHEET_DIR"], filename)

    if not filename or not os.path.isfile(path):
        abort(404)
    with open(path, encoding="utf-8", errors="replace") as handle:
        content = handle.read()
    return render_template("datasheet.html", product=product, filename=filename, content=content)
