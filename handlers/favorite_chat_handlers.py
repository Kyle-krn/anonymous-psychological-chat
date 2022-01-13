from handlers.handlers import bot, stop_companion, send_start_dialog_message
from database import db
from keyboard import *

@bot.message_handler(regexp='(^Избранные чаты($|\s⭐))')
def favorite_chat_handler(message):
    '''Отдает список избранных чатов'''
    user = db.get_user_by_id(message.chat.id)
    if user['companion_id']:    return
    if not user['favorite_chat']:    return
    if user['call_favorite_chat']:
        text = f'<b>Вы ожидаете ответа от {user["call_favorite_chat"]["name"]}. Вы можете отменить запрос, нажав на кнопку ниже.</b>'
        return bot.send_message(chat_id=message.chat.id, text=text, reply_markup=cancel_call_favorite_chat_keyboard(), parse_mode='HTML')
    bot.send_message(chat_id=message.chat.id, text='<b>С кем вы хотите связаться?</b>', reply_markup=favorite_chat_keyboard(user['favorite_chat']), parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'call_favorite_chat')
def call_favorite_chat_handler(call):
    '''Вызываем избранного психолога'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_by_id(call.message.chat.id)
    call_for = int(call.data.split('~')[1])         # id психолога
    psy_user = db.get_user_by_id(call_for)
    if psy_user["call_favorite_chat"]:
        return bot.send_message(user_id=call.message.chat.id, text='<b>Пользователь ещё не ответил на прошлый вызов. Повторите позже.</b>', parse_mode='HTML')
    if psy_user['time_start_premium_dialog']:
        return bot.send_message(user_id=call.message.chat.id, text='<b>Пользователь ведёт платную консультацию. Повторите позже.</b>', parse_mode='HTML')
    psy_data = db.get_favorite_chat(call.message.chat.id, call_for)
    data = {'name': psy_data["name"],
            'user_id': call_for,
            'from': call.message.chat.id}
    db.set_value(user_id=call.message.chat.id, key='call_favorite_chat', value=data)
    db.set_value(user_id=call_for, key='call_favorite_chat', value=data)
    text = f'<b>С вами хочет связаться пользователь #{call.message.chat.id}. Хотите перейти в диалог с ним?\n\n'  \
            '❗❗❗Пожалуйста, не игнорируйте это сообщение, иначе другие пользователи не смогут прислать вам заявку на диалог.\n'  \
            'Если вы сейчас находитесь в диалоге, после согласия на приватный диалог, этот чат завершится. </b>'
    bot.send_message(chat_id=call_for, text=text, reply_markup=control_call_favorite_chat_keyboard(), parse_mode='HTML')
    text=f'<b>Заяка на диалог успешно отправлена, к сожалению вы не cможете найти нового собеседника пока заявка ожидает '  \
            'ответа. Если вам надоело ждать и вы хотите общаться, вы можете так же нажать на кнопку "Избранные чаты ⭐" и отменить '  \
            'свою заявку самостоятельно.</b>'
    bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='HTML')



@bot.callback_query_handler(func=lambda call: call.data == 'cancel_call_favorite_chat')
def cancel_call_favorite_chat_handler(call):
    '''Отмена заявки приватого диалога (Может вызвать и пациент и психолог)'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_by_id(call.message.chat.id)
    if not user['call_favorite_chat']:    return
    psy_id = user['call_favorite_chat']['user_id']
    if user['user_id'] == psy_id:
        '''Если диалог отклоняет психолог'''
        text = f'<b>{user["call_favorite_chat"]["name"]} отклонил диалог.</b>'
        bot.send_message(chat_id=user['call_favorite_chat']['from'], text=text, parse_mode='HTML')
    elif user['user_id'] == user['call_favorite_chat']['from']:
        '''Если диалог отклоняет пациент'''
        text = f'<b>Пользователь #{user["user_id"]} отменил свою заявку на приватный чат с вами.</b>'
        bot.send_message(chat_id=user['call_favorite_chat']['user_id'], text=text, parse_mode='HTML')
    db.set_value(user_id=user['call_favorite_chat']['from'], key='call_favorite_chat', value=None)
    db.set_value(user_id=user['call_favorite_chat']['user_id'], key='call_favorite_chat', value=None)
    bot.send_message(chat_id=call.message.chat.id, text='<b>Успешно!</b>', parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'start_favorite_chat')
def start_call_favorite_chat_handler(call):
    '''Связываем 2ух юзеров после принятия психолога'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_by_id(call.message.chat.id)
    data_favorite_chat = user['call_favorite_chat']
    if user['companion_id']:
        '''Если психолог находится в диалоге, заканчиваем его'''
        stop_companion(call.message)
    db.set_value(user_id=call.message.chat.id, key='call_favorite_chat', value=None)
    db.set_value(user_id=data_favorite_chat['from'], key='call_favorite_chat', value=None)
    db.set_value(user_id=call.message.chat.id, key='companion_id', value=data_favorite_chat['from'])
    db.set_value(user_id=data_favorite_chat['from'], key='companion_id', value=call.message.chat.id)
    user = db.get_user_by_id(call.message.chat.id)
    companion_user = db.get_user_by_id(data_favorite_chat['from'])
    send_start_dialog_message(user)
    send_start_dialog_message(companion_user)
    return

