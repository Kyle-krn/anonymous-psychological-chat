from database import db
from settings import TELEGRAM_TOKEN
import telebot
from keyboard import *

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def command_start(message):
    user = db.get_or_create_user(message.chat)
    if db.cancel_search(message.chat.id):
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
    return bot.send_message(chat_id=message.chat.id, text='Привет', reply_markup=main_keyboard())



@bot.message_handler(regexp="^(Настройки)$")
def settings_user(message):
    return bot.send_message(chat_id=message.chat.id, text='Выберите свою роль', reply_markup=settings_keyboard())


@bot.message_handler(regexp="^(Я хочу помочь)$")
def i_want_help(message):
    db.helper(message.chat.id, True)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - Я хочу помочь', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Мне нужна помощь)$")
def i_need_help(message):
    db.helper(message.chat.id, False)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - мне нужна помощь', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Найти собеседника)$")
def companion(message):
    user = db.get_or_create_user(message.chat)
    if user['helper'] is None:
        return bot.send_message(chat_id=message.chat.id, text='Необходимо выбрать роль, для этого перейдите в настройки', reply_markup=main_keyboard())

    answer = db.search_companion(message.chat.id)

    user = db.get_or_create_user(message.chat)  # второй раз получаем юзера потому что в search_companion() юзер обновлен
    if answer:
        bot.send_message(chat_id=user['companion_id'], text='Собеседник найден! Вы можете начать общение.', reply_markup=control_companion())
        return bot.send_message(chat_id=message.chat.id, text='Собеседник найден, напиши привет!', reply_markup=control_companion())
    return bot.send_message(chat_id=message.chat.id, text='Идет поиск')


@bot.message_handler(regexp='^(Следующий собеседник)$')
def next_companion(message):
    bot.delete_message(message.chat.id, message.message_id)
    user = db.get_user_on_id(message.chat.id)
    if not user['companion_id']:
        return companion(message)
    bot.send_message(chat_id=message.chat.id, text='Вы уверены что хотите пропустить собеседника?', reply_markup=yes_no_keyboard('next_companion'))    


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'next_companion')
def next_companion_inline(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_on_id(call.message.chat.id)
    # if not user['companion_id']:
    #     return companion(call.message)
    if call.data.split('~')[1] == 'yes':
        user = db.get_user_on_id(call.message.chat.id)
        if user['companion_id']:
            bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
            rating_message_companion = bot.send_message(chat_id=user['companion_id'], text='Как вы оцените вашего собеседника?', reply_markup=rating_keyboard())
            rating_data_companion = {
                'user_id': call.message.chat.id,
                'message_id': rating_message_companion.message_id 
            }
            db.push_data_rating_companion(user['companion_id'], rating_data_companion)

            rating_message = bot.send_message(chat_id=call.message.chat.id, text='Как вы оцените вашего собеседника?', reply_markup=rating_keyboard())
            rating_data = {
                'user_id': user['companion_id'],
                'message_id': rating_message.message_id
            }
            db.push_data_rating_companion(call.message.chat.id, rating_data)

        # Продолжить здесь
    #     bot.delete_message(call.message.chat.id, call.message.message_id)
    #     answer = db.next_companion(call.message.chat.id)
    #     user = db.get_or_create_user(call.message.chat)
    #     if answer:
    #         bot.send_message(chat_id=user['companion_id'], text='Собеседник найден! Вы можете начать общение.', reply_markup=control_companion())
    #         return bot.send_message(chat_id=call.message.chat.id, text='Собеседник найден, напиши привет!', reply_markup=control_companion())
    #     return bot.send_message(chat_id=call.message.chat.id, text='Идет поиск')

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'rating')
def rating_handler(call):
    data_rating = db.get_data_rating_companion(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1] == "+":
        count = 1
    else:
        count = -2
    db.inc_rating(data_rating['user_id'], count)
    # db.delete_data_rating_companion(call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Спасибо, ваш голос учтен!')


# @bot.message_handler(regexp="^(Заблокировать собеседника)$")
# def block_companion(message): 
#     bot.delete_message(message.chat.id, message.message_id)
#     user = db.get_user_on_id(message.chat.id)
#     if not user['companion_id']:
#         return companion(message)
#     bot.send_message(chat_id=message.chat.id, text='Вы уверены что хотите заблокировать собеседника?', reply_markup=yes_no_keyboard('block_companion'))


# @bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'block_companion')
# def block_companion_inline(call):
#     if call.data.split('~')[1] == 'yes':
#         user = db.get_or_create_user(call.message.chat)
#         bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил диалог. Вы можете найти нового собеседника', reply_markup=main_keyboard())
#         db.block_companion(call.message.chat.id)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         return bot.send_message(chat_id=call.message.chat.id, text='Собеседник успешно заблокирован! Вы можете найти нового собеседника', reply_markup=main_keyboard())
#     else:
#         return bot.delete_message(call.message.chat.id, call.message.message_id)

# @bot.message_handler(regexp='^(Стоп)$')
# def stop_search_handler(message):
#     user = db.get_user_on_id(message.chat.id)
#     answer = db.cancel_search(message.chat.id)
#     if answer:
#         bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
#     return bot.send_message(chat_id=message.chat.id, text='Вы можете найти нового собеседника', reply_markup=main_keyboard())











@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'voice', 'sticker', 'video', 'video_note'])
def chat(message):
    user = db.get_or_create_user(message.chat)
    if message.text:
        return bot.send_message(chat_id=user['companion_id'], text=message.text)
    if message.photo:
        return bot.send_photo(user['companion_id'], message.photo[-1].file_id, message.caption)
    if message.video:
        return bot.send_video(user['companion_id'], message.video.file_id)
    if message.voice:
        return bot.send_voice(user['companion_id'], message.voice.file_id)
    if message.video_note:
        return bot.send_video_note(user['companion_id'], message.video_note.file_id)
    if message.sticker:
        return bot.send_sticker(user['companion_id'], message.sticker.file_id)

