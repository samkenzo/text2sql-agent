import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "shop.db"


def get_readonly_connection(path=DB_PATH):
    # LAYER 3 (the real wall): open the file in read-only mode.
    # PRAGMA query_only is a second lock on the same door.
    uri = f"{Path(path).resolve().as_uri()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.execute("PRAGMA query_only = ON")
    return conn


def get_schema(conn):
    """Return (schema text for the prompt, set of table names)."""
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return "\n\n".join(r[1] for r in rows), {r[0] for r in rows}


def run_query(conn, sql, max_rows=100, timeout_s=5):
    """Run SQL with a row cap and a time limit (stops runaway queries)."""
    deadline = time.monotonic() + timeout_s
    # SQLite calls this function every 10,000 steps; returning 1 aborts the query.
    conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10_000)
    try:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(max_rows)
    finally:
        conn.set_progress_handler(None, 0)
    return columns, rows