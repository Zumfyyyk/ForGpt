from .database import (
    create_tables,                 # Исправлено: заменили init_db на create_tables
    get_support_messages,
    respond_to_support_message,
    save_support_message,
    update_status,
)

__all__ = [
    "create_tables",
    "get_support_messages",
    "respond_to_support_message",
    "save_support_message",
    "update_status",
]
