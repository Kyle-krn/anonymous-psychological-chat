from handlers.handlers import bot, system_message_filter
from database import db
from keyboard import *

@bot.message_handler(regexp="^(Настройки)$")
def settings_user(message):
    if system_message_filter(message):  return
    db.update_last_action_date(message.chat.id)
    return bot.send_message(chat_id=message.chat.id, text='Выберите свою роль', reply_markup=settings_keyboard())


@bot.message_handler(regexp="^(Я хочу помочь)$")
def i_want_help(message):
    if system_message_filter(message):  return
    db.update_last_action_date(message.chat.id)
    db.helper(message.chat.id, True)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - Я хочу помочь', reply_markup=main_keyboard())
    bot.send_message(chat_id=message.chat.id, text='Вы дипломированный психолог? Верифицируйте аккаунт ', reply_markup=verification_keyboard())


@bot.message_handler(regexp="^(Мне нужна помощь)$")
def i_need_help(message):
    if system_message_filter(message):  return
    db.update_last_action_date(message.chat.id)
    db.helper(message.chat.id, False)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - мне нужна помощь', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Мой рейтинг)$")
def my_rating(message):
    if system_message_filter(message):  return
    db.update_last_action_date(message.chat.id)
    user = db.get_user_on_id(message.chat.id)
    return bot.send_message(chat_id=message.chat.id, text=f'Ваш рейтинг: {user["rating"]}.')


@bot.message_handler(regexp="^(Служба поддержки)$")
def support_handler(message):
    if system_message_filter(message):  return
    db.update_last_action_date(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text="Если вы столкнулись с проблемой или ошибкой в боте, дайте нам знать.\nВы можете обратиться к нашей службе поддержки: @kyle_krn",
                     reply_markup=support_keyboard())


@bot.message_handler(regexp="^(Назад)$")
def back_handler(message):
    if system_message_filter(message):  return
    db.update_last_action_date(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='👋', reply_markup=main_keyboard())