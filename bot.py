import logging
import asyncio
import threading
import sys
import sqlite3
import nest_asyncio
from flask import Flask, render_template, request, redirect, url_for, session
from telegram.ext import ApplicationBuilder
from handlers.start import get_start_handler
from handlers.analysis import get_analysis_handlers
from handlers.support import get_support_handler
from handlers.market import get_market_handler
from handlers.donate import get_donate_handler
from handlers.info import get_info_handler
from handlers.sentiment import get_sentiment_handler
from handlers.back import get_back_handler
from database.database import create_tables, respond_to_support_message, get_support_messages, clear_all_support_messages
from config.config import TOKEN, USERNAME, PASSWORD, SECRET_KEY
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logger import setup_logger

# Применение nest_asyncio для поддержки многозадачности в Windows
nest_asyncio.apply()

# Устанавливаем настройку логирования
logger = setup_logger()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Создание таблиц при запуске
create_tables()

# Глобальные переменные для приложения и планировщика
application = None
scheduler = None

# Настройка Flask-приложения
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Для обновления изменений в шаблонах

# Главная страница
@app.route('/')
def home():
    return redirect(url_for('login'))

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = "Неверные учетные данные!"

    return render_template('login.html', error=error)

# Страница базы данных
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    support_messages = get_support_messages()
    return render_template('index.html', support_messages=support_messages)

# Страница поддержки
@app.route('/support')
def support():
    return render_template('support.html')

# Страница настроек
@app.route('/settings')
def settings():
    return render_template('settings.html')

# Логирование
@app.route('/view_logs')
def view_logs():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        with sqlite3.connect('crypto_bot.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC')
            logs = cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при доступе к базе данных для логов: {e}")
        logs = []

    return render_template('logger.html', logs=logs)

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Обработка ответов на сообщения поддержки
@app.route('/respond', methods=['POST'])
def respond():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    message_id = request.form.get('message_id')
    response = request.form.get('response')

    if message_id and response:
        respond_to_support_message(message_id, response)
    return redirect(url_for('dashboard'))

# Очистка чатов
@app.route('/clear_chats', methods=['POST'])
def clear_chats():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    clear_all_support_messages()
    return redirect(url_for('dashboard'))

# Очистка логов
@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        with sqlite3.connect('crypto_bot.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM logs')
            conn.commit()
        logger.info("Логи успешно очищены.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при очистке логов: {e}")

    return redirect(url_for('view_logs'))

async def shutdown():
    logger.info("Завершаю все задачи перед остановкой бота.")
    # Завершаем все активные задачи, если они есть
    tasks = asyncio.all_tasks()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Задачи завершены. Остановка бота.")

# Функция запуска Telegram-бота
async def run_bot():
    global application
    application = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(60).build()

    logger.info("Telegram-бот успешно создан.")

    # Добавляем обработчики
    application.add_handler(get_start_handler())
    for handler in get_analysis_handlers():
        application.add_handler(handler)

    application.add_handler(get_support_handler())
    application.add_handler(get_market_handler())
    application.add_handler(get_donate_handler())
    application.add_handler(get_info_handler())
    application.add_handler(get_sentiment_handler())
    application.add_handler(get_back_handler())

    try:
        logger.info("Бот запущен. Нажми CTRL+C для остановки.")
        await application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка работы бота: {e}", exc_info=True)
    finally:
        logger.info("Остановка бота...")
        if application and application.running:
            await application.stop()
        if scheduler:
            scheduler.shutdown(wait=False)
        logger.info("Бот успешно остановлен.")

# Функция запуска Flask
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)

# Запуск Flask в отдельном потоке
def start_flask_in_thread():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

# Основная асинхронная функция
async def main():
    global scheduler

    # Запуск Flask
    start_flask_in_thread()

    # Настройка планировщика
    scheduler = AsyncIOScheduler()
    scheduler.start()

    # Запуск Telegram-бота
    await run_bot()

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
