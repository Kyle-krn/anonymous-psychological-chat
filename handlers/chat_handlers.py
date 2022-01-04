from handlers.handlers import bot, check_premium_dialog
from database import db
from pathlib import Path
import os
import telebot
from datetime import datetime, timedelta
from keyboard import *



@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'voice', 'sticker', 'video', 'video_note'])
def chat(message):
    '''Хендлер чата, если пользователь отправляет сообщение и у него есть собесденик, это сообщение пересылается собеседнику'''
    user = db.get_or_create_user(message.chat)
    db.update_last_action_date(message.chat.id)
    if not user['companion_id']:    return
    companion = db.get_user_by_id(user['companion_id'])
    check_premium_dialog(user)  # Прогоняем сообщение по функции проверки платного диалога, костыль, хз как по другому сделать
    db.update_count_message_dialog_time(message.chat.id)
    try:
        if message.text:
            return bot.send_message(chat_id=user['companion_id'], text="<u><b>Собеседник пишет:</b></u>\n\n"+message.text, parse_mode='HTML')
        elif message.photo:
            return bot.send_photo(user['companion_id'], message.photo[-1].file_id, caption='<u><b>Фото от собеседника:</b></u>\n\n' + (message.caption or ''), parse_mode='HTML')
        elif message.video:
            return bot.send_video(user['companion_id'], message.video.file_id, caption='<u><b>Видео от собеседника:</b></u>\n\n' + (message.caption or ''), parse_mode='HTML')
        elif message.voice:
            bot.send_message(chat_id=user['companion_id'], text='<u><b>Голосовое сообщение от собеседника:</b></u>', parse_mode='HTML')
            return bot.send_voice(user['companion_id'], message.voice.file_id)
        elif message.video_note:
            bot.send_message(chat_id=user['companion_id'], text='<u><b>Видео сообщение от собеседника:</b></u>', parse_mode='HTML')
            return bot.send_video_note(user['companion_id'], message.video_note.file_id)
        elif message.sticker:
            bot.send_message(chat_id=user['companion_id'], text='<u><b>Стикер от собеседника:</b></u>', parse_mode='HTML')
            return bot.send_sticker(user['companion_id'], message.sticker.file_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(e)