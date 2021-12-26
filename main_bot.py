import telebot
import logging
import time
from flask_route import app
from handlers import bot
from webhook_settings import *


if __name__ == '__main__':
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)
    bot.remove_webhook()
    time.sleep(2)
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))
    app.run(host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
            debug=True)
