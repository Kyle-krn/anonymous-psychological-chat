from flask import render_template, request, abort, redirect, url_for
from flask_login.utils import logout_user
from flask_login import login_required, login_user, current_user
from settings import app
from utils import russian_str_date, delete_microseconds
from handlers import bot
from keyboard import block_keyboard, main_keyboard
from database import Users, db
from webhook_settings import *
from flask import jsonify
from qiwi import qiwi_balance
import pytz
import os
import shutil
import statistics
import datetime
import telebot
import time
from statistics import mean



@app.context_processor
def utility_processor():
    def computation_premium_rating(user_id):
        user = db.get_user_by_id(user_id)
        data_rating = user['premium_rating']
        int_rating = [item['rating'] for item in data_rating]
        return f"{mean(int_rating):.1f}"

    verification_count = db.db.users.count_documents({'verified_psychologist': 'under_consideration'})
    complaint_count = db.db.users.count_documents({'complaint.check_admin': False})
    shadowing_count = db.db.users.count_documents({'$or': [{'rating': {'$lte': -15}}, {'': True}]})
    transfer_money_count = db.db.users.count_documents({'temp_transfer_money': {'$ne': None}})
    return dict(verification_count=verification_count, complaint_count=complaint_count, shadowing_count=shadowing_count, transfer_money_count=transfer_money_count, computation_premium_rating=computation_premium_rating)

