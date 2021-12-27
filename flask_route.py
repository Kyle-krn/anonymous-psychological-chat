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
import pytz
import os
import shutil
import statistics
import datetime
import telebot
 

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


@app.route('/', methods=['GET', 'HEAD'])
def index():
    '''Представление списка пользователей'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    params = {k:v for k,v in request.args.items() if v != ''}
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
    users = db.db.users.find(search_filter)
    count_users = db.db.users.count_documents(search_filter)
    count_search_user = db.db.users.count_documents({'search_companion': True})
    if 'sort' in params:               # Сортировка массива юзеров
        sort_by = params['sort']
        if params['sort_param'] == 'asc':
            sort_params = 1
        else:
            sort_params = -1
        users = users.sort(sort_by, sort_params)
    return render_template('index.html', users=users, count_users=count_users, count_search_user=count_search_user)


@app.route("/<int:user_id>",  methods=['GET'])
def user_view(user_id):
    '''Детальное представление пользователя'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    user = db.get_user_on_id(user_id)
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
    if user['companion_id']:
        companion = db.db.users.find_one({'user_id': user['companion_id']})
    return render_template('user.html', user=user, companion=companion, statistic=statistic)


@app.route("/bulk",  methods=['GET'])
def bulk_handler():
    '''Представление массовой рассылки пользователям'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    return render_template('bulk.html')


@app.route("/<int:user_id>/verif",  methods=['POST'])
def user_verif(user_id):
    '''Верификация пользователя'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    if 'reject' in request.form:            # Отклонение верификации
        filepath = f'static/verefication_doc/{user_id}/'
        db.update_verifed_psychologist(user_id, False)
        if os.path.exists(filepath):
            coment = request.form['reject_coment']
            text = '<u><b>Сообщение от администрации об отклонении верификации:</b></u>\n\n' + (coment or 'Ваши документы отклоненны по неуказаной причине')
            shutil.rmtree(filepath)
    if 'confirm' in request.form:           # Подтверждение верификации
        db.update_verifed_psychologist(user_id, True)
        text = '<u><b>Ваша заявка о верификации одобрена</b></u>\n\n'
    message = bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
    return redirect(url_for('user_view', user_id=user_id))


@app.route("/<int:user_id>/send_message",  methods=['POST'])
def send_user_message(user_id):
    '''Отправить сообщение пользователю'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    text = '<u><b>Сообщение от администрации:</b></u>\n\n' +  request.form['text']
    try:
        bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:      # Если пользователя не существует
        print('chat_not_found')
    return redirect(url_for('user_view', user_id=user_id))


@app.route("/<int:user_id>/blocked",  methods=['POST'])
def blocked_user(user_id):
    '''Блокировка пользователя'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    user = db.get_user_on_id(user_id)
    if user['companion_id']:            # Если у пользователя есть собесендик, завершаем диалог с ним
        db.push_date_in_end_dialog_time(user_id) # Записываем дату и время конца диалога
        db.update_statistic_inc(user_id, 'output_finish')
        bot.send_message(chat_id=user['companion_id'], text='Ваш собеседник завершил беседу, вы можете найти нового собеседника', reply_markup=main_keyboard())
        db.push_date_in_end_dialog_time(user['companion_id']) # Записываем дату и время конца диалога
        db.update_statistic_inc(user['companion_id'], 'input_finish')
        db.cancel_search(user_id)
    text = '<u><b>Сообщение от администрации о блокировке:</b></u>\n\n' +  request.form['text'] 
    try:  
        bot.send_message(chat_id=user_id, text=text, reply_markup=block_keyboard(), parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:
        print('chat_not_found')
    db.blocked_user(user_id, True)
    return redirect(url_for('user_view', user_id=user_id))


@app.route("/<int:user_id>/unblocked",  methods=['POST'])
def unblocked_user(user_id):
    '''Разблокировка пользователя'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    text = '<u><b>Сообщение от администрации о разблокировке:</b></u>\n\n' +  request.form['text']
    try:
        bot.send_message(chat_id=user_id, text=text, reply_markup=main_keyboard(), parse_mode='HTML')
    except telebot.apihelper.ApiTelegramException:
        print('chat_not_found')
    db.blocked_user(user_id, False)
    return redirect(url_for('user_view', user_id=user_id))


@app.route("/bulk_mailing_post",  methods=['POST'])
def bulk_mailing():
    '''Массовая рассылка пользователям'''
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
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
    for user in users:
        try:
            if 'img' in request.files:
                bot.send_photo(user['user_id'], request.files['img'], caption=request.form['text'], parse_mode='HTML')
            else:
                bot.send_message(user['user_id'], text='<u><b>Сообщение от администрации:</b></u>\n\n'+request.form['text'], parse_mode='HTML')
        except telebot.apihelper.ApiTelegramException:
            print('chat_not_found')
    return redirect(url_for('bulk_handler'))


@app.route('/fix', methods=['GET'])
def fix_bug():
    users = db.db.users.find({'search_companion': False, 'companion_id': None})
    for user in users:
        try:
            bot.send_message(user['user_id'], text='<u><b>Сообщение от администрации:</b></u>\n\n'+'Фикс бага кто не получил клавиатуру при старте', parse_mode='HTML', reply_markup=main_keyboard())
        except:
            print('error')
    return redirect(url_for('bulk_handler'))


@app.route('/get_username', methods=['POST'])
def get_username():
    user = db.get_user_on_id(int(request.form['user_id']))
    if user['username']:
        username = user['username']
    else:
        username = user['user_id']
    return jsonify({'username': username})




