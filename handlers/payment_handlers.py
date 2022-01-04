from handlers.handlers import bot, system_message_filter, blocked_filter
from database import db
from utils import generate_alphanum_random_string
from qiwi import send_bill_api_qiwi, reject_bill_api_qiwi, check_bill_api_qiwi
from keyboard import *
import telebot 
from datetime import datetime, timedelta
from statistics import mean
##########################################################

########################################################################
 
@bot.message_handler(commands=['balance'])
@bot.message_handler(regexp="(^Пополнить счёт($|\s💳))")
def start_qiwi_order(message):
    try:
        return bot.send_message(message.chat.id, text='Выберите сумму пополнения:', reply_markup=choise_sum_qiwi())
    except Exception as e:
        print(e)

@bot.message_handler(commands=['my_balance'])
@bot.message_handler(regexp="(^Мой баланс($|\s💰))")
def my_balance(message):
    user = db.get_user_by_id(message.chat.id)
    text = f'На вашем счету --- {user["balance"]} руб.'
    keyboard = None
    if user['history_payment']:
        keyboard = confirm_hisory_payment()
    return bot.send_message(message.chat.id, text=f'На вашем счету --- {user["balance"]} руб.', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'history_balance')
def history_balance(call):
    try:
        if call.data.split('~')[1] == 'close':
            return bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user = db.get_user_by_id(call.message.chat.id)
        history_payment = user['history_payment']
        page = int(call.data.split('~')[1])
        count_documents = len(history_payment)
        offset = 10
        if len(history_payment) % offset:
            last_page = (count_documents // offset) + 1
        else:
            last_page = count_documents // offset
        next_page = page + 1
        if page == last_page:
            next_page = None
        previous_page = page - 1
        if page == 1:
            previous_page = None
        limit = offset * page
        skip = 0
        if page > 1:
            skip = offset *(page-1)
        history_payment = history_payment[skip:limit]
        keyboard = history_payment_keyboard(history_payment, previous_page, next_page, page)
        bot.send_message(call.message.chat.id, text=f'На вашем счету --- {user["balance"]} руб.', reply_markup=keyboard)
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'qiwi_order')
def create_qiwi_order(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user = db.get_user_by_id(call.message.chat.id)
        if call.data.split('~')[1] == 'cancel':    return
        if user['companion_id']:
            try:
                bot.send_message(call.message.chat.id, text='В режиме пополнения баланса, невозможно вести диалог с собеседником, все что будет написано до момента оплаты или отмены платежа собеседник не увидит')
                bot.send_message(user['companion_id'], text='Ваш собеседник пополняет счёт, он видит ваши сообщения, но ответить не может, подождите пожалуйста.')
            except telebot.apihelper.ApiTelegramException:
                pass
                
        coast = call.data.split('~')[1]
        
        coast = int(coast)
        billid = generate_alphanum_random_string(6)
        bill_data = send_bill_api_qiwi(billid, coast, call.message.chat.id)
        bill_date = bill_data[1]
        bill = bill_data[0]
        db.set_temp_payment(user_id=call.message.chat.id, coast=coast, billid=billid, date=bill_date, pay_url=bill['payUrl'])
        text = f'К оплате {coast} рублей + 2% комиссии QIWI.\n\n' \
               f'Оплата по ссылке: {bill["payUrl"]}\n\n' \
               f'После оплаты нажмите кнопку "Проверить платёж"\n\n' \
               f'Если вы передумали или нажали случайно, нажмите на кнопку "Отмена"\n\n' \
               'В случе не оплаты, платёж автоматически отменится через час после создания заяки.'
        message = bot.send_message(call.message.chat.id, text, reply_markup=order_keyboard()) 
        bot.register_next_step_handler(message, get_qiwi_order)
    except Exception as e:
        print(e) 

def get_qiwi_order(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id-1)
    user = db.get_user_by_id(message.chat.id)
    payment = user['temp_payment']
    if payment is None:
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        # keyboard = main_keyboard()
        # if user['companion_id']:
        #     keyboard = control_companion()
        #     companion_user = db.get_user_by_id(user["companion_id"])
        #     if companion_user['helper'] is True and companion_user['verified_psychologist'] is True:
        #         keyboard = control_companion_verif()
        return bot.send_message(text='Ваш заказ был удалён.')
    text = f'К оплате {payment["coast"]} рублей + 2% комиссии QIWI.\n\n' \
           f'Оплата по ссылке: {payment["pay_url"]}\n\n' \
           f'После оплаты нажмите кнопку "Проверить платёж"\n\n' \
           f'Если вы передумали или нажали случайно, нажмите на кнопку "Отмена"\n\n' \
           'В случе не оплаты, платёж автоматически отменится через час после создания заяки.'
    message = bot.send_message(message.chat.id, text, reply_markup=order_keyboard()) 
    bot.register_next_step_handler(message, get_qiwi_order)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_payment')
def cancel_qiwi_order(call):
    bot.send_message(call.message.chat.id, text='Вы уверены что хотите отменить платёж?', reply_markup=yes_no_keyboard('reject'))

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'reject')
def reject_bill_qiwi(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if call.data.split('~')[1] == 'yes':
            bot.delete_message(call.message.chat.id, call.message.message_id-1)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            user = db.get_user_by_id(call.message.chat.id)
            payment = user['temp_payment']
            reject_bill_api_qiwi(payment['billid'])
            # db.delete_temp_payment(call.message.chat.id)
            db.set_value(user_id=call.message.chat.id, key='temp_payment', value=None)
            # keyboard = main_keyboard()
            # if user['companion_id']:
            #     keyboard = control_companion()
            #     companion_user = db.get_user_by_id(user["companion_id"])
            #     if companion_user['helper'] is True and companion_user['verified_psychologist'] is True:
            #         keyboard = control_companion_verif()
            bot.send_message(call.message.chat.id, text='Ваш платёж был отменён.')
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'check_payment')
def check_bill_qiwi(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user = db.get_user_by_id(call.message.chat.id)
        payment = user['temp_payment']
        answer = check_bill_api_qiwi(payment['billid'])
        companion = None
        if user['companion_id']:
            companion = db.get_user_by_id(user['companion_id'])
        text = ''
        if answer['status']['value'] == 'EXPIRED':
            # db.delete_temp_payment(call.message.chat.id)
            db.set_value(user_id=call.message.chat.id, key='temp_payment', value=None)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            # keyboard = main_keyboard()
            # if companion:
            #     keyboard = control_companion()
            #     if companion['helper'] is True and companion['verified_psychologist'] is True:
            #         keyboard = control_companion_verif()
                
            return bot.send_message(text='Ваша заявка на пополнение счёта удалена из за истечения времени ссылки')
        elif answer['status']['value'] == 'WAITING':
            text = f'Счёт не оплачен, если вы только что оплатили, подождите 1 минуту и попробуйте провермть платёж снова \n\n\n' \
            f'К оплате {payment["coast"]} рублей + 2% комиссии QIWI.\n\n' \
            f'Оплата по ссылке: {payment["pay_url"]}\n\n' \
            f'После оплаты нажмите кнопку "Проверить платёж"\n\n' \
            f'Если вы передумали или нажали случайно, нажмите на кнопку "Отмена"\n\n' \
            'В случе не оплаты, платёж автоматически отменится через час после создания заяки.'
            message = bot.send_message(call.message.chat.id, text, reply_markup=order_keyboard()) 
            return bot.register_next_step_handler(message, get_qiwi_order)
        elif answer['status']['value'] == 'PAID':
            # db.push_paid_payment(call.message.chat.id, payment)
            db.push_value(user_id=call.message.chat.id, key='history_payment', value=payment)
            # db.inc_balance(call.message.chat.id, payment['coast'])
            db.inc_value(user_id=call.message.chat.id, key='balance', value=payment['coast'])
            user = db.get_user_by_id(call.message.chat.id)
            # db.delete_temp_payment(call.message.chat.id)
            db.set_value(user_id=call.message.chat.id, key='temp_payment', value=None)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            text = f'Ваш счёт был успешно оплачен, на ваш баланс зачисленно {payment["coast"]} рублей.\n\nВаш баланс - {user["balance"]} рублей.'
            # keyboard = main_keyboard()
            # if companion['companion_id']:
            #     keyboard = control_companion()
            #     if companion['helper'] is True and companion['verified_psychologist'] is True:
            #         keyboard = control_companion_verif()
            bot.send_message(call.message.chat.id, text)
    except Exception as e:
        print(e)




