import telebot 
from datetime import datetime
from .handlers import bot, system_message_filter, blocked_filter
from database import db
from utils import generate_alphanum_random_string
from qiwi import send_bill_api_qiwi, reject_bill_api_qiwi, check_bill_api_qiwi
from keyboard import *


@bot.message_handler(commands=['my_balance'])
@bot.message_handler(regexp="(^Мой баланс($|\s💰))")
def my_balance(message):
    '''Отображает остаток на счету'''
    user = db.get_user_by_id(message.chat.id)
    text = f'На вашем счету --- {user["balance"]} руб.'
    keyboard = None
    if user['history_payment']:
        keyboard = confirm_hisory_payment()
    return bot.send_message(message.chat.id, text=f'На вашем счету --- {user["balance"]} руб.', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'history_balance')
def history_balance(call):
    '''История баланса'''
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


@bot.message_handler(commands=['balance'])
@bot.message_handler(regexp="(^Пополнить счёт($|\s💳))")
def start_qiwi_order(message):
    return bot.send_message(message.chat.id, text='Выберите сумму пополнения:', reply_markup=choise_sum_qiwi())


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'qiwi_order')
def create_qiwi_order(call):
    '''Создает платежку и отдает пользователю сообщение которое он может скипнуть только нажав на кнопку "Отмена"'''
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
    coast_with_commission = int(coast + (coast/100 * 20))
    billid = generate_alphanum_random_string(6)
    bill_data = send_bill_api_qiwi(billid, coast_with_commission, call.message.chat.id)
    bill_date = bill_data[1]
    bill = bill_data[0]
    data = {
                'user_id': call.message.chat.id,
                'status': 'replenishment',
                'date': bill_date,
                'billid': billid,
                'coast_with_commission': coast_with_commission,
                'coast': coast,
                'pay_url': bill['payUrl']
            }
    
    db.set_value(user_id=call.message.chat.id, key='temp_payment', value=data)
    text = f'К оплате {coast_with_commission} рублей.\n\n' \
            f'Оплата по ссылке: {bill["payUrl"]}\n\n' \
            f'После оплаты нажмите кнопку "Проверить платёж"\n\n' \
            f'Если вы передумали или нажали случайно, нажмите на кнопку "Отмена"\n\n' \
            'В случе не оплаты, платёж автоматически отменится через час после создания заяки.'
    message = bot.send_message(call.message.chat.id, text, reply_markup=order_keyboard()) 
    bot.register_next_step_handler(message, get_qiwi_order)         # Для того что бы другие хендлеры не работали во время оплаты кидаем юзера в цикл
    
def get_qiwi_order(message):
    '''Отправляет сообщение с ссылкой для оплаты (сообщение блокируется, может быть отменено по кнопке "Отмена")'''
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id-1)
    user = db.get_user_by_id(message.chat.id)
    payment = user['temp_payment']
    if payment is None:
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        return bot.send_message(text='Ваш заказ был удалён.')
    text = f'К оплате {payment["coast_with_commission"]} рублей.\n\n' \
           f'Оплата по ссылке: {payment["pay_url"]}\n\n' \
           f'После оплаты нажмите кнопку "Проверить платёж"\n\n' \
           f'Если вы передумали или нажали случайно, нажмите на кнопку "Отмена"\n\n' \
           'В случе не оплаты, платёж автоматически отменится через час после создания заяки.'
    message = bot.send_message(message.chat.id, text, reply_markup=order_keyboard()) 
    bot.register_next_step_handler(message, get_qiwi_order)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_payment')
def cancel_qiwi_order(call):
    '''Отмена платежа(подтверждающее сообщение)'''
    bot.send_message(call.message.chat.id, text='Вы уверены что хотите отменить платёж?', reply_markup=yes_no_keyboard('reject'))

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'reject')
def reject_bill_qiwi(call):
    '''Отмена платежа'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data.split('~')[1] == 'yes':
        bot.delete_message(call.message.chat.id, call.message.message_id-1)
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        user = db.get_user_by_id(call.message.chat.id)
        payment = user['temp_payment']
        reject_bill_api_qiwi(payment['billid'])
        db.set_value(user_id=call.message.chat.id, key='temp_payment', value=None)
        bot.send_message(call.message.chat.id, text='Ваш платёж был отменён.')


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'check_payment')
def check_bill_qiwi(call):
    '''Проверить платеж'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_by_id(call.message.chat.id)
    payment = user['temp_payment']
    answer = check_bill_api_qiwi(payment['billid'])
    companion = None
    if user['companion_id']:
        companion = db.get_user_by_id(user['companion_id'])
    text = ''
    if answer['status']['value'] == 'EXPIRED':
        '''Заявка истекла по времени'''
        db.set_value(user_id=call.message.chat.id, key='temp_payment', value=None)
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        return bot.send_message(text='Ваша заявка на пополнение счёта удалена из за истечения времени ссылки')

    elif answer['status']['value'] == 'WAITING':
        '''Заявка ожидает платежа'''
        text = f'Счёт не оплачен, если вы только что оплатили, подождите 1 минуту и попробуйте провермть платёж снова \n\n\n' \
        f'К оплате {payment["coast_with_commission"]} рублей + 2% комиссии QIWI.\n\n' \
        f'Оплата по ссылке: {payment["pay_url"]}\n\n' \
        f'После оплаты нажмите кнопку "Проверить платёж"\n\n' \
        f'Если вы передумали или нажали случайно, нажмите на кнопку "Отмена"\n\n' \
        'В случе не оплаты, платёж автоматически отменится через час после создания заяки.'
        message = bot.send_message(call.message.chat.id, text, reply_markup=order_keyboard()) 
        return bot.register_next_step_handler(message, get_qiwi_order)
    elif answer['status']['value'] == 'PAID':
        '''Заявка оплачена'''
        db.push_value(user_id=call.message.chat.id, key='history_payment', value=payment)
        db.inc_value(user_id=call.message.chat.id, key='balance', value=payment['coast'])
        user = db.get_user_by_id(call.message.chat.id)
        db.set_value(user_id=call.message.chat.id, key='temp_payment', value=None)
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        text = f'Ваш счёт был успешно оплачен, на ваш баланс зачисленно {payment["coast"]} рублей.\n\nВаш баланс - {user["balance"]} рублей.'
        bot.send_message(call.message.chat.id, text)



