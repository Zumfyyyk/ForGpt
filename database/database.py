import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_connection():
    try:
        conn = sqlite3.connect('crypto_bot.db')
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def create_tables():
    conn = create_connection()
    if conn is None:
        return
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS support_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def log_message(level, message):
    conn = create_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('INSERT INTO logs (level, message) VALUES (?, ?)', (level, message))
    conn.commit()
    conn.close()

def get_logs():
    conn = create_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC')
    logs = cursor.fetchall()
    conn.close()
    return logs

def save_setting(key, value):
    conn = create_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_setting(key):
    conn = create_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    value = cursor.fetchone()
    conn.close()
    return value[0] if value else None

def save_support_message(user_id, message):
    conn = create_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('INSERT INTO support_messages (user_id, message) VALUES (?, ?)', (user_id, message))
    conn.commit()
    conn.close()

def get_support_messages():
    conn = create_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM support_messages ORDER BY timestamp DESC')
    messages = cursor.fetchall()
    conn.close()
    return messages

def respond_to_support_message(message_id, response):
    conn = create_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('UPDATE support_messages SET response = ? WHERE id = ?', (response, message_id))
    conn.commit()
    conn.close()

def get_support_message_by_id(message_id):
    conn = create_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, message FROM support_messages WHERE id = ?', (message_id,))
    message = cursor.fetchone()
    conn.close()
    return message