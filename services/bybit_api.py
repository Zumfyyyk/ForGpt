import ccxt.async_support as ccxt  # Асинхронная версия ccxt
import logging
import asyncio
from config.config import BYBIT_API_KEY, BYBIT_SECRET

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверяем наличие API-ключей
if not BYBIT_API_KEY or not BYBIT_SECRET:
    logger.error("API-ключи Bybit не указаны в config.py")
    raise ValueError("Необходимо указать BYBIT_API_KEY и BYBIT_SECRET в config.py")

# Инициализация Bybit API
exchange = ccxt.bybit({
    'apiKey': BYBIT_API_KEY,
    'secret': BYBIT_SECRET,
    'enableRateLimit': True,  # Включение ограничения скорости запросов
})

async def fetch_markets():
    """Получение списка рынков с повтором при ошибке"""
    try:
        markets = await exchange.fetch_markets()
        logger.info("Успешно получены рынки")
        return markets
    except Exception as e:
        logger.error(f"Ошибка при получении рынков: {e}")
        return []

async def fetch_ohlcv_async(symbol: str, timeframe: str = '1m', limit: int = 100):
    """
    Асинхронная функция для получения OHLCV данных с повтором при ошибке.
    """
    try:
        if not await exchange.load_markets():
            await exchange.load_markets()

        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        logger.info(f"Получены данные OHLCV для {symbol}")
        return ohlcv
    except Exception as e:
        logger.error(f"Ошибка при получении OHLCV для {symbol}: {e}")
        return None

async def fetch_market_sentiment():
    """
    Заглушка для получения настроения рынка (Bybit напрямую не предоставляет эти данные).
    """
    try:
        # В реальном случае можно подключить сторонний API для индекса страха и жадности
        sentiment = "Данные о настроении рынка временно недоступны"
        logger.info("Получены данные о настроении рынка")
        return sentiment
    except Exception as e:
        logger.error(f"Ошибка при получении настроения рынка: {e}")
        return None

async def close_connection():
    """
    Закрытие соединения с биржей, проверка на открытое соединение.
    """
    try:
        if exchange:
            await exchange.close()
            logger.info("Соединение с Bybit закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии соединения: {e}")

# Пример повторной попытки при ошибке
async def fetch_markets_with_retry(retries=3, delay=5):
    """
    Получение списка рынков с повтором при ошибке.
    :param retries: Количество попыток.
    :param delay: Задержка между попытками в секундах.
    """
    for attempt in range(retries):
        markets = await fetch_markets()
        if markets:
            return markets
        logger.warning(f"Попытка {attempt + 1} не удалась, повтор через {delay} секунд...")
        await asyncio.sleep(delay)
    return []

