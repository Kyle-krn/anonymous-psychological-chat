from telebot import types

def main_keyboard():
    '''Главная клавиатура'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Найти собеседника 🎯')
    button1 = types.KeyboardButton('Настройки ⚙')
    button2 = types.KeyboardButton('Служба поддержки 🗣')
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
    i_want_help_button = types.KeyboardButton('Я хочу помочь 👩‍⚕️')
    if user['verified_psychologist'] is True:
        about_me_button = types.KeyboardButton('Обо мне 📖')
    i_need_help_button = types.KeyboardButton('Мне нужна помощь 💆‍♂️')
    my_rating = types.KeyboardButton('Мой рейтинг 📈')
    my_balance = types.KeyboardButton('Мой баланс 💰')
    top_up_account_button = types.KeyboardButton('Пополнить счёт 💳')
    back_button = types.KeyboardButton('Назад 🔙')
    keyboard.add(i_want_help_button, i_need_help_button)
    if user['verified_psychologist'] is True:
        keyboard.add(about_me_button)
    keyboard.add(my_rating, top_up_account_button, my_balance)
    # keyboard.add(top_up_account_button)
    keyboard.add(back_button)
    return keyboard


def control_companion(next=True):
    '''Клавиатура контроля собеседника'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if next:
        button1 = types.KeyboardButton('Следующий собеседник ⏭')
        keyboard.add(button1)
    button2 = types.KeyboardButton('Стоп ⛔️')
    keyboard.add(button2)
    return keyboard

def control_companion_verif():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Следующий собеседник ⏭')
    button2 = types.KeyboardButton('Начать консультацию 📒')
    button3 = types.KeyboardButton('Стоп ⛔️')
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    return keyboard