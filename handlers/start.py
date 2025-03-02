from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from utils.buttons import get_main_menu

WELCOME_MESSAGE = """
👋 Привет\\! Я — *CryptoBot*\\.

✅ Что я умею\\:
\\- Показывать графики криптовалют за последние 30 минут \\(в формате свечей\\)\\.
\\- Отображать доступные торговые пары с USDT\\.

📊 *Как использовать*\\:
1\\. Нажми "📊 График" и введи монету \\(например, BTC/USDT\\)\\.
2\\. Получи график с последними свечами\\.

🔔 Больше функций скоро\\!
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown_v2(WELCOME_MESSAGE)
    await show_main_menu(update)

async def show_main_menu(update: Update):
    keyboard = get_main_menu()
    await update.message.reply_text("Выбери действие:", reply_markup=keyboard)

def get_start_handler() -> CommandHandler:
    return CommandHandler("start", start)
