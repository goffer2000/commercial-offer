# db.py
import sqlite3

def init_db():
    with sqlite3.connect("offers.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            object_name TEXT,
            address TEXT,
            total REAL,
            pdf_filename TEXT
        );
        """)
