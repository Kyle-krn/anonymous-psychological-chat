from telebot import types


def yes_no_keyboard(callback):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Да', callback_data=f'{callback}~yes')
    button1 = types.InlineKeyboardButton(text='Нет', callback_data=f'{callback}~no')
    keyboard.add(button, button1)
    return keyboard


def rating_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='👍', callback_data='rating~+')
    button1 = types.InlineKeyboardButton(text='👎', callback_data='rating~-')
    keyboard.add(button, button1)
    return keyboard