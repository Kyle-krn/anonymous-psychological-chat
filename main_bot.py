import telebot
from flask import render_template, request, abort, redirect, url_for
import logging
import time
import datetime
from settings import TELEGRAM_TOKEN, HOST, app
from handlers import bot
from database import sql_db, Users, db
import os
import shutil
import statistics
from pytz import timezone


if __name__ == '__main__':
    WEBHOOK_HOST = HOST
    WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
    WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

    WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
    WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

    # Quick'n'dirty SSL certificate generation:
    #
    # openssl genrsa -out webhook_pkey.pem 2048
    # openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
    #
    # When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
    # with the same value in you put in WEBHOOK_HOST

    WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
    WEBHOOK_URL_PATH = "/%s/" % (TELEGRAM_TOKEN)

    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    # # Process webhook calls

    def russian_str_date(str_time):
        if 'days' in str_time:
            str_time = str_time.replace('days', 'дней')
        elif 'day' in str_time:
            str_time = str_time.replace('day', 'день')
        return str_time

    def delete_microseconds(delta):
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            abort(403)

    @app.route('/', methods=['GET', 'HEAD'])
    def index():
        # sql_db.create_all()
        users = db.db.users.find()
        return render_template('index.html', users=users)

    @app.route("/<int:user_id>",  methods=['GET'])
    def user_view(user_id):
        user = db.get_user_on_id(user_id)
        companion = None
        list_count_message = [x['count_message'] for x in user['dialog_time']]
        second_in_dialog = sum([x['delta'] for x in user['dialog_time']])
        time_in_dialog = str(datetime.timedelta(seconds=second_in_dialog))
        all_time_in_bot = str(delete_microseconds(datetime.datetime.now() - datetime.datetime.strptime(user['statistic']['start_date'], "%Y-%m-%d %H:%M:%S")))
        mean_time_in_dialog = statistics.mean(([x['delta'] for x in user['dialog_time']] or [0]))
        mean_time_in_dialog = str(datetime.timedelta(seconds=mean_time_in_dialog))
        print(mean_time_in_dialog)
        statistic = {
            'all_count_message': sum(list_count_message),
            'mean_count_message': statistics.mean((list_count_message or [0])),
            'count_dialog': len(user['dialog_time']),
            'time_in_dialog': russian_str_date(time_in_dialog),
            'all_time_in_bot': russian_str_date(all_time_in_bot)
            }

        user['statistic']['start_date'] = (datetime.datetime.strptime(user['statistic']['start_date'], "%Y-%m-%d %H:%M:%S") \
                                           + datetime.timedelta(hours=3)).isoformat(' ', 'seconds')
        user['statistic']['last_action_date'] = (datetime.datetime.strptime(user['statistic']['last_action_date'], "%Y-%m-%d %H:%M:%S") \
                                                 + datetime.timedelta(hours=3)).isoformat(' ', 'seconds')
        if user['companion_id']:
            companion = db.db.users.find_one({'user_id': user['companion_id']})
        return render_template('user.html', user=user, companion=companion, statistic=statistic)

    @app.route("/<int:user_id>/verif",  methods=['POST'])
    def user_verif(user_id):
        if 'reject' in request.form:
            filepath = f'static/verefication_doc/{user_id}/'
            db.update_verifed_psychologist(user_id, False)
            if os.path.exists(filepath):
                coment = request.form['reject_coment']
                text = '<u><b>Сообщение от администрации об отклонении верификации:</b></u>\n\n' + (coment or 'Ваши документы отклоненны по неуказаной причине')
                message = bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
                shutil.rmtree(filepath)
        if 'confirm' in request.form:
            db.update_verifed_psychologist(user_id, True)
        return redirect(url_for('user_view', user_id=user_id))


    # Handle '/start' and '/help'


    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()

    time.sleep(2)

    # Set webhook
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    # Start flask server
    app.run(host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
            debug=True)
