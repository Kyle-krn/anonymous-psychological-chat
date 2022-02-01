from datetime import datetime
from .handlers import bot 
from keyboard import *
from database import db

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'complaint')
def complaint_handlers(call):
    '''Оставить жалобу на человека. Хендлер вызывается если человек поставил дизлайк собеседнику'''
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data.split('~')[1] == 'yes':
        companion_id = int(call.data.split('~')[2])
        message = bot.send_message(call.message.chat.id, f"Напишите жалобу ниже.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, get_complaint, companion_id)


def get_complaint(message, companion_id):
    '''Принимаем текст жалобы'''
    if message.text:
        complaint = message.text
        data = {
            'complaint': complaint,
            'date': datetime.utcnow().replace(microsecond=0),
            'check_admin': False 
        }
        db.push_value(user_id=companion_id, key='complaint', value=data)
        bot.send_message(chat_id=message.chat.id, text='Спасибо, мы обязательно рассмотрим вашу жалобу в ближайшее время.')
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    else:
        message = bot.send_message(message.chat.id, f"Напишите жалобу ниже.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, get_complaint, companion_id)