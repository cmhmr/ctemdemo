"""Product catalog: listing, search, details and stock reorder."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .auth import login_required
from .db import get_db

bp = Blueprint("catalog", __name__)


@bp.get("/")
def index():
    db = get_db()
    stats = db.execute(
        "SELECT COUNT(*) AS products, SUM(stock) AS units, COUNT(DISTINCT category) AS categories FROM products"
    ).fetchone()
    return render_template("index.html", stats=stats)


@bp.get("/products")
def product_list():
    products = get_db().execute(
        "SELECT id, sku, name, category, price, stock FROM products ORDER BY category, name"
    ).fetchall()
    return render_template("products.html", products=products)


@bp.get("/products/search")
def search():
    term = request.args.get("q", "").strip()
    results = []
    if term:
        # CTEM-SAST-01 remediated: parameterized query; input is bound, never concatenated.
        pattern = f"%{term[:100]}%"
        results = get_db().execute(
            "SELECT id, sku, name, category, price FROM products "
            "WHERE name LIKE ? OR category LIKE ? ORDER BY name",
            (pattern, pattern),
        ).fetchall()
    return render_template("search.html", term=term, results=results)


@bp.get("/products/<int:product_id>")
def product_detail(product_id: int):
    product = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        abort(404)
    return render_template("product.html", product=product)


@bp.post("/products/<int:product_id>/reorder")
@login_required
def reorder(product_id: int):
    db = get_db()
    if db.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone() is None:
        abort(404)

    # -----------------------------------------------------------------------
    # CTEM-SAST-05 | CWE-20 / CWE-1284 | Insufficient input validation
    # TRAINING EXAMPLE: the quantity is trusted as-is. Negative or huge values
    # corrupt inventory, and non-numeric values raise an unhandled error.
    # Remediation: validate type and enforce an allowed range server-side.
    # -----------------------------------------------------------------------
    quantity = int(request.form.get("quantity", "0"))

    db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
    db.commit()
    flash(f"Reorder of {quantity} unit(s) recorded.", "success")
    return redirect(url_for("catalog.product_detail", product_id=product_id))
