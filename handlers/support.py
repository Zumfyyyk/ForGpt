from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.buttons import get_back_button, get_main_menu
from database.database import save_support_message, get_support_message_by_id  # Измените импорт

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    message = update.message.text
    save_support_message(user_id, message)
    await update.message.reply_text("Ваше сообщение отправлено в поддержку. Мы свяжемся с вами в ближайшее время.", reply_markup=get_back_button())

async def respond_to_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, response: str) -> None:
    await context.bot.send_message(chat_id=user_id, text=response)

def get_support_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("Поддержка"), support)
