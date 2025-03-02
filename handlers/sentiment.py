from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.buttons import get_back_button, get_main_menu

async def sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Настроение рынка:\n\nУровень страха и жадности: <ваша информация здесь>",
        reply_markup=get_back_button()
    )

def get_sentiment_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("Настроение"), sentiment)
