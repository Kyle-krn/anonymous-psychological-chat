from handlers.handlers import bot
from database import db
import os
from pathlib import Path

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'voice', 'sticker', 'video', 'video_note'])
def chat(message):
    user = db.get_or_create_user(message.chat)
    db.update_last_action_date(message.chat.id)
    if not user['companion_id']:    return
    db.update_count_message_dialog_time(message.chat.id)
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