@app.context_processor
def utility_processor():
    def get_username_companion(user_id):
        user = db.get_user_by_id(user_id)
        return user['username'] if user['username'] else user['user_id']
    return dict(get_username_companion=get_username_companion)

 

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    '''Принимает сообщения от telegram'''
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@app.route("/login", methods=['POST', 'GET'])
def login():
    '''Представление аутентификации'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        login = request.form['login']
        pswd = request.form['password']
        user = Users.query.filter_by(login=login).first()
        if user is None:
            flash('Попробуйте снова')
        else:
            if user.check_password(pswd):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Попробуйте снова')
    return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    '''Представление выхода из аккаунта'''
    logout_user()
    return redirect(url_for('login'))


@app.route('/<int:page>', methods=['GET', 'HEAD'])
@app.route('/', methods=['GET', 'HEAD'])
@login_required
def index(page=1):
    '''Представление списка пользователей'''
    params = {k:v for k,v in request.args.items() if v != ''}
    copy_params = params.copy()

    search_filter = {}
    if 'username' in params:            # Фильтр по никнейму
        nick = params['username']
        search_filter['username'] = {'$regex': nick, '$options' : 'i' }
    if 'category' in params:            # Фильтр по роли (психологи или те кому нужна помощь)
        if params['category'] == 'helper':
            params['category'] = True
        elif params['category'] == 'non_helper':
            params['category'] = False
        search_filter['helper'] = params['category']
    if 'verification' in params:        # Фильтр по верификации психолога 
        if params['verification'] == 'verif':
            params['verification'] = True
        elif params['verification'] == 'non_verif':
            params['verification'] = False
        elif params['verification'] == 'under_consideration':
            params['verification'] == 'under_consideration'
        search_filter['verified_psychologist'] = params['verification']
    if 'search_companion_params' in params:
        if params['search_companion_params'] == 'companion':
            # params['search_companion_params'] = {'companion_id': {'$ne': None}}
            search_filter['companion_id'] = {'$ne': None}
        elif params['search_companion_params'] == 'search':
            search_filter['search_companion'] = True
        elif params['search_companion_params'] == 'non_search': 
            search_filter['search_companion'] = False
    count_search_user = db.db.users.count_documents({'search_companion': True})
    today_online_users = db.db.users.count_documents({'statistic.last_action_date': {'$gte': datetime.datetime.now() - datetime.timedelta(minutes=60 * 24)}})
    now_online_users = db.db.users.count_documents({'statistic.last_action_date': {'$gte': datetime.datetime.now() - datetime.timedelta(minutes=10)}})
    if 'complaint' in params:
        search_filter = {'complaint.check_admin': False}
    elif 'shadowing' in params:
        search_filter = {'$or': [{'rating': {'$lte': -15}}, {'admin_shadowing': True}]}
    users = db.db.users.find(search_filter)
    count_users = db.db.users.count_documents(search_filter)
    sort_by = '_id'
    sort_params = 1
    if 'sort' in params:               # Сортировка массива юзеров
        sort_by = params['sort']
        if params['sort_param'] == 'asc':
            sort_params = 1
        else:
            sort_params = -1
    users = users.sort(sort_by, sort_params)
    limit = 20
    last_page = count_users/limit
    
    previous_page = page-1
    next_page = page+1
    if type(last_page) == float:
        last_page = int(last_page+1)
    elif type(last_page) == int:
        last_page = last_page
    if page == 1:
        previous_page = None
    if page == last_page:
        next_page = None
    if page > last_page:
        return redirect(url_for('index', **copy_params))

    query_string = request.query_string.decode('utf-8')
    if query_string:
        query_string = '?' + query_string
    offset = (page - 1) * 20
    users = users.skip(offset).limit(limit)
    return render_template('index.html', users=users, 
                                         count_users=count_users, 
                                         count_search_user=count_search_user,
                                         today_online_users=today_online_users,
                                         now_online_users=now_online_users,
                                         query_string=query_string,
                                         previous_page=previous_page,
                                         next_page=next_page,
                                         page=page,
                                         last_page=last_page,
                                         offset=offset)


@app.route("/user/<int:user_id>",  methods=['GET'])
@login_required
def user_view(user_id):
    '''Детальное представление пользователя'''
    user = db.get_user_by_id(user_id)
    user['statistic']['last_action_date'] += datetime.timedelta(hours=3, minutes=0)
    if user is None:
        abort(404)
    list_count_message = [x['count_message'] for x in user['dialog_time']]                                                  # Массив кол-ва сообщений в диалогах
    second_in_dialog = sum((([x['delta'] for x in user['dialog_time'] if x['delta'] is not None])))                         # Общее время в диалогах с собеседниками (в секундах)
    mean_time_in_dialog = statistics.mean(([x['delta'] for x in user['dialog_time'] if x['delta'] is not None] or [0]))     # Среднее время проведенное в диалогах (в секундах)
    time_in_dialog = str(datetime.timedelta(seconds=second_in_dialog))                                                      # Преобразование секунд в дни или часы
    all_time_in_bot = str(delete_microseconds(datetime.datetime.now() - datetime.datetime.strptime(user['statistic']['start_date'], "%Y-%m-%d %H:%M:%S")))  # Общее время использование бота
    mean_time_in_dialog = str(datetime.timedelta(seconds=mean_time_in_dialog))                                              # Преобразование секунд в дни или часы
    statistic = {
        'total_count_message': sum(list_count_message),                         # Всего сообщений написанных собеседнику
        'mean_count_message': statistics.mean((list_count_message or [0])),     # Среднее кол-во сообщений написанных собеседнику
        'count_dialog': len(user['dialog_time']),                               # Кол-во диалогов
        'time_in_dialog': russian_str_date(time_in_dialog),                     # Общее время проведенное в переписке с собеседником
        'mean_time_in_dialog':russian_str_date(mean_time_in_dialog),            # Среднее время проведенное в переписке с собеседником
        'all_time_in_bot': russian_str_date(all_time_in_bot),                   # Общее время использования бота
        }
    companion = None
    stat_payment = {
                'consumption_total': sum([cons['coast'] for cons in user['history_payment'] if cons['status'] == 'consumption']), # Расход
                'replenishment_total': sum([cons['coast'] for cons in user['history_payment'] if cons['status'] == 'replenishment']), # Пополнение
                'income_total': sum([cons['coast'] for cons in user['history_payment'] if cons['status'] == 'income']) # Доход
                }
    if user['companion_id']:
        companion = db.db.users.find_one({'user_id': user['companion_id']})
    new_complaint = [comp for comp in user['complaint'] if comp['check_admin'] is False]
    
    return render_template('user.html', user=user, companion=companion, statistic=statistic, len_new_complaint=len(new_complaint), stat_payment=stat_payment)



@app.route("/user/<int:user_id>/shadowing",  methods=['GET'])
@login_required
def shadowing_view(user_id):
    '''Представление прослушивания сообщений'''
    user = db.get_user_by_id(user_id)
    if len(user['temp_message']) == 0:
        abort(404)
    user['temp_message'].reverse()
    return render_template('shadowing.html', user=user)

@app.route("/user/<int:user_id>/review",  methods=['GET'])
@login_required
def review_view(user_id):
    '''Представление отзывов вериф. психолога'''
    user = db.get_user_by_id(user_id)
    if len(user['premium_rating']) == 0:
        abort(404)
    return render_template('review.html', user=user)

@app.route("/user/<int:user_id>/complaint",  methods=['GET'])
@login_required
def complaint_view(user_id):
    '''Представления жалоб'''
    user = db.get_user_by_id(user_id)
    if len(user['complaint']) == 0:
        abort(404)
    return render_template('complaint.html', user=user)

@app.route("/bulk",  methods=['GET'])
@login_required
def bulk_handler():
    '''Представление массовой рассылки пользователям'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    return render_template('bulk.html')


