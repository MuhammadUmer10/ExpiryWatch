import sqlite3

def init_db():
    conn = sqlite3.connect("monitor.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT,
            alert_email TEXT,
            certificate_expiry TEXT
        )
    """)

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            expiry_date TEXT,
            alert_email TEXT
        )
    """)

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect("monitor.db")
