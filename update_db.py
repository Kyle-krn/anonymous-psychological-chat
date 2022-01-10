from database import db
from handlers import bot
import time

def update_users():
    new_field = {
        'temp_payment': None,
        'temp_transfer_money': None,
        'balance': 0,
        'history_payment': [],
        'about_me': {
                        'price': 0,
                        'name': '',
                        'about': ''
                    },
        'premium_search': False,
        'time_start_premium_dialog': None,
        'premium_rating': [],
        'data_premium_rating_companion': [],
        'premium_dialog_time': [],
        'complaint': [],
        'admin_shadowing': False,
        'temp_message': [],
    }

    db.db.users.update_many({}, {'$set': new_field})

def test(val):
    bot.send_message(chat_id=390442593, text=val)

if __name__ == '__main__':
    update_users()