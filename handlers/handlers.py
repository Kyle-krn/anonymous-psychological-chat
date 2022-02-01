from datetime import datetime, timedelta
from statistics import mean
import telebot
from database import db
from settings import TELEGRAM_TOKEN
from keyboard import *


bot = telebot.TeleBot(TELEGRAM_TOKEN)

####################################################################################################################################################
#Блок относится к преимум чату между пациентом и психологом, решить проблему с импортами
def stop_premium_dialog(user, companion, forced_stop=False):
    data = {
        'start': user['time_start_premium_dialog'],
        'end': datetime.utcnow().replace(microsecond=0),
        'delta': (datetime.utcnow().replace(microsecond=0) - user['time_start_premium_dialog']).total_seconds(),
        'psy': user['user_id'] if user['helper'] else user['companion_id'],
        'patient': user['companion_id'] if user['helper'] else user['user_id'],
        'price': user['about_me']['price'] if user['helper'] else companion['about_me']['price']
    }

    db.stop_premium_chat_db(user['user_id'], data)
    db.stop_premium_chat_db(user['companion_id'], data)
    
    psy_id = user['user_id'] if user['helper'] else user['companion_id']
    patient_id = user['companion_id'] if user['helper'] else user['user_id']

    if forced_stop:
        bot.send_message(chat_id=psy_id, text='<b>Ваш собеседник пропустил платный диалог, вы можете найти нового собеседника.</b>', parse_mode='HTML')
        bot.send_message(chat_id=patient_id, text='<b>Вы пропустили платную консультацию.</b>', parse_mode='HTML')
    else:
        bot.send_message(chat_id=psy_id, text='<b>Время консультации прошло, ваш собеседник может оплатить еще 1 час.</b>', parse_mode='HTML')
        bot.send_message(chat_id=patient_id, text='<b>Время консультации прошло, Вы можете оплатить еще 1 час.</b>', reply_markup=control_companion_verif(), parse_mode='HTML')
    
    if user['helper']:
        return push_data_premium_rating(companion) # Отправляем сообщение о том что можно оставить отзыв
    else:
        return push_data_premium_rating(user)


def check_premium_dialog(user):
    '''Функция сканирует сообщения, если у юзера активен платный диалог(В user['time_start_premium_dialog'] должна быть дата и время с началом 
    платного диалога, если None - значит нет платного диалога. Если диалог активен проверяет прошел ли час с начала платного диалога. Если час прошел,
    отрабатывает функции связанные с окончанием платного диалога, у психолога разблокируется функция пропуска, а пациент может оплатить еще 1 час и оставить отзыв
    '''
    if user['companion_id']:
        companion = db.get_user_by_id(user['companion_id'])
        if user['time_start_premium_dialog']:
            '''Если user психолог в премиум диалоге'''
            start_time = user['time_start_premium_dialog']
            if datetime.utcnow() > start_time + timedelta(hours=1):     # Если прошел час с момента старта премиум диалога
                return stop_premium_dialog(user, companion)


def stop_patient_premium_dialog(user):
    '''В случае если пациент сам хочет пропустить платный час'''
    companion = db.get_user_by_id(user['companion_id'])
    stop_premium_dialog(user, companion, forced_stop=True)


def send_view_premium_rating(user, rating_target='companion'):
    '''Отправлет пациенту отзывы и рейтинг психолога'''
    data_rating = user['premium_rating']
    int_rating = [item['rating'] for item in data_rating]
    if int_rating:
        mean_rating = f"{mean(int_rating):.1f}"
    else:
        mean_rating = 'Нет оценок'
    keyboard = None
    if [item['review'] for item in data_rating]:
        keyboard = start_view_review_keyboard()
        if rating_target == 'my_self':
            keyboard = start_view_review_keyboard(rating_target='my_self')
    if rating_target == 'companion':
        chat_id = user['companion_id']
    elif rating_target == 'my_self':
        chat_id = user['user_id']
    bot.send_message(chat_id=chat_id, text=f'Рейтинг психолога - {mean_rating}/5\nВсего {len(int_rating)} оценок.', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'view_my_self_premium_rating')
