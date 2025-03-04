import logging
import asyncio
import threading
import httpx
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
from database.database import create_tables, respond_to_support_message, get_support_messages
from config.config import TOKEN, USERNAME, PASSWORD, SECRET_KEY
import nest_asyncio

# Настройка логирования
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Token: {TOKEN}")

# Создание таблиц при запуске
create_tables()

# Настройка Flask-приложения
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.telegram_context = None

# Главная страница
@app.route('/')
def home():
    return redirect(url_for('login'))  # Перенаправление на страницу логина

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Инициализация переменной для ошибки
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем логин и пароль из config.py
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = "Неверные учетные данные!"  # Устанавливаем ошибку, если логин или пароль неверны

    return render_template('login.html', error=error)  # Передаем ошибку в шаблон

# Страница базы данных (доступ только после авторизации)
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Получаем все активные сообщения из базы данных
    support_messages = get_support_messages()

    return render_template('index.html', support_messages=support_messages)

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


# Функция запуска Telegram-бота
async def run_bot():
    application = ApplicationBuilder().token(TOKEN).http_version("1.1").build()
    app.telegram_context = application

    logging.debug("Приложение Telegram создано успешно.")

    # Добавление обработчиков команд
    application.add_handler(get_start_handler())

    for handler in get_analysis_handlers():
        application.add_handler(handler)

    application.add_handler(get_support_handler())
    application.add_handler(get_market_handler())
    application.add_handler(get_donate_handler())
    application.add_handler(get_info_handler())
    application.add_handler(get_sentiment_handler())
    application.add_handler(get_back_handler())

    print("Бот запущен. Нажми CTRL+C для остановки.")
    await application.run_polling()

# Функция запуска Flask
def run_flask():
    app.run(debug=True, use_reloader=False, threaded=True)

# Запуск Flask в отдельном потоке
def start_flask_in_thread():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Обеспечивает завершение потока при выходе программы
    flask_thread.start()

# Основная асинхронная функция
async def main():
    start_flask_in_thread()  # Запуск Flask в фоновом потоке
    await run_bot()  # Запуск Telegram-бота в асинхронном режиме

if __name__ == "__main__":
    nest_asyncio.apply()  # Разрешение асинхронных операций в основном потоке
    asyncio.run(main())  # Запуск основной функции
