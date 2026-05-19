import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "data/manager.db")

def init_db():
    queries = [
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, approved INTEGER DEFAULT 0)",
        "CREATE TABLE IF NOT EXISTS accounts (user_id INTEGER, name TEXT, access_key TEXT, secret_key TEXT, project_id TEXT, PRIMARY KEY(user_id, name))",
        "CREATE TABLE IF NOT EXISTS templates (user_id INTEGER, name TEXT, content TEXT, PRIMARY KEY(user_id, name))"
    ]
    for q in queries:
        db_query(q)

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(query, params)
        res = c.fetchall() if fetch else None
        conn.commit()
        return res
    finally:
        conn.close()