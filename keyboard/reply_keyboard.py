from telebot import types

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Найти собеседника')
    button1 = types.KeyboardButton('Настройки')
    keyboard.add(button, button1)
    return keyboard


def settings_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Я хочу помочь')
    button1 = types.KeyboardButton('Мне нужна помощь')
    keyboard.add(button, button1)
    return keyboard


def control_companion():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # button = types.KeyboardButton('Заблокировать собеседника')
    button1 = types.KeyboardButton('Следующий собеседник')
    button2 = types.KeyboardButton('Стоп')
    keyboard.add(button1)
    keyboard.add(button2)
    return keyboard
