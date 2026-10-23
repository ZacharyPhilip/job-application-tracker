"""SQLite access using the standard library's sqlite3 module."""
import os
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    company      TEXT NOT NULL,
    role         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'wishlist'
                 CHECK (status IN ('wishlist', 'applied', 'interview', 'offer', 'rejected')),
    applied_date TEXT,          -- ISO format: YYYY-MM-DD
    url          TEXT,
    notes        TEXT
);
"""


def db_path() -> str:
    # Read on each call so tests can point the app at a temporary database.
    return os.getenv("TRACKER_DB", "tracker.db")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row  # rows can be converted to dicts
    return conn


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()