######################################################################


@bot.message_handler(regexp="(^Вывод денег($|\s💸))")
def transfer_money_start(message):
    '''Вывод средств с баланса для верифицированных психологов'''
    user = db.get_user_by_id(message.chat.id)
    system_message_filter(message)
    blocked_filter(message)
    if user['verified_psychologist'] is not True:
        return
    if user['temp_transfer_money']:
        return bot.send_message(chat_id=message.chat.id, text='<b>Ваша прошлая заявка ещё не обработана, вывод будет доступен после обработки прошлой заявки.</b>', parse_mode='HTML')
    text = f"<b>Доступно для вывода {user['balance']} руб.\nВнимание! Вывод средств выполняется на QIWI кошелек и обрабатывается в ручном режиме, деньги на ваш кошелёк поступят " \
            "в течении суток после оформления выплаты. Пожалуйста, вводите номер телефона только с привязанным QIWI кошельком!\nМаксимальная сумма для единовременного вывода - 10000 р.</b>"
    message = bot.send_message(message.chat.id, text=text, reply_markup=transfer_money_keyboard(), parse_mode='HTML') 



@bot.callback_query_handler(func=lambda call: call.data == 'transfer_money')
def transfer_money_handler(call):
    '''Предлагаем ввести сумму вывода'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = db.get_user_by_id(call.message.chat.id)
    message = bot.send_message(call.message.chat.id, text=f'<b>На вашем счету {user["balance"]} руб.\nВведите сумму вывода.</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML') 
    bot.register_next_step_handler(message, transfer_money_count)


def transfer_money_count(message):
    '''Принимаем сумму и просим ввести номер киви кошелька'''
    try:
        money = int(message.text)
        user = db.get_user_by_id(message.chat.id)
        if money <= 0 or money > user['balance'] or money > 10000:
            message = bot.send_message(message.chat.id, text=f'<b>На вашем счету {user["balance"]} руб.\nВведите сумму вывода. (Только цифры, максимум 10000р.)</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML') 
            return bot.register_next_step_handler(message, transfer_money_count)
        
        message = bot.send_message(message.chat.id, text=f'<b>Введите номер QIWI кошелька в формате 79001112233.</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML') 
        bot.register_next_step_handler(message, qiwi_account_transfer, money)
    except (ValueError, TypeError) as e:
        message = bot.send_message(message.chat.id, text=f'<b>На вашем счету {user["balance"]} руб.\nВведите сумму вывода.</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML') 
        bot.register_next_step_handler(message, transfer_money_count)


def qiwi_account_transfer(message, money):
    '''Принимаем киви кошелек и отдаем админу на обработку'''
    try:
        qiwi_account = int(message.text)
        if len(str(qiwi_account)) != 11:
            message = bot.send_message(message.chat.id, text=f'<b>Введите номер QIWI кошелька в формате 79001112233.(Без + и 11 цифр)</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML') 
            return bot.register_next_step_handler(message, qiwi_account_transfer, money)
        data = {
            'user_id': message.chat.id,
            'coast': money,
            'qiwi_account': qiwi_account,
            'date': datetime.utcnow().replace(microsecond=0)
        }
        db.inc_value(user_id=message.chat.id, key='balance', value=-money)
        db.set_value(user_id=message.chat.id, key='temp_transfer_money', value=data)
        return bot.send_message(chat_id=message.chat.id, text='<b>Ваша заявка обрабатывается, вам придет уведомление когда администратор обработает заявку.</b>', parse_mode='HTML')
    except (ValueError, TypeError):
        message = bot.send_message(message.chat.id, text=f'<b>Введите номер QIWI кошелька в формате 79001112233.</b>', reply_markup=cancel_next_handlers(), parse_mode='HTML') 
        bot.register_next_step_handler(message, qiwi_account_transfer, money)