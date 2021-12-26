from database import db
from settings import TELEGRAM_TOKEN
import telebot
from keyboard import *
from datetime import datetime
import os
import shutil


bot = telebot.TeleBot(TELEGRAM_TOKEN)

def system_message_filter(message):
    '''В случае если пользователь пишет какое либо системное сообщение и у пользователя активный диалог, пересылает это сообщение
       собеседнику, а не отрабаывает опредленный хендлер'''
    user = db.get_or_create_user(message.chat)
    if user['companion_id']:
        return chat(message)

def blocked_filter(message):
    '''Фильтр для заблокированных пользователей'''
    user = db.get_or_create_user(message.chat)
    if user['blocked'] is True:
        return bot.send_message(chat_id=message.chat.id, text='<u><b>Сообщение от администрации:</b></u>\n\nВы заблокированны', parse_mode='HTML')

@bot.message_handler(commands=['start', 'help'])
def command_start(message):
    user = db.get_or_create_user(message.chat)
    if system_message_filter(message):  return
    if blocked_filter(message):    return
    return bot.send_message(chat_id=message.chat.id, text='Это приветственное сообщение бота', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Найти собеседника)$")
def companion(message):
    '''Поиск собеседника'''
    if blocked_filter(message):    return
    user = db.get_or_create_user(message.chat)
    db.update_last_action_date(message.chat.id)
    if user['helper'] is None:
        return bot.send_message(chat_id=message.chat.id, text='Необходимо выбрать роль, для этого перейдите в настройки', reply_markup=main_keyboard())
    answer = db.search_companion(message.chat.id)

    user = db.get_or_create_user(message.chat)  # второй раз получаем юзера потому что в search_companion() юзер обновлен
    if answer:
        db.push_date_in_start_dialog_time(user['companion_id'])     # Записываем дату и время начала диалога
        bot.send_message(chat_id=user['companion_id'], text=f'Собеседник найден! Рейтинг вашего собеседника: {user["rating"]}. Вы можете начать общение.', reply_markup=control_companion())
        companion_user = db.get_user_on_id(user['companion_id'])
        db.push_date_in_start_dialog_time(message.chat.id)          # Записываем дату и время начала диалога
        return bot.send_message(chat_id=message.chat.id, text=f'Собеседник найден! Рейтинг вашего собеседника: {companion_user["rating"]}. Вы можете начать общение.', reply_markup=control_companion())
    return bot.send_message(chat_id=message.chat.id, text='Ожидание собедсеника ⌛', reply_markup=control_companion(next=False))


@bot.message_handler(regexp='^(Следующий собеседник)$')
def next_companion(message):
    if blocked_filter(message):    return
    bot.delete_message(message.chat.id, message.message_id)
    user = db.get_user_on_id(message.chat.id)
    db.update_last_action_date(message.chat.id)
    if not user['companion_id']:
        return companion(message)
    bot.send_message(chat_id=message.chat.id, text='Вы уверены что хотите пропустить собеседника?', reply_markup=yes_no_keyboard('next_companion'))    


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'next_companion')
def next_companion_inline(call):
    if blocked_filter(call.message):    return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_on_id(call.message.chat.id)
    db.update_last_action_date(call.message.chat.id)
    if not user['companion_id']:
        return companion(call.message)
    if call.data.split('~')[1] == 'yes':
        user = db.get_user_on_id(call.message.chat.id)
        db.push_date_in_end_dialog_time(call.message.chat.id) # Записываем дату и время конца диалога
        db.update_statistic_inc(call.message.chat.id, 'output_finish')
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        db.push_date_in_end_dialog_time(user['companion_id']) # Записываем дату и время конца диалога
        db.update_statistic_inc(user['companion_id'], 'input_finish')
        rating_message(call.message)
        db.next_companion(call.message.chat.id)
        companion(call.message)


@bot.message_handler(regexp='^(Стоп)$')
def stop_search_handler(message):
    if blocked_filter(message):    return
    user = db.get_or_create_user(message.chat)
    db.update_last_action_date(message.chat.id)
    if user['companion_id']:
        db.push_date_in_end_dialog_time(message.chat.id) # Записываем дату и время конца диалога
        db.update_statistic_inc(message.chat.id, 'output_finish')
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        db.push_date_in_end_dialog_time(user['companion_id']) # Записываем дату и время конца диалога
        db.update_statistic_inc(user['companion_id'], 'input_finish')
        rating_message(message)
        db.cancel_search(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='Вы завершили диалог.', reply_markup=main_keyboard())


def rating_message(message):
    if blocked_filter(message):    return
    user = db.get_user_on_id(message.chat.id)
    db.update_last_action_date(message.chat.id)
    rating_message_companion = bot.send_message(chat_id=user['companion_id'], text='Как вы оцените вашего собеседника?', reply_markup=rating_keyboard())
    rating_data_companion = {
        'user_id': message.chat.id,
        'message_id': rating_message_companion.message_id 
    }
    db.push_data_rating_companion(user['companion_id'], rating_data_companion)
    rating_message = bot.send_message(chat_id=message.chat.id, text='Как вы оцените вашего собеседника?', reply_markup=rating_keyboard())
    rating_data = {
        'user_id': user['companion_id'],
        'message_id': rating_message.message_id
    }
    db.push_data_rating_companion(message.chat.id, rating_data)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'rating')
def rating_handler(call):
    if blocked_filter(call.message):    return
    data_rating = db.get_data_rating_companion(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1] == "+":
        count = 1
    else:
        count = -2
    db.inc_rating(data_rating['user_id'], count)
    db.delete_data_rating_companion(call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Спасибо, ваш голос учтен!')


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_register_next_step_handler(call):
    user = get_user_on_id(call.message.chat.id)
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if user['verified_psychologist'] != False:    return
    filepath = f'static/verefication_doc/{call.message.chat.id}/'
    if os.path.exists(filepath):
        shutil.rmtree(filepath)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'verification')
def verification_handler(call):
    if blocked_filter(call.message):    return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1]  == 'yes':
        message = bot.send_message(call.message.chat.id, f"Пришлите фото паспорта.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, send_photo_pasport)


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


def send_photo_pasport(message):
    if message.photo:
        save_photo(message, 'passport_photo')
        message = bot.send_message(message.chat.id, f"Пришлите ваше фото с паспортом.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, send_self_photo_with_pasport)
    else:
        message = bot.send_message(message.chat.id, f"Пришлите фото паспорта.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, send_photo_pasport)


def send_self_photo_with_pasport(message):
    if message.photo:
        save_photo(message, 'selfie_passport_photo')
        message = bot.send_message(message.chat.id, f"Пришлите фото диплома об образовании психолога или трудовую книжку.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, send_photo_diploma)
    else:
        message = bot.send_message(message.chat.id, f"Пришлите ваше фото с паспортом.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, send_self_photo_with_pasport)


def send_photo_diploma(message):
    if message.photo:
        save_photo(message, 'diploma_photo')
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.send_message(chat_id=message.chat.id, text='Ждите решения администрации. Обычно на это уходит не больше 1 суток.')            
        db.update_verifed_psychologist(user_id=message.chat.id, value='under_consideration')
    else:
        message = bot.send_message(message.chat.id, f"Пришлите фото диплома об образовании психолога или трудовую книжку.", reply_markup=cancel_next_handlers()) 
        bot.register_next_step_handler(message, send_photo_diploma)
