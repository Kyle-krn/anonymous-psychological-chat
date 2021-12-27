from handlers.handlers import bot, system_message_filter, blocked_filter
from database import db
from keyboard import *


@bot.message_handler(regexp="^(Настройки)$")
def settings_user(message):
    if system_message_filter(message):  return
    if blocked_filter(message):    return
    db.update_last_action_date(message.chat.id)
    return bot.send_message(chat_id=message.chat.id, text='Выберите свою роль', reply_markup=settings_keyboard())


@bot.message_handler(regexp="^(Я хочу помочь)$")
def i_want_help(message):
    if system_message_filter(message):  return
    if blocked_filter(message):    return
    db.update_last_action_date(message.chat.id)
    db.helper(message.chat.id, True)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - Я хочу помочь', reply_markup=main_keyboard())
    user = db.get_user_on_id(message.chat.id)
    if user['verified_psychologist'] is False:
        bot.send_message(chat_id=message.chat.id, text='Вы дипломированный психолог? Верифицируйте аккаунт', reply_markup=verification_keyboard())
    elif user['verified_psychologist'] == 'under_consideration':
        bot.send_message(chat_id=message.chat.id, text='Ваша заявка на верификацию находтся на рассмотрении.')
    elif user['verified_psychologist'] is True:
        bot.send_message(chat_id=message.chat.id, text='Ваш аккаунт верифицирован.')


@bot.message_handler(regexp="^(Мне нужна помощь)$")
def i_need_help(message):
    if system_message_filter(message):  return
    if blocked_filter(message):    return
    db.update_last_action_date(message.chat.id)
    db.helper(message.chat.id, False)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - мне нужна помощь.', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Мой рейтинг)$")
def my_rating(message):
    if system_message_filter(message):  return
    if blocked_filter(message):    return
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
    if blocked_filter(message):    return
    db.update_last_action_date(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='👋', reply_markup=main_keyboard())


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'helper')
def helper_inline_handler(call):
    helper_bool = call.data.split('~')[1]
    if helper_bool == 'true':
        helper_bool = True
        text = '<u><b>Ваша роль - Я хочу помочь</b></u>'
    elif helper_bool == 'false':
        helper_bool = False
        text = '<u><b>Ваша роль - Мне нужна помощь</b></u>'
    bot.delete_message(call.message.chat.id, call.message.message_id)
    db.helper(call.message.chat.id, helper_bool)
    bot.send_message(call.message.chat.id, text=text, parse_mode='HTML')
    if helper_bool is True:
        bot.send_message(chat_id=call.message.chat.id, text='Вы дипломированный психолог? Верифицируйте аккаунт ', reply_markup=verification_keyboard())



