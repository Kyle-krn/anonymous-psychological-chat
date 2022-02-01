import os 
import shutil
from .handlers import bot, blocked_filter
from database import db
from keyboard import *


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_veif')
def cancel_verif(call):
    '''Отмена цикла хендлеров для верификации'''
    user = db.get_user_by_id(call.message.chat.id)
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if user['verified_psychologist'] != False:    return
    filepath = f'static/verefication_doc/{call.message.chat.id}/'
    if os.path.exists(filepath):
        shutil.rmtree(filepath)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'verification')
def verification_handler(call):
    '''Начало загрузки документов для верификации'''
    if blocked_filter(call.message):    return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1]  == 'yes':
        message = bot.send_message(call.message.chat.id, f"Пришлите фото диплома об образовании психолога или трудовую книжку.", reply_markup=cancel_next_handlers_verif()) 
        bot.register_next_step_handler(message, send_photo_diploma)


def save_photo(message, file_name):
    '''Сохранение фото на сервер'''
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filepath = f'static/verefication_doc/{message.chat.id}/'
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    src = filepath + file_name + '.jpg'
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)


def send_photo_diploma(message):
    '''Шаг #3 - Загружаем фото диплома или трудовой книжки'''
    if message.photo:
        save_photo(message, 'diploma_photo')
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.send_message(chat_id=message.chat.id, text='Ждите решения администрации. Обычно на это уходит не больше 1 суток.')            
        db.set_value(user_id=message.chat.id, key='verified_psychologist', value='under_consideration')
    else:
        message = bot.send_message(message.chat.id, f"Пришлите фото диплома об образовании психолога или трудовую книжку.", reply_markup=cancel_next_handlers_verif()) 
        bot.register_next_step_handler(message, send_photo_diploma)
