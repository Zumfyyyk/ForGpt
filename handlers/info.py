from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.buttons import get_back_button, get_main_menu

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Информация о проекте:\n\nЭтот бот помогает анализировать криптовалютные графики и предоставлять информацию о рынке.",
        reply_markup=get_back_button()
    )

def get_info_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("Информация о проекте"), info)
