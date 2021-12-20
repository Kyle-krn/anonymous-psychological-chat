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

def verification_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Верифицировать', callback_data='verification~yes')
    button1 = types.InlineKeyboardButton(text='Нет, спасибо', callback_data='verification~no')
    keyboard.add(button, button1)
    return keyboard

def support_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Нажмите что бы связаться со службой тех. поддержки', url='https://t.me/kyle_krn')
    keyboard.add(button)
    return keyboard

def cancel_next_handlers():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
    keyboard.add(button)
    return keyboard