@app.route("/transfer_money", methods=['GET'])
@login_required
def transfer_money_view():
    '''Список вывода денег'''
    balance = qiwi_balance()
    users = db.db.users.find({'temp_transfer_money': {'$ne' : None}})
    return render_template('transfer_money.html', balance=balance, users=users)

@app.route("/get_money", methods=['GET'])
@login_required
def get_money_view():
    '''Список пополнений счёта'''
    balance = qiwi_balance()
    users = db.db.users.find({'history_payment.status': 'replenishment'}).sort('history_payment.date', -1)
    data = [{'user_id': user['user_id'], 'username': user['username'], 'balance': user['balance'], 'history_payment': [payment for payment in user['history_payment'] if payment['status'] == 'replenishment']} for user in users]
    return render_template('get_money.html', balance=balance, users=data)


@app.route("/user/<int:user_id>/complaint_post",  methods=['POST'])
@login_required
def complaint_post(user_id):
    '''Отмечает жалобу обработанной'''
    str_date = request.form['date']
    date = datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
    db.db.users.update_one({'user_id': user_id, 'complaint.date': date}, {'$set': {'complaint.$.check_admin': True}})
    return redirect(url_for('complaint_view', user_id=user_id))


@app.route("/user/<int:user_id>/cancel_transfer_money/",  methods=['POST'])
@login_required
def cancel_transfer_money_post(user_id):
    '''Отмена вывода'''
    user = db.get_user_by_id(user_id)
    if not user['temp_transfer_money']:    return
    temp_transfer_money = user['temp_transfer_money']
    db.set_value(user_id=user_id, key='temp_transfer_money', value=None)
    db.inc_value(user_id=user_id, key='balance', value=temp_transfer_money['coast'])
    bot.send_message(chat_id=user_id, text='**Ваша заявка на вывод средств была отклонена**')
    return redirect(url_for('transfer_money_view'))

@app.route("/user/<int:user_id>/confirm_transfer_money/",  methods=['POST'])
@login_required
def confirm_transfer_money_post(user_id):
    '''Подтверждение отправки вывода'''
    user = db.get_user_by_id(user_id)
    if not user['temp_transfer_money']:    return
    db.set_value(user_id=user_id, key='temp_transfer_money', value=None)
    temp_transfer_money = user['temp_transfer_money']
    temp_transfer_money['status'] = 'transfer_money'
    db.push_value(user_id=user_id, key='history_payment', value=temp_transfer_money)
    bot.send_message(chat_id=user_id, text='**Ваша заявка на вывод средств была выполнена**')
    return redirect(url_for('transfer_money_view'))

@app.route("/user/<int:user_id>/verif",  methods=['POST'])
@login_required
def user_verif(user_id):
    '''Верификация пользователя'''
    if 'reject' in request.form:            # Отклонение верификации
        filepath = f'static/verefication_doc/{user_id}/'
        # db.update_verifed_psychologist(user_id, False)
        db.set_value(user_id=user_id, key='verified_psychologist', value=False)
        if os.path.exists(filepath):
            coment = request.form['reject_coment']
            text = '<u><b>Сообщение от администрации об отклонении верификации:</b></u>\n\n' + (coment or 'Ваши документы отклоненны по неуказаной причине')
            shutil.rmtree(filepath)
    if 'confirm' in request.form:           # Подтверждение верификации
        # db.update_verifed_psychologist(user_id, True)
        db.set_value(user_id=user_id, key='verified_psychologist', value=True)
        text = '<u><b>Ваша заявка о верификации одобрена</b></u>\n\n'
    message = bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
    return redirect(url_for('user_view', user_id=user_id))


