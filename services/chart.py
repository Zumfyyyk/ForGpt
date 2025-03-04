import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from services.bybit_api import fetch_ohlcv_async  # Correct import
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_chart(symbol: str, timeframe: str):
    logger.info(f"Fetching OHLCV data for {symbol} with timeframe {timeframe}")
    try:
        ohlcv = await fetch_ohlcv_async(symbol, timeframe, limit=30)  # Асинхронный вызов
        if not ohlcv:
            logger.error(f"No OHLCV data found for {symbol} with timeframe {timeframe}")
            return None

        times = [datetime.datetime.fromtimestamp(candle[0] / 1000) for candle in ohlcv]
        opens = [candle[1] for candle in ohlcv]
        closes = [candle[4] for candle in ohlcv]
        highs = [candle[2] for candle in ohlcv]
        lows = [candle[3] for candle in ohlcv]

        colors = ['green' if close >= open else 'red' for open, close in zip(opens, closes)]

        plt.figure(figsize=(10, 5))
        for i in range(len(ohlcv)):
            plt.plot([times[i], times[i]], [lows[i], highs[i]], color='black', linewidth=1)
            plt.plot([times[i], times[i]], [opens[i], closes[i]], color=colors[i], linewidth=6)

        plt.title(f"График {symbol} ({timeframe})", fontsize=16)
        plt.xlabel('Время', fontsize=12)
        plt.ylabel('Цена (USDT)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        logger.info(f"Chart generated for {symbol} with timeframe {timeframe}")
        return buffer
    except Exception as e:
        logger.error(f"Error generating chart for {symbol} with timeframe {timeframe}: {e}")
        return None

def generate_chart(data):
    # Реализация функции для создания графика на основе данных
    pass