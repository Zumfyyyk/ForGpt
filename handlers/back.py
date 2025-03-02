from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.buttons import get_main_menu

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Выбери действие:", reply_markup=get_main_menu())

def get_back_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("Назад"), back)
