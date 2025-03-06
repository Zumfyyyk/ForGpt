import logging
from database.database import log_message  # Импортируем функцию для записи логов в БД

def setup_logger():
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)

    # Создаем обработчик для записи логов в файл
    file_handler = logging.FileHandler('bot.log', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Создаем форматтер и добавляем его в обработчик
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Добавляем обработчик в логгер
    logger.addHandler(file_handler)

    # Создаем обработчик для записи в базу данных
    db_handler = DBHandler()
    db_handler.setLevel(logging.DEBUG)
    db_handler.setFormatter(formatter)

    # Добавляем обработчик в логгер
    logger.addHandler(db_handler)
    
    return logger

class DBHandler(logging.Handler):
    def emit(self, record):
        log_msg = self.format(record)  # Создаем форматированное сообщение
        log_message('INFO', log_msg)  # Здесь вызываем функцию для записи лога в базу данных
