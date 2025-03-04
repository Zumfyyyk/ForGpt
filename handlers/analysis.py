import ccxt
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.chart import generate_chart
from services.bybit_api import fetch_ohlcv_async
from utils.buttons import get_back_button, get_main_menu
from handlers.start import show_main_menu
from logger import setup_logger

exchange = ccxt.bybit()  # Инициализация биржи
logger = setup_logger()  # Настройка логгера

async def request_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("Получена команда для запроса графика")
    await update.message.reply_text("Введите монету в формате: BTC/USDT", reply_markup=get_back_button())

async def select_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    symbol = update.message.text.strip().upper()
    markets = exchange.load_markets()
    if symbol not in markets:
        logger.debug(f"Неверный символ: {symbol}")
        await update.message.reply_text("Неверный символ. Пожалуйста, введите символ в формате: BTC/USDT.")
        return

    context.user_data['symbol'] = symbol
    logger.debug(f"Выбран символ: {symbol}")
    await update.message.reply_text("Введите временной интервал (например, 1m, 5m, 15m, 30m, 1h, 2h, 4h, 5h):", reply_markup=get_back_button())

async def send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    timeframe = update.message.text.strip()
    symbol = context.user_data.get('symbol')
    logger.debug(f"Выбран временной интервал: {timeframe} для символа: {symbol}")

    try:
        await handle_chart_request(symbol, timeframe, update.effective_chat.id, context)
    except ccxt.BaseError as e:
        if isinstance(e, ccxt.BadSymbol):
            logger.error(f"Неверный символ: {symbol}")
            await update.message.reply_text("Неверный символ.")
        else:
            logger.error(f"Ошибка при получении данных: {e}")
            await update.message.reply_text("Произошла ошибка при получении данных.")
    return await show_main_menu(update)

async def handle_chart_request(symbol, interval, user_id, context) -> None:
    logger.debug(f"Запрос данных для символа: {symbol} с интервалом: {interval}")
    data = await fetch_ohlcv_async(symbol, interval)
    chart = await generate_chart(symbol, interval)
    if chart:
        await context.bot.send_photo(chat_id=user_id, photo=chart)
        logger.debug(f"График отправлен пользователю: {user_id}")
    else:
        await context.bot.send_message(chat_id=user_id, text="Не удалось сгенерировать график.")
        logger.error(f"Не удалось сгенерировать график для символа: {symbol} с интервалом: {interval}")

def get_analysis_handlers() -> list:
    logger.debug("Настройка обработчиков анализа")
    return [
        MessageHandler(filters.TEXT & filters.Regex("📊 График"), request_chart),
        MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("Назад") & filters.Regex("^[A-Z]+/[A-Z]+$"), select_timeframe),
        MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("Назад") & filters.Regex("^(1m|5m|15m|30m|1h|2h|4h|5h)$"), send_chart),
    ]
