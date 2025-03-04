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

# Функция для создания таблиц (обновленная)
def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS support_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'  -- Добавляем поле для статуса чата
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

def log_error(message):
    # Здесь можно настроить сохранение ошибки в лог файл или базу данных
    logging.error(f"Ошибка: {message}")

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
    return value

def save_support_message(user_id, message):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO support_messages (user_id, message) VALUES (?, ?)', (user_id, message))
    conn.commit()
    conn.close()

def get_support_message_by_id(message_id):
    conn = create_connection()
    if conn is None:
        logger.error("Failed to connect to the database")
        return None
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM support_messages WHERE id = ?', (message_id,))
        message = cursor.fetchone()
        if message:
            logger.info(f"Fetched support message {message_id}: {message}")
        else:
            logger.warning(f"Message with id {message_id} not found")
        return message
    except sqlite3.Error as e:
        logger.error(f"Error fetching support message by id: {e}")
    finally:
        conn.close()

def get_chat_history(user_id):
    conn = create_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM support_messages WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages

# Функция для получения сообщений (с фильтрацией по статусу)
def get_support_messages():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM support_messages WHERE status != 'closed'  -- Исключаем закрытые чаты
    ''')
    messages = cursor.fetchall()
    conn.close()
    return messages

# Функция для закрытия чата
def close_chat(message_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE support_messages
    SET status = 'closed'
    WHERE id = ?
    ''', (message_id,))
    conn.commit()
    conn.close()

def respond_to_support_message(message_id, response):
    conn = create_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute('UPDATE support_messages SET response = ? WHERE id = ?', (response, message_id))
    conn.commit()
    conn.close()

def clear_all_logs():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    conn.commit()
    conn.close()