import telebot 
from database import db
from handlers.handlers import bot, system_message_filter, blocked_filter
from keyboard import *

@bot.message_handler(regexp="(^Обо мне($|\s📖))")
def about_me_handler(message):
    user = db.get_user_by_id(message.chat.id)
    text = f'<u><b>Цена за 1 час</b></u> - {user["about_me"]["price"]} руб.\n\n' \
           f'<u><b>Представлять как</b></u> - {user["about_me"]["name"]}\n\n' \
           f'<u><b>Обо мне</b></u> - {user["about_me"]["about"]}'
    bot.send_message(message.chat.id, text=text, reply_markup=about_me_keyboard(), parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'about_me_change')
def update_about_me(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    category_about_me = call.data.split('~')[1]
    if category_about_me == 'price':
        message = bot.send_message(call.message.chat.id, text='<b>Введите цену за 1 час консультации:</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML')
        bot.register_next_step_handler(message, price_consult)
    elif category_about_me == 'name':
        message = bot.send_message(call.message.chat.id, text='<b>Как Вас представлять в начале диалога:</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML')
        bot.register_next_step_handler(message, my_name)
    elif category_about_me == 'about':
        message = bot.send_message(call.message.chat.id, text='<b>Расскажите о вашем опыте, на чем Вы спеицализируетесь и т.д. [До 700 символов]:</b>\n', reply_markup=cancel_next_handlers(), parse_mode='HTML')
        bot.register_next_step_handler(message, my_about)


# @bot.callback_query_handler(func=lambda call: call.data == 'about_me')
# def about_me_register_next_handler(call):
#     bot.delete_message(call.message.chat.id, call.message.message_id)
#     message = bot.send_message(call.message.chat.id, text='Введите цену за 1 час консультации:', reply_markup=cancel_next_handlers())
#     bot.register_next_step_handler(message, price_consult)

def price_consult(message):
    try:
        try:
            price = int(message.text)
            if price <= 0:
                message = bot.send_message(message.chat.id, text='<b>Введите цену за 1 час консультации (Цена не может быть меньше или равна 0):</b>', reply_markup=cancel_next_handlers(),parse_mode='HTML')
                return bot.register_next_step_handler(message, price_consult)
        except:
            message = bot.send_message(message.chat.id, text='<b>Введите цену за 1 час консультации (Только цифры):</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML')
            return bot.register_next_step_handler(message, price_consult)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id-1)
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        db.set_value(user_id=message.chat.id, key='about_me.price', value=price)
        about_me_handler(message)
        # message = bot.send_message(message.chat.id, text='Как вас представлять? (Введите псевдоним или имя):', reply_markup=cancel_next_handlers())
        # return bot.register_next_step_handler(message, my_name)
    except Exception as e:
        print(e)


def my_name(message):
    if not message.text:
        message = bot.send_message(message.chat.id, text='<b>Как Вас представлять в начале диалога:</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML')
        return bot.register_next_step_handler(message, my_name)
    name = message.text
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id-1)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    db.set_value(user_id=message.chat.id, key='about_me.name', value=name)
    about_me_handler(message)
    # message = bot.send_message(message.chat.id, text='Расскажите о себe. (Ваш опыт или методики лечения):', reply_markup=cancel_next_handlers())
    # return bot.register_next_step_handler(message, my_about)

def my_about(message):
    try:
        text = '<b>Расскажите о вашем опыте, на чем Вы спеицализируетесь и т.д.:</b>\n'
        if not message.text:
            message = bot.send_message(message.chat.id, text=text + '(Я понимаю только текст)', reply_markup=cancel_next_handlers(), parse_mode='HTML')
            return bot.register_next_step_handler(message, my_about)
        if len(message.text) >= 700:
            message = bot.send_message(message.chat.id, text=text + '(Слишком большой текст, попробуйте короче)', reply_markup=cancel_next_handlers(), parse_mode='HTML')
            return bot.register_next_step_handler(message, my_about)
        about = message.text
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id-1)
        db.set_value(user_id=message.chat.id, key='about_me.about', value=about)
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        about_me_handler(message)
    except Exception as e:
        print(e)