import ccxt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler
from services.chart import generate_chart
from services.bybit_api import fetch_ohlcv_async
from utils.buttons import get_back_button, get_main_menu
from handlers.start import show_main_menu

exchange = ccxt.bybit()  # Инициализация биржи

TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "5h"]  # Допустимые временные интервалы

async def request_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите монету в формате: BTC/USDT", reply_markup=get_back_button())

async def select_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    symbol = update.message.text.strip().upper()
    markets = exchange.load_markets()
    if symbol not in markets:
        await update.message.reply_text("Неверный символ. Пожалуйста, введите символ в формате: BTC/USDT.")
        return

    context.user_data['symbol'] = symbol
    keyboard = [[InlineKeyboardButton(tf, callback_data=tf) for tf in TIMEFRAMES]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите временной интервал:", reply_markup=reply_markup)

async def send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    timeframe = query.data
    symbol = context.user_data.get('symbol')

    try:
        chart = await generate_chart(symbol, timeframe)
        if chart:
            await query.message.reply_photo(photo=chart)
        else:
            await query.message.reply_text("Не удалось получить данные для графика.")
    except ccxt.BaseError as e:
        if isinstance(e, ccxt.BadSymbol):
            await query.message.reply_text("Неверный символ. Пожалуйста, введите символ в формате: BTC/USDT.")
        else:
            await query.message.reply_text("Произошла ошибка при получении данных.")
    return await show_main_menu(update)

async def handle_chart_request(symbol, interval, user_id):
    data = await fetch_ohlcv_async(symbol, interval)
    chart = generate_chart(data)
    # Код для отправки графика пользователю
    pass

def get_analysis_handlers() -> list:
    return [
        MessageHandler(filters.TEXT & filters.Regex("📊 График"), request_chart),
        MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("Назад") & filters.Regex("^[A-Z]+/[A-Z]+$"), select_timeframe),
        CallbackQueryHandler(send_chart, pattern='^(1m|5m|15m|30m|1h|2h|4h|5h)$'),
    ]
