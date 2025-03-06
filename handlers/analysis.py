import ccxt
import numpy as np
import pandas as pd
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.chart import generate_chart
from services.bybit_api import fetch_ohlcv_async
from utils.buttons import get_back_button, get_main_menu
from handlers.start import show_main_menu
from logger import setup_logger

exchange = ccxt.bybit()
logger = setup_logger()

def calculate_indicators(data):
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # KDJ
    low_min = df['low'].rolling(window=9).min()
    high_max = df['high'].rolling(window=9).max()
    df['RSV'] = (df['close'] - low_min) / (high_max - low_min) * 100
    df['K'] = df['RSV'].ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    # Bollinger Bands
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['BOLL_UP'] = df['MA20'] + 2 * df['close'].rolling(window=20).std()
    df['BOLL_DOWN'] = df['MA20'] - 2 * df['close'].rolling(window=20).std()

    # Buy/Sell signals
    df['Bullish'] = (df['RSI'] < 30) & (df['MACD'] > df['Signal_Line'])
    df['Bearish'] = (df['RSI'] > 70) & (df['MACD'] < df['Signal_Line'])

    return df.iloc[-1]

async def request_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите монету в формате: BTC/USDT", reply_markup=get_back_button())

async def select_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    symbol = update.message.text.strip().upper()
    markets = exchange.load_markets()
    if symbol not in markets:
        await update.message.reply_text("Неверный символ. Введите в формате: BTC/USDT")
        return

    context.user_data['symbol'] = symbol
    await update.message.reply_text("Введите временной интервал (например, 1m, 5m, 1h, 4h):", reply_markup=get_back_button())

async def send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    timeframe = update.message.text.strip()
    symbol = context.user_data.get('symbol')

    try:
        await handle_chart_request(symbol, timeframe, update.effective_chat.id, context)
    except Exception as e:
        logger.error(f"Ошибка при запросе данных: {e}")
        await update.message.reply_text("Произошла ошибка при получении данных.")

async def handle_chart_request(symbol, interval, user_id, context) -> None:
    data = await fetch_ohlcv_async(symbol, interval)
    if not data:
        await context.bot.send_message(chat_id=user_id, text="Не удалось получить данные.")
        return

    chart = await generate_chart(symbol, interval)
    indicators = calculate_indicators(data)

    analysis_msg = (
        f"📊 Анализ {symbol}\n"
        f"RSI: {indicators['RSI']:.2f}\n"
        f"MACD: {indicators['MACD']:.2f} (Signal: {indicators['Signal_Line']:.2f})\n"
        f"KDJ (K/D/J): {indicators['K']:.2f}/{indicators['D']:.2f}/{indicators['J']:.2f}\n"
        f"BOLL: {indicators['BOLL_DOWN']:.2f} - {indicators['MA20']:.2f} - {indicators['BOLL_UP']:.2f}\n"
        f"Бычьи сигналы: {'Да' if indicators['Bullish'] else 'Нет'}\n"
        f"Медвежьи сигналы: {'Да' if indicators['Bearish'] else 'Нет'}"
    )

    await context.bot.send_photo(chat_id=user_id, photo=chart)
    await context.bot.send_message(chat_id=user_id, text=analysis_msg)

def get_analysis_handlers() -> list:
    return [
        MessageHandler(filters.TEXT & filters.Regex("📊 График"), request_chart),
        MessageHandler(filters.TEXT & filters.Regex("^[A-Z]+/[A-Z]+$"), select_timeframe),
        MessageHandler(filters.TEXT & filters.Regex("^(1m|5m|15m|30m|1h|2h|4h)$"), send_chart),
    ]
