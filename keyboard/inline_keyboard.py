from telebot import types


def yes_no_keyboard(callback):
    '''Клавиатура (да, нет)'''
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Да', callback_data=f'{callback}~yes')
    button1 = types.InlineKeyboardButton(text='Нет', callback_data=f'{callback}~no')
    keyboard.add(button, button1)
    return keyboard


def rating_keyboard():
    '''Клавиаутра рейтинга'''
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='👍', callback_data='rating~+')
    button1 = types.InlineKeyboardButton(text='👎', callback_data='rating~-')
    keyboard.add(button, button1)
    return keyboard


def verification_keyboard():
    '''Клавиатура верификации'''
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Верифицировать', callback_data='verification~yes')
    button1 = types.InlineKeyboardButton(text='Нет, спасибо', callback_data='verification~no')
    keyboard.add(button, button1)
    return keyboard


def support_keyboard():
    '''Клавиатура тех. поддержка'''
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Нажмите что бы связаться со службой тех. поддержки', url='https://t.me/kyle_krn')
    keyboard.add(button)
    return keyboard


def cancel_next_handlers():
    '''Клавиатура отмены ввода'''
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
    keyboard.add(button)
    return keyboard


def helper_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Я хочу помочь', callback_data='helper~true')
    button1 = types.InlineKeyboardButton(text='Мне нужна помощь', callback_data='helper~false')
    keyboard.add(button)
    keyboard.add(button1)
    return keyboard

def choise_sum_qiwi():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='300 р.', callback_data='qiwi_order~300')
    button1 = types.InlineKeyboardButton(text='500 р.', callback_data='qiwi_order~500')
    button2 = types.InlineKeyboardButton(text='700 р.', callback_data='qiwi_order~700')
    button3 = types.InlineKeyboardButton(text='1000 р.', callback_data='qiwi_order~1000')
    button4 = types.InlineKeyboardButton(text='Отмена', callback_data='qiwi_order~cancel')
    keyboard.add(button, button1)
    keyboard.add(button2, button3)
    keyboard.add(button4)
    return keyboard

def order_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Проверить платёж', callback_data='check_payment')
    button1 = types.InlineKeyboardButton(text='Тех. поддержка', url='https://t.me/kyle_krn')
    button2 = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_payment')
    keyboard.add(button)
    keyboard.add(button1, button2)
    return keyboard
    
