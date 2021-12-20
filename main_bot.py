# import telebot
# from handlers import bot
# from settings import TELEGRAM_TOKEN

# if __name__ == '__main__':
#     bot.remove_webhook()
#     bot.polling(none_stop=True)

import telebot
import flask
import logging
import time
from settings import TELEGRAM_TOKEN, HOST
from handlers import bot
from flask_module import app



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

    # app = flask.Flask(__name__)


    # Empty webserver index, return nothing, just http 200
    # @app.route('/', methods=['GET', 'HEAD'])
    # def index():
    #     return 'Привет'


    # # Process webhook calls
    @app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)


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
