import logging
import asyncio
import threading
import httpx
from telegram.ext import ApplicationBuilder
from flask import Flask, render_template, request, redirect, url_for
from handlers.start import get_start_handler
from handlers.analysis import get_analysis_handlers
from handlers.support import get_support_handler
from handlers.market import get_market_handler
from handlers.donate import get_donate_handler
from handlers.info import get_info_handler
from handlers.sentiment import get_sentiment_handler
from handlers.back import get_back_handler
from database.database import create_tables, get_logs, get_support_messages, respond_to_support_message
from config.config import TOKEN
import nest_asyncio

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Token: {TOKEN}")

create_tables()

app = Flask(__name__)
app.telegram_context = None

@app.route('/')
def index():
    logs = get_logs()
    support_messages = get_support_messages()
    return render_template('index.html', logs=logs, support_messages=support_messages)

@app.route('/respond', methods=['POST'])
def respond():
    message_id = request.form['message_id']
    response = request.form['response']
    respond_to_support_message(message_id, response)
    return redirect(url_for('index'))

async def run_bot():
    application = ApplicationBuilder().token(TOKEN).http_version("1.1").build()
    app.telegram_context = application
    logging.debug("Приложение Telegram создано успешно.")
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

def run_flask():
    app.run(debug=True, use_reloader=False, threaded=True)

def start_flask_in_thread():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

async def main():
    start_flask_in_thread()
    await run_bot()

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
