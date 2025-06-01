import sqlite3
from pathlib import Path

DB_PATH = Path("db/base_stock.sqlite")

def log_action(action, message, utilisateur="systeme"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO journal_actions (action, message, utilisateur)
        VALUES (?, ?, ?)
    """, (action, message, utilisateur))
    conn.commit()
    conn.close()