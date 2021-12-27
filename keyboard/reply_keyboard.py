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


def settings_keyboard():
    '''Клавиатура настроек'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Я хочу помочь')
    button1 = types.KeyboardButton('Мне нужна помощь')
    button2 = types.KeyboardButton('Мой рейтинг')
    button3 = types.KeyboardButton('Назад')
    keyboard.add(button, button1)
    keyboard.add(button2)
    keyboard.add(button3)
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
