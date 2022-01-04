from database import db
from keyboard import *
from handlers.handlers import bot, system_message_filter, blocked_filter, send_view_premium_rating
from datetime import datetime
from statistics import mean

 
@bot.message_handler(regexp='(^Начать консультацию($|\s📒))')
def confirm_premium_chat(message):
    user = db.get_user_by_id(message.chat.id)
    if blocked_filter(message):    return
    if not user['companion_id']:    return
    companion_user = db.get_user_by_id(user['companion_id'])
    if companion_user['helper'] is not True:    return
    if companion_user['verified_psychologist'] is not True:    return
    text = f'Цена за 1 час консультации --> {companion_user["about_me"]["price"]} рублей\n' \
            'Вы уверены что хотите оплатить этот час?\n' \
            'После оплаты психолог не сможет в течении часа пропустить этот чат, это можете сделать только вы.'
    bot.send_message(message.chat.id, text=text, reply_markup=yes_no_keyboard('start_premium_chat'))

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'start_premium_chat')
def start_premium_chat(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if call.data.split('~')[1] == 'yes':
            user = db.get_user_by_id(call.message.chat.id)
            companion_user = db.get_user_by_id(user['companion_id'])
            price = companion_user["about_me"]["price"]
            if price > user['balance']:
                text = f'Стоимость 1 часа консультации {price} рублей.\n' \
                    f'Ваш баланс {user["balance"]} рубля.\n' \
                    f'Недостаточно средств для начала консультации, вы можете пополнить баланс прямо из диалога.' 
                return bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=choise_sum_qiwi(price-user['balance']))
            date =  datetime.utcnow().replace(microsecond=0)
            data = {
                'status': 'consumption',
                'date': date,
                'from': user['user_id'],
                'coast': price,
                'for': companion_user['user_id']
            }
            
            db.inc_value(user_id=call.message.chat.id, key='balance', value=-price)
            db.push_value(user_id=call.message.chat.id, key='history_payment', value=data)
            db.set_value(user_id=call.message.chat.id, key='time_start_premium_dialog', value=date)
            data['status'] = 'income'
            db.inc_value(user_id=companion_user["user_id"], key='balance', value=price)
            db.push_value(user_id=companion_user["user_id"], key='history_payment', value=data)
            db.set_value(user_id=companion_user["user_id"], key='time_start_premium_dialog', value=date)
            user = db.get_user_by_id(call.message.chat.id)
            companion_user = db.get_user_by_id(user['companion_id'])
            bot.send_message(chat_id=user['user_id'], text=f'Вы успешно оплатили 1 час консультации, на вашем балансе {user["balance"]} рублей.\n В течении 1го часа психолог не сможет пропустить диалог, но это можете вы.', reply_markup=control_companion())
            bot.send_message(chat_id=companion_user['user_id'], text=f'Собеседник успешно оплатил 1 час консультации, на вашем балансе {companion_user["balance"]} рублей.\n В течении 1го часа Вы не можете пропустить диалог, но это может сделать ваш собеседник.')
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'premium_rating')
def premium_rating_handler(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        rating_data = db.get_data_premium_rating_companion(call.message.chat.id, call.message.message_id)
        db.delete_data_premium_rating_companion(call.message.chat.id, call.message.message_id)
        review_for = rating_data['user_id']
        rating = int(call.data.split('~')[1])
        text = f'Ваша оценка - {rating}\nВы можете оставить отзыв о психологе, просто напишите его ниже.\nЕсли вы не хотите оставлять отзыв, просто нажмите кнопку - "Закончить".'
        message = bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=stop_review_keyboard(review_for=review_for, rating=rating))
        bot.register_next_step_handler(message, review_psy, rating, review_for)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['companion_premium_rating'])
def view_command_premium_rating(message):
    '''По команде отправляет рейтинг и отзывы, если его собеседник вериф. психолог'''
    user = db.get_user_by_id(message.chat.id)
    if not user['companion_id']:    return
    companion_user = db.get_user_by_id(user['companion_id'])
    if companion_user['helper'] is True and companion_user['verified_psychologist'] is True:
        send_view_premium_rating(companion_user)


def review_psy(message, rating, review_for):
    try:
        if message.text:
            review = message.text
            data = {
                'rating': rating,
                'review': review,
                'datetime': datetime.utcnow(),
                'from': message.chat.id
            }
            db.push_value(user_id=review_for, key='premium_rating', value=data)
            bot.send_message(chat_id=message.chat.id, text='Спасибо за ваш отзыв!')
        else:
            text = 'Я понимаю только текст 🤷\nПопробуйте еще раз.'
            message = bot.send_message(chat_id=message.chat.id, text=text)
            bot.register_next_step_handler(message, review_psy, rating, review_for)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'stop_premium_rating')
def send_rating_without_review(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        review_for = int(call.data.split('~')[1])
        rating = int(call.data.split('~')[2])
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        data = {
                    'rating': rating,
                    'review': '',
                    'datetime': datetime.utcnow(),
                    'from': call.message.chat.id
                }
        db.push_value(user_id=review_for, key='premium_rating', value=data)
        bot.send_message(chat_id=call.message.chat.id, text='Спасибо за ваш отзыв!')
    except Exception as e:
        print(e)



    