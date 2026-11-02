"""SQLite persistence. The database is rebuilt and seeded at startup so every
demo run starts from the same deterministic state."""

import os
import sqlite3

from flask import Flask, current_app, g

from .passwords import hash_password

SCHEMA = """
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE products (
    id          INTEGER PRIMARY KEY,
    sku         TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    price       REAL NOT NULL,
    stock       INTEGER NOT NULL,
    description TEXT NOT NULL,
    datasheet   TEXT
);

CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL,
    role          TEXT NOT NULL,
    password_hash TEXT NOT NULL
);
"""

PRODUCTS = [
    ("NET-100", "Edge Router ER-100", "Networking", 349.00, 42,
     "Branch-office router with dual WAN uplinks.", "edge-router-er100.txt"),
    ("NET-210", "Managed Switch MS-24", "Networking", 529.00, 18,
     "24-port managed gigabit switch with VLAN support.", "managed-switch-ms24.txt"),
    ("SEC-300", "Badge Reader BR-3", "Physical Security", 189.50, 75,
     "Proximity badge reader for office doors.", "badge-reader-br3.txt"),
    ("SRV-400", "Rack Server RS-4", "Compute", 4299.00, 6,
     "2U rack server for internal workloads.", "rack-server-rs4.txt"),
    ("WKS-510", "Developer Laptop DL-5", "Endpoints", 1899.00, 23,
     "Standard developer laptop image, 32 GB RAM.", None),
    ("ACC-600", "USB-C Dock UD-6", "Accessories", 229.00, 120,
     "Docking station with dual display output.", None),
]

DEMO_USERS = [
    ("analyst", "Alex Analyst", "alex.analyst@example.test", "user"),
    ("admin", "Riley Admin", "riley.admin@example.test", "admin"),
]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(app: Flask) -> None:
    path = app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    # Lab-only shared password for the seeded demo accounts; override via env.
    demo_password = os.environ.get("CTEM_DEMO_PASSWORD", "ctem-demo")
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO products (sku, name, category, price, stock, description, datasheet) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            PRODUCTS,
        )
        conn.executemany(
            "INSERT INTO users (username, full_name, email, role, password_hash) VALUES (?, ?, ?, ?, ?)",
            [(u, n, e, r, hash_password(demo_password)) for (u, n, e, r) in DEMO_USERS],
        )


def init_app(app: Flask) -> None:
    init_db(app)
    app.teardown_appcontext(close_db)
