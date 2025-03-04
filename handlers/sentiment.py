from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.buttons import get_back_button, get_main_menu
from services.bybit_api import fetch_market_sentiment

async def sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sentiment = await fetch_market_sentiment()
    if sentiment:
        await update.message.reply_text(
            f"Настроение рынка:\n\nУровень страха и жадности: {sentiment}",
            reply_markup=get_back_button()
        )
    else:
        await update.message.reply_text(
            "Не удалось получить информацию о настроении рынка.",
            reply_markup=get_back_button()
        )

def get_sentiment_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("Настроение"), sentiment)
