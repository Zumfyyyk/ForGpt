from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.bybit_api import fetch_markets
from utils.buttons import get_back_button, get_main_menu

async def get_markets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    markets = fetch_markets()
    usdt_markets = [m['symbol'] for m in markets if 'USDT' in m['symbol']]
    market_list = ", ".join(usdt_markets[:10]) + "..."
    await update.message.reply_text(f"Доступные пары с USDT: {market_list}", reply_markup=get_back_button())

async def show_main_menu(update: Update):
    keyboard = get_main_menu()
    await update.message.reply_text("Выбери действие:", reply_markup=keyboard)

def get_market_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("📈 Маркет"), get_markets)
