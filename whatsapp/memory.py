import json
import sqlite3
from pathlib import Path

DB_PATH = Path("chat_memory.db")

def init_memory_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            user_id TEXT PRIMARY KEY,
            history TEXT
        )
        """)
        conn.commit()

def load_memory(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT history FROM memory WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            return json.loads(row[0])
    return []

def save_memory(user_id, messages):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "REPLACE INTO memory (user_id, history) VALUES (?, ?)",
            (user_id, json.dumps(messages[-20:])),
        )
        conn.commit()
