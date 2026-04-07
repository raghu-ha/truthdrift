"""
TruthDrift - DuckDB Store
Stores and retrieves snapshots from a local DuckDB database.
"""

import duckdb
import json
from pathlib import Path

DB_PATH = "truthdrift.db"


def get_connection():
    return duckdb.connect(DB_PATH)


def init_db():
    """Create the snapshots table if it doesn't exist."""
    con = get_connection()
    con.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id          INTEGER PRIMARY KEY,
            filepath    VARCHAR,
            filename    VARCHAR,
            captured_at VARCHAR,
            content_hash VARCHAR,
            word_count  INTEGER,
            line_count  INTEGER,
            char_count  INTEGER,
            backlink_count INTEGER,
            backlinks   VARCHAR
        )
    """)
    con.execute("""
        CREATE SEQUENCE IF NOT EXISTS snapshots_id_seq START 1
    """)
    con.close()
    print("✅ TruthDrift DB initialised")


def save_snapshot(snapshot: dict):
    """Save a snapshot to DuckDB."""
    con = get_connection()
    con.execute("""
        INSERT INTO snapshots VALUES (
            nextval('snapshots_id_seq'),
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, [
        snapshot["filepath"],
        snapshot["filename"],
        snapshot["captured_at"],
        snapshot["content_hash"],
        snapshot["word_count"],
        snapshot["line_count"],
        snapshot["char_count"],
        snapshot["backlink_count"],
        json.dumps(snapshot["backlinks"])
    ])
    con.close()
    print(f"✅ Snapshot saved → {snapshot['filename']} @ {snapshot['captured_at']}")


def get_latest_snapshot(filepath: str):
    """Get the most recent snapshot for a given file."""
    con = get_connection()
    result = con.execute("""
        SELECT * FROM snapshots
        WHERE filepath = ?
        ORDER BY captured_at DESC
        LIMIT 1
    """, [filepath]).fetchone()
    con.close()
    return result


def list_all_snapshots():
    """List all snapshots in the DB."""
    con = get_connection()
    result = con.execute("""
        SELECT filename, captured_at, content_hash, word_count
        FROM snapshots
        ORDER BY captured_at DESC
    """).fetchall()
    con.close()
    return result


if __name__ == "__main__":
    init_db()
    snaps = list_all_snapshots()
    if snaps:
        print("\n📋 All snapshots:")
        for s in snaps:
            print(f"  {s[0]} | {s[1]} | words: {s[3]}")
    else:
        print("No snapshots yet. Run snapshot.py first.")
