"""SQLite bilan ishlash: ulanish, jadvallarni yaratish, xonalarni qo'shish."""
import sqlite3

from flask import current_app, g

ROOMS = [
    ("Katta zal", 20),
    ("Kichik xona", 6),
    ("Kabinet", 4),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL UNIQUE,
    capacity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id    INTEGER NOT NULL REFERENCES rooms(id),
    name       TEXT NOT NULL,
    people     INTEGER NOT NULL,
    date       TEXT NOT NULL,  -- YYYY-MM-DD
    start_time TEXT NOT NULL,  -- HH:MM
    end_time   TEXT NOT NULL,  -- HH:MM
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bookings_room_date ON bookings(room_id, date);
"""


def get_db():
    """Joriy so'rov uchun bitta ulanish (g ichida saqlanadi)."""
    if "db" not in g:
        # isolation_level=None: tranzaksiyalarni o'zimiz BEGIN/COMMIT bilan boshqaramiz
        g.db = sqlite3.connect(current_app.config["DATABASE"], isolation_level=None)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    """Jadvallarni yaratadi va xonalarni qo'shadi. Qayta chaqirilsa ham xavfsiz."""
    conn = sqlite3.connect(path)
    with conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT OR IGNORE INTO rooms (name, capacity) VALUES (?, ?)", ROOMS
        )
    conn.close()
