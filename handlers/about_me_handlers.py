import telebot 
from database import db
from handlers.handlers import bot, system_message_filter, blocked_filter
from keyboard import *

@bot.message_handler(regexp="^(Обо мне)$")
def about_me_handler_step_1(message):
    user = db.get_user_by_id(message.chat.id)
    text = f'Цена за 1 час консультации - {user["about_me"]["price"]}\n\n' \
           f'Имя или псевдоним - {user["about_me"]["name"]}\n\n' \
           f'Обо мне - {user["about_me"]["about"]}'
    bot.send_message(message.chat.id, text=text, reply_markup=about_me_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'about_me')
def about_me_register_next_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = bot.send_message(call.message.chat.id, text='Введите цену за 1 час консультации:', reply_markup=cancel_next_handlers())
    bot.register_next_step_handler(message, price_consult)

def price_consult(message):
    try:
        try:
            price = int(message.text)
        except:
            message = bot.send_message(message.chat.id, text='Введите цену за 1 час консультации (только цифры):', reply_markup=cancel_next_handlers())
            return bot.register_next_step_handler(message, price_consult)
        db.set_value(user_id=message.chat.id, key='about_me.price', value=price)
        message = bot.send_message(message.chat.id, text='Как вас представлять? (Введите псевдоним или имя):', reply_markup=cancel_next_handlers())
        return bot.register_next_step_handler(message, my_name)
    except Exception as e:
        print(e)

def my_name(message):
    if not message.text:
        message = bot.send_message(message.chat.id, text='Как вас представлять? (Введите псевдоним или имя):', reply_markup=cancel_next_handlers())
        return bot.register_next_step_handler(message, my_name)
    name = message.text
    db.set_value(user_id=message.chat.id, key='about_me.name', value=name)
    message = bot.send_message(message.chat.id, text='Расскажите о себe. (Ваш опыт или методики лечения):', reply_markup=cancel_next_handlers())
    return bot.register_next_step_handler(message, my_about)

def my_about(message):
    try:
        if not message.text:
            message = bot.send_message(message.chat.id, text='Расскажите о себe. (Ваш опыт или методики лечения):', reply_markup=cancel_next_handlers())
            return bot.register_next_step_handler(message, my_about)
        about = message.text
        db.set_value(user_id=message.chat.id, key='about_me.about', value=about)
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.send_message(message.chat.id, text='Информация о вас была обновлена.')
    except Exception as e:
        print(e)