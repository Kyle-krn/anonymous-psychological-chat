from database import db
from settings import TELEGRAM_TOKEN
import telebot
from keyboard import *

bot = telebot.TeleBot(TELEGRAM_TOKEN)

system_message = ('Настройки', 'Я хочу помочь', 'Мне нужна помощь')


def system_message_filter(message):
    '''В случае если пользователь пишет какое либо системное сообщение и у пользователя активный диалог, пересылает это сообщение
       собеседнику, а не отрабаывает опредленный хендлер'''
    user = db.get_or_create_user(message.chat)
    if user['companion_id']:
        return chat(message)

@bot.message_handler(commands=['start', 'help'])
def command_start(message):
    user = db.get_or_create_user(message.chat)
    if user['companion_id']:
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        rating_message(message)
        db.cancel_search(message.chat.id)
    return bot.send_message(chat_id=message.chat.id, text='Это приветственное сообщение бота', reply_markup=main_keyboard())



@bot.message_handler(regexp="^(Настройки)$")
def settings_user(message):
    if system_message_filter(message):  return
    return bot.send_message(chat_id=message.chat.id, text='Выберите свою роль', reply_markup=settings_keyboard())


@bot.message_handler(regexp="^(Я хочу помочь)$")
def i_want_help(message):
    if system_message_filter(message):  return
    db.helper(message.chat.id, True)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - Я хочу помочь', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Мне нужна помощь)$")
def i_need_help(message):
    if system_message_filter(message):  return
    db.helper(message.chat.id, False)
    bot.send_message(chat_id=message.chat.id, text='Ваша роль - мне нужна помощь', reply_markup=main_keyboard())

@bot.message_handler(regexp="^(Мой рейтинг)$")
def my_rating(message):
    if system_message_filter(message):  return
    user = db.get_user_on_id(message.chat.id)
    return bot.send_message(chat_id=message.chat.id, text=f'Ваш рейтинг: {user["rating"]}.')


@bot.message_handler(regexp="^(Найти собеседника)$")
def companion(message):
    if system_message_filter(message):  return
    user = db.get_or_create_user(message.chat)
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
    if not user['companion_id']:
        return companion(message)
    bot.send_message(chat_id=message.chat.id, text='Вы уверены что хотите пропустить собеседника?', reply_markup=yes_no_keyboard('next_companion'))    


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'next_companion')
def next_companion_inline(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_on_id(call.message.chat.id)
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
    if user['companion_id']:
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        rating_message(message)
        db.cancel_search(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='Вы завершили диалог.', reply_markup=main_keyboard())


@bot.message_handler(regexp="^(Служба поддержки)$")
def support_handler(message):
    if system_message_filter(message):  return
    bot.send_message(chat_id=message.chat.id, text="Если вы столкнулись с проблемой или ошибкой в боте, дайте нам знать.\nВы можете обратиться к нашей службе поддержки: @kyle_krn",
                     reply_markup=support_keyboard())


@bot.message_handler(regexp="^(Назад)$")
def back_handler(message):
    if system_message_filter(message):  return
    bot.send_message(chat_id=message.chat.id, text='👋', reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'voice', 'sticker', 'video', 'video_note'])
def chat(message):
    user = db.get_or_create_user(message.chat)
    if not user['companion_id']:
        return
    if message.text:
        # return bot.send_message(chat_id=user['companion_id'], text=message.text)
        return bot.send_message(chat_id=user['companion_id'], text="<u><b>Собеседник пишет:</b></u>\n\n"+message.text, parse_mode='HTML')
    elif message.photo:
        # return bot.send_photo(user['companion_id'], message.photo[-1].file_id, message.caption)
        return bot.send_photo(user['companion_id'], message.photo[-1].file_id, caption='<u><b>Фото от собеседника:</b></u>\n\n' + (message.caption or ''), parse_mode='HTML')
    elif message.video:
        # return bot.send_video(user['companion_id'], message.video.file_id, caption=(message.caption or ''))
        return bot.send_video(user['companion_id'], message.video.file_id, caption='<u><b>Видео от собеседника:</b></u>\n\n' + (message.caption or ''), parse_mode='HTML')
    elif message.voice:
        # return bot.send_voice(user['companion_id'], message.voice.file_id)
        bot.send_message(chat_id=user['companion_id'], text='<u><b>Голосовое сообщение от собеседника:</b></u>', parse_mode='HTML')
        return bot.send_voice(user['companion_id'], message.voice.file_id)
    elif message.video_note:
        # return bot.send_video_note(user['companion_id'], message.video_note.file_id)
        bot.send_message(chat_id=user['companion_id'], text='<u><b>Видео сообщение от собеседника:</b></u>', parse_mode='HTML')
        return bot.send_video_note(user['companion_id'], message.video_note.file_id)
    elif message.sticker:
        # return bot.send_sticker(user['companion_id'], message.sticker.file_id)
        bot.send_message(chat_id=user['companion_id'], text='<u><b>Стикер от собеседника:</b></u>', parse_mode='HTML')
        return bot.send_sticker(user['companion_id'], message.sticker.file_id)