@app.route("/user/<int:user_id>/send_message",  methods=['POST'])
@login_required
def send_user_message(user_id):
    '''Отправить сообщение пользователю'''
    text = '<u><b>Сообщение от администрации:</b></u>\n\n' +  request.form['text']
    try:
        bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:      # Если пользователя не существует
        print('chat_not_found')
    return redirect(url_for('user_view', user_id=user_id))


@app.route("/user/<int:user_id>/blocked",  methods=['POST'])
@login_required
def blocked_user(user_id):
    '''Блокировка пользователя'''
    user = db.get_user_by_id(user_id)
    if user['companion_id']:            # Если у пользователя есть собесендик, завершаем диалог с ним
        db.push_date_in_end_dialog_time(user_id) # Записываем дату и время конца диалога
        db.inc_value(user_id=user_id, key='statistic.output_finish', value=1)
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        db.push_date_in_end_dialog_time(user['companion_id']) # Записываем дату и время конца диалога
        db.inc_value(user_id=user['companion_id'], key='statistic.input_finish', value=1)
        db.cancel_search(user_id)
    text = '<u><b>Сообщение от администрации о блокировке:</b></u>\n\n' +  request.form['text'] 
    try:  
        bot.send_message(chat_id=user_id, text=text, reply_markup=block_keyboard(), parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:
        print('chat_not_found')
    db.set_value(user_id=user_id, key='blocked', value=True)
    return redirect(url_for('user_view', user_id=user_id))

@app.route("/user/<int:user_id>/shadowing_post",  methods=['POST'])
@login_required
def admin_shadowing_post(user_id):
    '''Кидает выбранного пользователя в слежку'''
    try:
        if 'true' in request.form:
            db.set_value(user_id=user_id, key='admin_shadowing', value=True)
        elif 'false' in request.form:
            db.set_value(user_id=user_id, key='admin_shadowing', value=False)
        return redirect(url_for('user_view', user_id=user_id))
    except Exception as e:
        print(e)

@app.route("/user/<int:user_id>/unblocked",  methods=['POST'])
@login_required
def unblocked_user(user_id):
    '''Разблокировка пользователя'''
    text = '<u><b>Сообщение от администрации о разблокировке:</b></u>\n\n' +  request.form['text']
    try:
        bot.send_message(chat_id=user_id, text=text, reply_markup=main_keyboard(), parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:
        print('chat_not_found')
    # db.blocked_user(user_id, False)
    db.set_value(user_id=user_id, key='blocked', value=False)
    return redirect(url_for('user_view', user_id=user_id))


@app.route("/bulk_mailing_post",  methods=['POST'])
@login_required
def bulk_mailing():
    '''Массовая рассылка пользователям'''
    params = {k:v for k,v in request.form.items() if v != ''}
    mongo_filter = {}
    if 'category' in params:
        if params['category'] == 'helper':
            mongo_filter['helper'] = True
        else:
            mongo_filter['helper'] = False
    if 'verification' in params:
        if params['verification'] == 'verif':
            mongo_filter['verified_psychologist'] = True
        elif params['verification'] == 'non_verif':
            mongo_filter['verified_psychologist'] = False
        else:
            mongo_filter['verified_psychologist'] = 'under_consideration'
    users = db.db.users.find(mongo_filter)
    count_users = db.db.users.count_documents(mongo_filter)
    photo_file_id = None
    count = 0
    for item in range(count_users):
        try:
            if 'img' in request.files:
                if item == 0:
                    message = bot.send_photo(users[item]['user_id'], request.files['img'], caption=request.form['text'], parse_mode='HTML')
                    photo_file_id = message.photo[2].file_id
                else:
                    bot.send_photo(users[item]['user_id'], photo_file_id, caption=request.form['text'], parse_mode='HTML')
            else:
                bot.send_message(users[item]['user_id'], text='<u><b>Сообщение от администрации:</b></u>\n\n'+request.form['text'], parse_mode='HTML')
            count += 1
            if count % 29 == 0:
                count = 0
                time.sleep(15)
        except telebot.apihelper.ApiTelegramException as e:
            print(e)
    return redirect(url_for('bulk_handler'))