@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'view_companion_premium_rating')
def view_premium_review(call):
    '''Письменные отзывы о психологе, работает с пагинаацией, 1 страница - 1 отзыв'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1] == 'close':    return
    user = db.get_user_by_id(call.message.chat.id)
    if call.data.split('~')[0] == 'view_companion_premium_rating':
        user = db.get_user_by_id(user['companion_id'])
    data_rating = user['premium_rating']
    data_review = [(item['review'], item['rating']) for item in data_rating if item['review'] != '']
    page = int(call.data.split('~')[1])
    previous_page = page - 1
    next_page = page + 1
    if previous_page <= 0:
        previous_page = None
    if next_page > len(data_review):
        next_page = None
    keyboard = view_review_keyboard(page, previous_page, next_page)
    text = f'Оценка - {data_review[page-1][1]}\n\n' \
            f'Отзыв - {data_review[page-1][0]}'
    bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=keyboard)


def push_data_premium_rating(user):
    '''По хорошему эти функции в premium_chat перенести, хз че с импортом делать'''
    companion_user = db.get_user_by_id(user['companion_id'])
    message_premium_rating = bot.send_message(chat_id=user['user_id'], text='Нажмите на кнопку ниже что бы оставить отзыв о психологе.', reply_markup=premium_rating_keyboard())
    data = {
        'user_id': companion_user['user_id'],
        'message_id': message_premium_rating.message_id
    }
    db.push_value(user_id=user['user_id'], key='data_premium_rating_companion', value=data)
####################################################################################################################################################
def system_message_filter(message):
    '''В случае если пользователь пишет какое либо системное сообщение и у пользователя активный диалог, пересылает это сообщение
       собеседнику, а не отрабаывает опредленный хендлер'''
    user = db.get_or_create_user(message.chat)
    if user['companion_id']:
        return bot.send_message(chat_id=message.chat.id, text='<b>Ваше сообщение не отправлено, оно является системным и не может использоваться во время диалога!</b>', parse_mode='HTML')


def blocked_filter(message):
    '''Фильтр для заблокированных пользователей'''
    user = db.get_or_create_user(message.chat)
    if user['blocked'] is True:
        return bot.send_message(chat_id=message.chat.id, text='<u><b>Сообщение от администрации:</b></u>\n\nВы заблокированны', parse_mode='HTML')


@bot.message_handler(commands=['companion_rating'])
def view_command_rating(message):
    '''По команде отправлет рейтинг собеседника'''
    user = db.get_user_by_id(message.chat.id)
    if not user['companion_id']:    return
    companion_user = db.get_user_by_id(user['companion_id'])
    bot.send_message(chat_id=message.chat.id, text=f'Рейтинг вашего собеседника - {companion_user["rating"]}')


@bot.message_handler(commands=['start', 'help'])
def command_start(message):
    user = db.get_or_create_user(message.chat)
    if system_message_filter(message):  return
    if blocked_filter(message):    return
    if user['helper'] is None:
        bot.send_message(chat_id=message.chat.id, text='Выберите вашу роль:', reply_markup=helper_keyboard())
    return bot.send_message(chat_id=message.chat.id, text='Здесь вы найдете помощь.', reply_markup=main_keyboard())


def send_start_dialog_message(user):
    '''Отправляет сообщение о старте диалога'''
    db.push_date_in_start_dialog_time(user['user_id'])
    text_for_patient = '<b>Собеседник найден! Вы можете начать общение.</b>\n'
    keyboard = control_companion()
    if user['helper'] is True:
        text_for_patient += f'<b>Рейтинг вашего собеседника: {user["rating"]}.</b>\n\n'
        if user['verified_psychologist'] is True:
            keyboard = control_companion_verif()
            text_for_patient += '<b>Ваш собеседник верифицированный специалист ✔️</b>\n'
            about_me = user['about_me']
            text_for_patient += f'<b>Цена за 1 час консультации:</b> {about_me["price"]} руб.\n' \
                                f'<b>Имя:</b> {about_me["name"]}\n' \
                                f'<b>О психологе:</b> {about_me["about"]}'
            text_for_psy = f'<b>Ваша цена за 1 час консультации:</b> {about_me["price"]} руб.\n' \
                            '<b>После старта консультации, в течении часа нельзя будет пропустить собеседника.</b>'
            send_view_premium_rating(user)
            bot.send_message(chat_id=user['user_id'], text=text_for_psy, parse_mode='HTML')

    bot.send_message(chat_id=user['companion_id'], text=text_for_patient, reply_markup=keyboard, parse_mode='HTML')


def check_call_favorite_chat(message):
    user = db.get_user_by_id(message.chat.id)
    if user['user_id'] == user['call_favorite_chat']['user_id']:
        '''Если верифицированный психолог начинает поиск при активной заяке его бывшего пациента на приватный диалог
        просим сначала ответить на заявку.'''
        pasient = db.get_user_by_id(user['call_favorite_chat']['from'])
        text = f'<b>С вами хочет связаться пользователь #{pasient["user_id"]}. Хотите перейти в диалог с ним?\n\n'  \
                '❗❗❗Пожалуйста, не игнорируйте это сообщение, иначе другие пользователи не смогут прислать вам заявку на диалог.</b>'
        return bot.send_message(chat_id=message.chat.id, text=text, reply_markup=control_call_favorite_chat_keyboard(), parse_mode='HTML')
    elif user['user_id'] == user['call_favorite_chat']['from']:
        '''Если юзер отправил заявку на приватный диалог с избранным чатом'''
        text = f'<b>Вы ожидаете ответа от {user["call_favorite_chat"]["name"]}. Вы можете отменить запрос, нажав на кнопку ниже.</b>'
        return bot.send_message(chat_id=message.chat.id, text=text, reply_markup=cancel_call_favorite_chat_keyboard(), parse_mode='HTML')


@bot.message_handler(regexp="(^Найти собеседника($|\s🎯))")
def companion(message):
    '''Поиск собеседника'''
    if blocked_filter(message):    return
    user = db.get_or_create_user(message.chat)
    if user['call_favorite_chat']:
        return check_call_favorite_chat(message)
    if user['companion_id']:    return
    db.update_last_action_date(message.chat.id)
    if user['helper'] is None:
        return bot.send_message(chat_id=message.chat.id, text='Необходимо выбрать роль, для этого перейдите в настройки', reply_markup=main_keyboard())
    elif user['helper'] == True:
        text = '<u><b>Ваша роль - Я хочу помочь</b></u>'
    elif user['helper'] == False: 
        text = '<u><b>Ваша роль - Мне нужна помощь</b></u>'
    if user['helper'] is True and user['verified_psychologist'] is True and user['about_me']['price'] == 0:
        return bot.send_message(chat_id=message.chat.id, text='Заполните данные, для предоставления платных услуг.', reply_markup=about_me_keyboard())
    bot.send_message(message.chat.id, text=text, parse_mode='HTML')
    answer = db.search_companion(message.chat.id)
    
    user = db.get_or_create_user(message.chat)  # второй раз получаем юзера потому что в search_companion() юзер обновлен
    if answer:
        send_start_dialog_message(user)
        companion_user = db.get_user_by_id(user['companion_id'])
        send_start_dialog_message(companion_user)
        return
    return bot.send_message(chat_id=message.chat.id, text='Ожидание собеседника ⌛', reply_markup=control_companion(next=False))


@bot.message_handler(regexp='(^Следующий собеседник($|\s⏭))')
def next_companion(message):
    '''Отправляет сообщение с подтверждением о пропуске собеседника'''
    if blocked_filter(message):    return
    bot.delete_message(message.chat.id, message.message_id)
    user = db.get_user_by_id(message.chat.id)
    if user['helper'] is True and user['verified_psychologist'] is True and user['time_start_premium_dialog']:
        '''Не дает пропустить психологу собеседника если консультация оплачена'''
        premium_chat_time = datetime.utcnow().replace(microsecond=0) - user['time_start_premium_dialog']
        premium_chat_time = premium_chat_time.total_seconds()
        if premium_chat_time > (60*60):
            check_premium_dialog(user)
            bot.send_message(user['user_id'], 'Время консультации закончилось, вы можете пропустить собеседника.')
        else:
            return bot.send_message(user['user_id'], 'Вы не можете пропустить собеседника, время еще не вышло')
    db.update_last_action_date(message.chat.id)
    if not user['companion_id']:
        return companion(message)
    bot.send_message(chat_id=message.chat.id, text='Вы уверены что хотите пропустить собеседника?', reply_markup=yes_no_keyboard('next_companion'))    


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'next_companion')
def next_companion_inline(call):
    '''Следующий собеседник'''
    if blocked_filter(call.message):    return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_by_id(call.message.chat.id)
    db.update_last_action_date(call.message.chat.id)
    if not user['companion_id']:
        return companion(call.message)
    if call.data.split('~')[1] == 'yes':
        if user['helper'] is False and user['time_start_premium_dialog']:
            '''Если диалог завершает пациент с оплаченной консультацией, принудительно завершаем ее'''
            stop_patient_premium_dialog(user)
            bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, тем самым закончив платную консультацию.', reply_markup=main_keyboard())
        user = db.get_user_by_id(call.message.chat.id)
        db.push_date_in_end_dialog_time(call.message.chat.id) # Записываем дату и время конца диалога
        db.inc_value(user_id=call.message.chat.id, key='statistic.output_finish', value=1)
        db.push_date_in_end_dialog_time(user['companion_id']) # Записываем дату и время конца диалога
        db.inc_value(user_id=user['companion_id'], key='statistic.input_finish', value=1)
        rating_message(call.message)
        db.next_companion(call.message.chat.id)
        companion(call.message)


@bot.message_handler(regexp='(^Стоп($|\s⛔️))')
def stop_companion(message):
    '''Отправляет подтверждающее сообщение о пропуске собеседника и остановке поиска собеседника'''
    if blocked_filter(message):    return
    bot.delete_message(message.chat.id, message.message_id)
    user = db.get_user_by_id(message.chat.id)
    if user['helper'] is True and user['verified_psychologist'] is True and user['time_start_premium_dialog']:
        '''Не дает психологу завершить диалог если время консультации не прошло'''
        premium_chat_time =  datetime.utcnow().replace(microsecond=0) - user['time_start_premium_dialog']
        premium_chat_time = premium_chat_time.total_seconds()
        if premium_chat_time > (60*60):
            check_premium_dialog(user)
            bot.send_message(user['user_id'], 'Время консультации закончилось, вы можете пропустить собеседника.')
        else:
            return bot.send_message(user['user_id'], 'Вы не можете пропустить собеседника, время еще не вышло')
    if user['companion_id'] is None:
        db.cancel_search(message.chat.id)
        return bot.send_message(chat_id=message.chat.id, text='У вас нет активного диалога.', reply_markup=main_keyboard())
    db.update_last_action_date(message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='Вы уверены что хотите пропустить собеседника?', reply_markup=yes_no_keyboard('stop_companion'))  


def stop_companion(message):
    '''Завершает поиск собеседника'''
    user = db.get_user_by_id(message.chat.id)
    db.push_date_in_end_dialog_time(message.chat.id) # Записываем дату и время конца диалога
    db.inc_value(user_id=message.chat.id, key='statistic.output_finish', value=1)
    try:
        '''Если собеседник остановил бота или удалил телеграм'''
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        rating_message(message)
    except telebot.apihelper.ApiTelegramException:
        pass
    db.push_date_in_end_dialog_time(user['companion_id']) # Записываем дату и время конца диалога
    db.inc_value(user_id=user['companion_id'], key='statistic.input_finish', value=1)
    db.cancel_search(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'stop_companion')
def stop_search_handler(call):
    '''Завершает поиск собеседника'''
    if blocked_filter(call.message):    return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_or_create_user(call.message.chat)
    db.update_last_action_date(call.message.chat.id)
    if call.data.split('~')[1] == 'yes':
        if user['helper'] is False and user['time_start_premium_dialog']:
            '''Принудительно закрываем консультацию если она есть'''
            stop_patient_premium_dialog(user)
        if user['companion_id']:
            stop_companion(call.message)
        bot.send_message(chat_id=call.message.chat.id, text='Вы завершили диалог.', reply_markup=main_keyboard())


def rating_message(message):
    '''Соотносит message_id и user_id для выставления оценки правильного пользователя'''
    if blocked_filter(message):    return
    user = db.get_user_by_id(message.chat.id)
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
    '''Ставим собесденику оценку'''
    if blocked_filter(call.message):    return
    data_rating = db.get_data_rating_companion(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1] == "+":
        count = 1
    else:
        count = -2
        bot.send_message(chat_id=call.message.chat.id, text='<b>Желаете оставить жалобу на собеседника?</b>', reply_markup=complaint_keyboard(data_rating['user_id']), parse_mode='HTML')
    db.inc_rating(data_rating['user_id'], count)
    db.delete_data_rating_companion(call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Спасибо, ваш голос учтен!')


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_register_next_step_handler(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
