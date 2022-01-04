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
    button = types.InlineKeyboardButton(text='Нажмите что бы связаться со службой тех. поддержки', url='https://t.me/TechSupportVeles')
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

def choise_sum_qiwi(custom_coast=None):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='300 р.', callback_data='qiwi_order~300')
    button1 = types.InlineKeyboardButton(text='500 р.', callback_data='qiwi_order~500')
    button2 = types.InlineKeyboardButton(text='700 р.', callback_data='qiwi_order~700')
    button3 = types.InlineKeyboardButton(text='1000 р.', callback_data='qiwi_order~1000')
    button4 = types.InlineKeyboardButton(text='Отмена', callback_data='qiwi_order~cancel')
    if custom_coast:
        custom_coast_button = types.InlineKeyboardButton(text=f'{custom_coast} р.', callback_data=f'qiwi_order~{custom_coast}')
        keyboard.add(custom_coast_button)
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

def confirm_hisory_payment():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='История баланса', callback_data='history_balance~1'))
    return keyboard

def about_me_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(types.InlineKeyboardButton(text='Изменить данные обо мне', callback_data='about_me'))
    keyboard.add(types.InlineKeyboardButton(text='Изменить цену 💰', callback_data='about_me_change~price'))
    keyboard.add(types.InlineKeyboardButton(text='Изменить имя 🗯', callback_data='about_me_change~name'))
    keyboard.add(types.InlineKeyboardButton(text='Изменить "Обо мне" 📃', callback_data='about_me_change~about'))
    return keyboard
    
def history_payment_keyboard(payment_data, previous_page, next_page, page):
    keyboard = types.InlineKeyboardMarkup()
    for item in payment_data:
        text = ''
        if item['status'] == 'replenishment':
            text += 'Пополнение баланса --> '
        elif item['status'] == 'income':
            text += 'Доход --> '   
        elif item['status'] == 'consumption':
            text += 'Расход --> '
        elif item['status'] == 'transfer_money':
            text += 'Вывод --> '
        text += f'{item["coast"]} рублей от {item["date"].strftime("%m/%d/%Y, %H:%M:%S")}'
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data='cc'))
    previous_button = None
    next_button = None
    if previous_page:
        previous_button = types.InlineKeyboardButton(text='⬅️', callback_data=f'history_balance~{previous_page}')
    page_button = types.InlineKeyboardButton(text=f'Страница #{page}', callback_data=f'history_balance~{page}')
    if next_page:
        next_button = types.InlineKeyboardButton(text='➡️', callback_data=f'history_balance~{next_page}')
    if previous_button and next_button:
        keyboard.add(previous_button, page_button, next_button)
    elif previous_button:
        keyboard.add(previous_button, page_button)
    elif next_button:
        keyboard.add(page_button, next_button)
    else:
        keyboard.add(page_button)
    close_button = types.InlineKeyboardButton(text='Закрыть ❌', callback_data=f'history_balance~close')
    keyboard.add(close_button)
    return keyboard

def i_need_help_settings_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Искать всех', callback_data='i_need_help~all')
    button1 = types.InlineKeyboardButton(text='Искать только верифицированных психологов', callback_data='i_need_help~verif')
    keyboard.add(button)
    keyboard.add(button1)
    return keyboard

def premium_rating_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    # for i in range(1,6):
    b = types.InlineKeyboardButton(text='⭐', callback_data='premium_rating~1')
    b1 = types.InlineKeyboardButton(text='⭐⭐', callback_data='premium_rating~2')
    b2 = types.InlineKeyboardButton(text='⭐⭐⭐', callback_data='premium_rating~3')
    b3 = types.InlineKeyboardButton(text='⭐⭐⭐⭐', callback_data='premium_rating~4')
    b4 = types.InlineKeyboardButton(text='⭐⭐⭐⭐⭐', callback_data='premium_rating~5')
    # keyboard.add(b,b1,b2,b3,b4)
    keyboard.add(b4)
    keyboard.add(b3)
    keyboard.add(b2)
    keyboard.add(b1)
    keyboard.add(b)
    return keyboard

def stop_review_keyboard(review_for, rating):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Закончить', callback_data=f'stop_premium_rating~{review_for}~{rating}'))
    return keyboard

def start_view_review_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Просмотреть отзывы', callback_data=f'view_premium_rating~1'))
    return keyboard

def view_review_keyboard(page, previous_page, next_page):
    keyboard = types.InlineKeyboardMarkup()
    page_button = types.InlineKeyboardButton(text=f'Страница #{page}', callback_data=f'view_premium_rating~{page}') 
    if previous_page and next_page:
        previous_page = types.InlineKeyboardButton(text='⬅️', callback_data=f'view_premium_rating~{previous_page}')
        next_page = types.InlineKeyboardButton(text='➡️', callback_data=f'view_premium_rating~{next_page}')
        keyboard.add(previous_page, page_button, next_page)
    elif previous_page:
        previous_page = types.InlineKeyboardButton(text='⬅️', callback_data=f'view_premium_rating~{previous_page}')
        keyboard.add(previous_page, page_button)
    elif next_page:
        next_page = types.InlineKeyboardButton(text='➡️', callback_data=f'view_premium_rating~{next_page}')
        keyboard.add(page_button, next_page)
    else:
        keyboard.add(page_button)
    keyboard.add(types.InlineKeyboardButton(text='❌', callback_data=f'view_premium_rating~close'))
    return keyboard