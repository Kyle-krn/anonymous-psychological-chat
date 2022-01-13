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

def test():
    x = db.db.users.find_one({'user_id': 5073540565, 'favorite_chat.user_id': 390442593}, {'favorite_chat.$': 1})['favorite_chat'][0]
    # db.db.users.update_one({'user_id': 5073540565}, {'$push': {'favorite_chat': {'name': 'Катя', 'user_id': 666666}}})
    # print([i for i in x])
    print(x)

if __name__ == '__main__':
    test()