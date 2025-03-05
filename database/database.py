import sqlite3
import logging
import telegram
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = 'crypto_bot.db'  # Убедимся, что имя базы данных одинаковое

def create_connection():
    """Создание соединения с базой данных SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
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

def update_status(user_id, status):
    """Обновление статуса пользователя в таблице поддержки."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE support_messages
                SET status = ?
                WHERE user_id = ? AND status = 'inactive'
            ''', (status, user_id))
            conn.commit()
            logger.info(f"Статус пользователя {user_id} обновлен на {status}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при обновлении статуса пользователя {user_id}: {e}")

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
            return row[0] if row else None  # Исправление: возвращаем первый элемент кортежа
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении настройки: {e}")
        return None

def save_support_message(user_id, message):
    """Сохранение сообщения поддержки в базу данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('INSERT INTO support_messages (user_id, message) VALUES (?, ?)', (user_id, message))
            conn.commit()
            logger.info(f"Сообщение поддержки сохранено для пользователя {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении сообщения поддержки: {e}")

def get_support_message_by_id(message_id):
    """Получение сообщения поддержки по ID."""
    try:
        with create_connection() as conn:
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM support_messages WHERE id = ?', (message_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении сообщения поддержки: {e}")
        return None

def get_support_messages():
    """Получение всех сообщений поддержки из базы данных."""
    try:
        with create_connection() as conn:
            if conn is None:
                return []
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM support_messages ORDER BY timestamp DESC')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении сообщений поддержки: {e}")
        return []

def respond_to_support_message(message_id, response):
    """Отправка ответа на сообщение поддержки."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('UPDATE support_messages SET response = ? WHERE id = ?', (response, message_id))
            conn.commit()
            logger.info(f"Ответ на сообщение {message_id} сохранен.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении ответа на сообщение {message_id}: {e}")

def clear_all_support_messages():
    """Очистка всех сообщений поддержки."""
    try:
        with create_connection() as conn:
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute('DELETE FROM support_messages')
            conn.commit()
            logger.info("Все сообщения поддержки удалены.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при удалении всех сообщений: {e}")
