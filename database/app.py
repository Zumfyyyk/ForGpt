import sqlite3
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = 'crypto_bot.db'

def create_connection():
    """Создание соединения с базой данных SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Доступ к столбцам по названию
        return conn
    except sqlite3.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None

def create_tables():
    """Создание необходимых таблиц, если их нет."""
    try:
        with create_connection() as conn:
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
            logger.info("Таблицы успешно созданы или уже существуют.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблиц: {e}")

def log_message(level, message):
    """Запись лог-сообщения в базу данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('INSERT INTO logs (level, message) VALUES (?, ?)', (level, message))
            conn.commit()
            logger.info(f"Лог записан: [{level}] {message}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при записи лога: {e}")

def get_logs(limit=50):
    """Получение последних логов из базы данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return []
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении логов: {e}")
        return []

def save_setting(key, value):
    """Сохранение настройки в базе данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
            conn.commit()
            logger.info(f"Настройка сохранена: {key} = {value}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении настройки: {e}")

def get_setting(key):
    """Получение значения настройки по ключу."""
    try:
        with create_connection() as conn:
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row is None:
                logger.warning(f"Настройка с ключом '{key}' не найдена.")
            return row['value'] if row else None
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении настройки: {e}")
        return None
