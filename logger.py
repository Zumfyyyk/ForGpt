import logging

def setup_logger():
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)
    
    # Создаем обработчик для записи логов в файл
    handler = logging.FileHandler('bot.log', mode='w', encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    
    # Создаем форматтер и добавляем его в обработчик
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Добавляем обработчик в логгер
    logger.addHandler(handler)
    
    return logger