import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "patient_data.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        skin_type TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diagnosis(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        disease TEXT,
        confidence REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        severity INTEGER,
        adherence INTEGER,
        notes TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()