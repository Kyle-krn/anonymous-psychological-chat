import telebot
from handlers import bot
from settings import TELEGRAM_TOKEN

if __name__ == '__main__':
    bot.polling(none_stop=True)