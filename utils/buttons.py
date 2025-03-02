from telegram import ReplyKeyboardMarkup

main_menu = [
            ["📊 График", "📈 Маркет"],
            ["Поддержать проект", "Информация о проекте"],
            ["Поддержка", "Настроение"]
]
back_button = [["Назад"]]

def get_main_menu():
    return ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

def get_back_button():
    return ReplyKeyboardMarkup(back_button, resize_keyboard=True)
