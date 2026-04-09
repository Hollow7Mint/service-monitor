import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

logger = logging.getLogger(__name__)
DB_PATH = Path("data.db")


def _schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         TEXT PRIMARY KEY,
            name       TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            role       TEXT NOT NULL DEFAULT 'user',
            active     INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS records (
            id         TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            owner_id   TEXT NOT NULL REFERENCES users(id),
            active     INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS tags (
            record_id TEXT NOT NULL REFERENCES records(id) ON DELETE CASCADE,
            tag       TEXT NOT NULL,
            PRIMARY KEY (record_id, tag)
        );
        CREATE INDEX IF NOT EXISTS idx_records_owner ON records(owner_id);
        CREATE INDEX IF NOT EXISTS idx_tags_record   ON tags(record_id);
    """)
    conn.commit()


@contextmanager
def get_conn(path: Path = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        _schema(conn)
        yield conn
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        logger.error("DB error: %s", exc)
        raise
    finally:
        conn.close()


def fetch_one(sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
    with get_conn() as c:
        return c.execute(sql, params).fetchone()


def fetch_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_conn() as c:
        return c.execute(sql, params).fetchall()


def execute(sql: str, params: tuple = ()) -> int:
    with get_conn() as c:
        return c.execute(sql, params).rowcount


def execute_many(sql: str, rows: list[tuple]) -> int:
    with get_conn() as c:
        return c.executemany(sql, rows).rowcount


def row_count(table: str) -> int:
    row = fetch_one(f"SELECT COUNT(*) AS n FROM {table}")
    return row["n"] if row else 0


def paginate(sql: str, params: tuple = (),
             page: int = 1, size: int = 20) -> dict[str, Any]:
    offset = (max(page, 1) - 1) * size
    rows   = fetch_all(sql + " LIMIT ? OFFSET ?", params + (size, offset))
    total  = fetch_one("SELECT COUNT(*) AS n FROM (" + sql + ")", params)
    n      = total["n"] if total else 0
    return {
        "page": page, "page_size": size, "total": n,
        "pages": (n + size - 1) // size,
        "items": [dict(r) for r in rows],
    }
