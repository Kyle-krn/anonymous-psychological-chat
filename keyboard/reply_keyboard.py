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
    keyboard.add(types.KeyboardButton('Служба поддержки'))
    return keyboard


def settings_keyboard(user):
    '''Клавиатура настроек'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    i_want_help_button = types.KeyboardButton('Я хочу помочь 👩‍⚕️')
    if user['verified_psychologist'] is True:
        about_me_button = types.KeyboardButton('Обо мне 📖')
        my_premium_rating = types.KeyboardButton('Отзывы и оценка психолога 📊')
        transfer_money = types.KeyboardButton('Вывод денег 💸')
    i_need_help_button = types.KeyboardButton('Мне нужна помощь 💆‍♂️')
    my_rating = types.KeyboardButton('Мой рейтинг 📈')
    my_balance = types.KeyboardButton('Мой баланс 💰')
    top_up_account_button = types.KeyboardButton('Пополнить счёт 💳')
    back_button = types.KeyboardButton('Назад 🔙')
    keyboard.add(i_want_help_button, i_need_help_button)
    if user['verified_psychologist'] is True:
        keyboard.add(about_me_button, transfer_money)
        keyboard.add(my_premium_rating)
    keyboard.add(my_rating, top_up_account_button, my_balance)
    if user['favorite_chat'] and user['helper'] is False:
        favorite_button = types.KeyboardButton('Избранные чаты ⭐')
        keyboard.add(favorite_button)
    keyboard.add(back_button)
    return keyboard


def control_companion(next=True):
    '''Клавиатура контроля собеседника'''
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if next:
        keyboard.add(types.KeyboardButton('Следующий собеседник ⏭'))
    keyboard.add(types.KeyboardButton('Стоп ⛔️'))
    return keyboard


def control_companion_verif():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Следующий собеседник ⏭'))
    keyboard.add(types.KeyboardButton('Начать консультацию 📒'))
    keyboard.add(types.KeyboardButton('Стоп ⛔️'))
    return keyboard