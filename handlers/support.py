import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database.database import save_support_message, update_status  # Импортируем функцию для обновления статуса
from utils.buttons import get_back_button

# Настройка логирования
logger = logging.getLogger(__name__)

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    message = update.message.text
    logger.info(f"Received support message from user {user_id}: {message}")
    
    # Обновляем статус пользователя на "active"
    update_status(user_id, "active")
    
    save_support_message(user_id, message)  # Сохраняем сообщение в БД
    await update.message.reply_text("В разработке.", reply_markup=get_back_button())  # Ответ пользователю

async def respond_to_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, response: str) -> None:
    await context.bot.send_message(chat_id=user_id, text=response)

def get_support_handler() -> MessageHandler:
    return MessageHandler(filters.TEXT & filters.Regex("Поддержка"), support)  # Обработчик команд "Поддержка"
