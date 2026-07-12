import json
import os
import secrets
import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent.parent / "plans.db")


def _connect():
    conn = sqlite3.connect(os.getenv("PLANS_DB", DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS saved_plans ("
        "id TEXT PRIMARY KEY, "
        "created_at TEXT DEFAULT CURRENT_TIMESTAMP, "
        "data TEXT NOT NULL)"
    )
    return conn


def save_plan(payload: dict) -> str:
    plan_id = secrets.token_hex(8)
    conn = _connect()
    try:
        with conn:
            conn.execute(
                "INSERT INTO saved_plans (id, data) VALUES (?, ?)",
                (plan_id, json.dumps(payload)),
            )
    finally:
        conn.close()
    return plan_id


def get_plan(plan_id: str):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT data FROM saved_plans WHERE id = ?", (plan_id,)
        ).fetchone()
    finally:
        conn.close()
    return json.loads(row[0]) if row else None
