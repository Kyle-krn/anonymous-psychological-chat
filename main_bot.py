# import telebot
# from handlers import bot
# from settings import TELEGRAM_TOKEN

# if __name__ == '__main__':
#     bot.polling(none_stop=True)

import telebot
import cherrypy
from settings import TELEGRAM_TOKEN

if __name__ == '__main__':
    WEBHOOK_HOST = '178.155.4.121'
    WEBHOOK_PORT = 80  # 443, 80, 88 или 8443 (порт должен быть открыт!)
    WEBHOOK_LISTEN = '178.155.4.121'  # На некоторых серверах придется указывать такой же IP, что и выше

    WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
    WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

    WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
    WEBHOOK_URL_PATH = "/%s/" % (TELEGRAM_TOKEN)

    bot = telebot.TeleBot(TELEGRAM_TOKEN)

    class WebhookServer(object):
        @cherrypy.expose
        def index(self):
            if 'content-length' in cherrypy.request.headers and \
                            'content-type' in cherrypy.request.headers and \
                            cherrypy.request.headers['content-type'] == 'application/json':
                length = int(cherrypy.request.headers['content-length'])
                json_string = cherrypy.request.body.read(length).decode("utf-8")
                update = telebot.types.Update.de_json(json_string)
                # Эта функция обеспечивает проверку входящего сообщения
                bot.process_new_updates([update])
                return ''
            else:
                raise cherrypy.HTTPError(403)


    bot.remove_webhook()

    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })

    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
