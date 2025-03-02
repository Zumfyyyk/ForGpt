from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.buttons import get_back_button, get_main_menu

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Поддержать проект:\n\nUAH Карточка: 4441 1144 0079 5314\nEUR Карта: 4441 1144 9042 1276\nUSDT (BEP20): (скоро)\nTrustee Plus: (скоро)",
        reply_markup=get_back_button()
    )

def get_donate_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("Поддержать проект"), donate)
