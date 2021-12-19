from database import db
from settings import TELEGRAM_TOKEN
import telebot
from keyboard import *
from datetime import datetime
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def system_message_filter(message):
    '''В случае если пользователь пишет какое либо системное сообщение и у пользователя активный диалог, пересылает это сообщение
       собеседнику, а не отрабаывает опредленный хендлер'''
    user = db.get_or_create_user(message.chat)
    if user['companion_id']:
        return chat(message)

@bot.message_handler(commands=['start', 'help'])
def command_start(message):
    user = db.get_or_create_user(message.chat)
    db.update_last_action_date(message.chat.id)
    if user['companion_id']:
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        rating_message(message)
        db.cancel_search(message.chat.id)
    return bot.send_message(chat_id=message.chat.id, text='Это приветственное сообщение бота', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Найти собеседника)$")
def companion(message):
    if system_message_filter(message):  return
    user = db.get_or_create_user(message.chat)
    db.update_last_action_date(message.chat.id)
    if user['helper'] is None:
        return bot.send_message(chat_id=message.chat.id, text='Необходимо выбрать роль, для этого перейдите в настройки', reply_markup=main_keyboard())

    answer = db.search_companion(message.chat.id)

    user = db.get_or_create_user(message.chat)  # второй раз получаем юзера потому что в search_companion() юзер обновлен
    if answer:
        bot.send_message(chat_id=user['companion_id'], text=f'Собеседник найден! Рейтинг вашего собеседника: {user["rating"]}. Вы можете начать общение.', reply_markup=control_companion())
        companion_user = db.get_user_on_id(user['companion_id'])
        return bot.send_message(chat_id=message.chat.id, text=f'Собеседник найден! Рейтинг вашего собеседника: {companion_user["rating"]}. Вы можете начать общение.', reply_markup=control_companion())
    return bot.send_message(chat_id=message.chat.id, text='Идет поиск', reply_markup=control_companion(next=False))


@bot.message_handler(regexp='^(Следующий собеседник)$')
def next_companion(message):
    bot.delete_message(message.chat.id, message.message_id)
    user = db.get_user_on_id(message.chat.id)
    db.update_last_action_date(message.chat.id)
    if not user['companion_id']:
        return companion(message)
    bot.send_message(chat_id=message.chat.id, text='Вы уверены что хотите пропустить собеседника?', reply_markup=yes_no_keyboard('next_companion'))    


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'next_companion')
def next_companion_inline(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_on_id(call.message.chat.id)
    db.update_last_action_date(call.message.chat.id)
    if not user['companion_id']:
        return companion(call.message)
    if call.data.split('~')[1] == 'yes':
        user = db.get_user_on_id(call.message.chat.id)
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        rating_message(call.message)
        db.next_companion(call.message.chat.id)
        companion(call.message)


def rating_message(message):
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
    data_rating = db.get_data_rating_companion(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1] == "+":
        count = 1
    else:
        count = -2
    db.inc_rating(data_rating['user_id'], count)
    db.delete_data_rating_companion(call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Спасибо, ваш голос учтен!')


@bot.message_handler(regexp='^(Стоп)$')
def stop_search_handler(message):
    user = db.get_or_create_user(message.chat)
    db.update_last_action_date(message.chat.id)
    if user['companion_id']:
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        rating_message(message)
        db.cancel_search(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='Вы завершили диалог.', reply_markup=main_keyboard())





