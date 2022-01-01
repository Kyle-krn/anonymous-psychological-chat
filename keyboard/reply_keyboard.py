from telebot import types

def main_keyboard():
    '''Главная клавиатура'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Найти собеседника')
    button1 = types.KeyboardButton('Настройки')
    button2 = types.KeyboardButton('Служба поддержки')
    keyboard.add(button, button1)
    keyboard.add(button2)
    return keyboard


def block_keyboard():
    '''Клавиатура заблокированного пользователя'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button2 = types.KeyboardButton('Служба поддержки')
    keyboard.add(button2)
    return keyboard


def settings_keyboard(user):
    '''Клавиатура настроек'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Я хочу помочь')
    if user['verified_psychologist'] is True:
        about_me_button = types.KeyboardButton('Обо мне')
    button1 = types.KeyboardButton('Мне нужна помощь')
    button2 = types.KeyboardButton('Мой рейтинг')
    button3 = types.KeyboardButton('Мой баланс')
    button4 = types.KeyboardButton('Пополнить счёт')
    button5 = types.KeyboardButton('Назад')
    keyboard.add(button, button1)
    if user['verified_psychologist'] is True:
        keyboard.add(about_me_button)
    keyboard.add(button2, button3)
    keyboard.add(button4)
    keyboard.add(button5)
    return keyboard


def control_companion(next=True):
    '''Клавиатура контроля собеседника'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if next:
        button1 = types.KeyboardButton('Следующий собеседник')
        keyboard.add(button1)
    button2 = types.KeyboardButton('Стоп')
    keyboard.add(button2)
    return keyboard
