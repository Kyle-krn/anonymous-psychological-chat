from pymongo import MongoClient
from settings import MONGO_LINK
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from utils import delete_microseconds

class DBclient:
    def __init__(self):
        self.client = MongoClient(MONGO_LINK)
        # self.db = self.client['anonymous_chat']
        self.db = self.client['chat']

    def cancel_search(self, user_id):
        '''Выключает поиск'''
        user = self.get_user_by_id(user_id)
        self.db.users.update_one({'user_id': user_id}, {'$set': {'search_companion': False, 'companion_id': None}})
        if user['companion_id']:
            self.db.users.update_one({'user_id': user_id}, {'$set': {'last_companion_id': user['companion_id']}})
            self.db.users.update_one({'user_id': user['companion_id']}, {'$set': {'search_companion': False, 'companion_id': None, 'last_companion_id': user_id}})
            return True

    def get_or_create_user(self, user_data):
        '''Создает и отдает юзера'''
        moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))
        user = self.db.users.find_one({'user_id': user_data.id})
        if user:
            if user['username'] != user_data.username:
                self.db.users.update_one({'user_id': user_data.id}, {'$set': {'username': user_data.username}})
        else:
            user = {
                'user_id': user_data.id,                # Уникальный id юзера
                'first_name': user_data.first_name,     # Имя
                'last_name': user_data.last_name,       # Фамилия
                'username': user_data.username,         # Юзернейм
                'search_companion': False,              # Если True - находится в поиске собеседника
                'companion_id': None,                   # Уникальный id собеседника
                'helper': None,                         # Если True - тот кто помогает, если False - - тот кому нужна помощь, None - не выбрано
                'rating': 0,                            # Рейтинг пользователя
                'last_companion_id': None,              # Уникальный id последнего собеседника
                'block_companion': [],                  # Список уникальных id юзеров в блоке 
                'data_rating_companion': [],            # Скалдывается информация о сообщениях рейтинга и к какому юзеру сообщение относится -- типа {'user_id': 0000000000, 'message_id': 0000000}
                'verified_psychologist': False,         # False - не верифицированный, 'under_consideration' - на рассмотрении, True - верифицированный
                'blocked': False,                       # True - заблокированный пользователь
                'statistic': {
                                'last_action_date': moscow_time,  # Последняя активность
                                'start_date': str(datetime.now().isoformat(' ', 'seconds')),    # Дата начала использования бота
                                'output_finish': 0,                         # Сколько раз с пользователем заверешили диалог
                                'input_finish': 0,                          # Сколько раз пользователь завершал диалог
                             },
                'dialog_time': [            # Пример пуша в dialog_time
                                    # {
                                    #     'start': str(datetime.now().isoformat(' ', 'seconds')),
                                    #     'end': str(datetime.now().isoformat(' ', 'seconds')),
                                    #     'delta': datetime.now() - datetime.strptime(last_date['start'], "%Y-%m-%d %H:%M:%S"),
                                    #     'count_message': 0
                                    # }
                                ],                       # Массив со статистикой диалогов
                                
                
                'temp_payment': None,           # Здесь хранится данные о текущей оплате
                                                # {
                                                #    'user_id': call.message.chat.id,
                                                #     'status': 'replenishment',
                                                #     'date': bill_date,
                                                #     'billid': billid,
                                                #     'coast_with_commission': coast_with_commission,
                                                #     'coast': coast,
                                                #     'pay_url': bill['payUrl']
                                                # }

                'temp_transfer_money': None,    # Данные о выводе средств       
                                                # {
                                                    # 'user_id': message.chat.id,
                                                    # 'amount_of_money': money,
                                                    # 'qiwi_account': qiwi_account,
                                                    # 'date': datetime.utcnow().replace(microsecond=0)
                                                # }

                'balance': 0,                   # Денежный счёт пользователя
                'history_payment': [          # История пополнений, выводов, переводов и тд           # status: consumption (Расход), replenishment(Пополнение),  (Доход)

                                    #    {  ---------- Пополнение баланса
                                    #    'user_id': call.message.chat.id,
                                    #     'status': 'replenishment',
                                    #     'date': bill_date,
                                    #     'billid': billid,
                                    #     'coast_with_commission': coast_with_commission,
                                    #     'coast': coast,
                                    #     'pay_url': bill['payUrl']
                                    #    }      

                                    # {   ----------- Вывод средств
                                    #     'user_id': message.chat.id,
                                    #     'status': 'transfer_money',
                                    #     'coast': money,
                                    #     'qiwi_account': qiwi_account,
                                    #     'date': datetime.utcnow().replace(microsecond=0)
                                    # }

                                    # {   ----------- Потрачено
                                    #     'status': 'consumption',
                                    #     'date': date,
                                    #     'from': user['user_id'],
                                    #     'coast': price,
                                    #     'for': companion_user['user_id']
                                    # }

                                    # {   ----------- Заработано
                                    #     'status': 'income',
                                    #     'date': date,
                                    #     'from': user['user_id'],
                                    #     'coast': price,
                                    #     'for': companion_user['user_id']
                                    # }

                                    ],
                'about_me': {                   # О психологе
                    'price': 0,                 # Цена
                    'name': '',                 # Имя
                    'about': ''                 # О себе
                },
                'premium_search': False,        # Премиум поиск - (для кат. "Мне нужна помощь - Поиск только вериф. психологов", для психологов - Поиск пациентов с не 0ым балансом)
                'time_start_premium_dialog': None,          # Если платный чат есть, здесь данные о старте диалога, если None - платного чата нет
                'premium_rating': [
                                    # {
                                    # 'rating': rating | int((1-5)),
                                    # 'review': review | str,
                                    # 'datetime': datetime.utcnow().replace(microsecond=0), | datetime
                                    # 'from': message.chat.id   int()
                                    # }
                ],                       # Отзывы и баллы для псхиологов
                'data_premium_rating_companion': [
                                            # {
                                            #     'user_id': companion_user['user_id'],
                                            #     'message_id': message_premium_rating.message_id
                                            # }
                ],        # Данные что бы отзыв и балл достался определенному психологу
                'premium_dialog_time': [                    # Данные о премиум диалогах
                                            # {
                                            #     'start':
                                            #     'end':
                                            #     'delta':
                                            #     'psy':
                                            #     'patient':
                                            # }
                                        ],
                'complaint': [
                            #  {
                            # 'complaint': complaint,
                            # 'date': datetime.utcnow().replace(microsecond=0),
                            # 'check_admin': False 
                            #  }
                             ],                         # Жалобы
                
                'admin_shadowing': False,                # Режим слежки от админа (используется для юзеров с жалобами по решению админа)
                'temp_message': [],                       # Последние 100 сообщений

                'favorite_chat': [],
                'call_favorite_chat': None,
                                        # {
                                            # 'name': '',
                                            # 'for': '',
                                            # 'from': '',
                                        # }
            }
            self.db.users.insert_one(user)
        return user

    def get_user_by_id(self, user_id):
        '''Получить пользователя по id'''
        return self.db.users.find_one({'user_id': user_id})

    def push_data_rating_companion(self, user_id, data):
        '''Скалдывает инфу о сообщениях рейтинга и к какому юзеру сообщение относится'''
        self.db.users.update_one({'user_id': user_id}, {'$push': {'data_rating_companion': data}})

    def get_data_rating_companion(self, user_id, message_id):
        '''Вытаскивает инфу о сообщениях рейтинга'''
        data = self.db.users.find_one({"user_id": user_id, 'data_rating_companion.message_id': message_id}, {'data_rating_companion.$': 1})
        data = data['data_rating_companion'][0]
        return data

    def get_data_premium_rating_companion(self, user_id, message_id):
        '''Вытаскивает инфу о сообщениях рейтинга'''
        data = self.db.users.find_one({"user_id": user_id, 'data_premium_rating_companion.message_id': message_id}, {'data_premium_rating_companion.$': 1})
        data = data['data_premium_rating_companion'][0]
        return data
    
    def delete_data_rating_companion(self, user_id, message_id):
        '''Удаляет инфу о сообщениях рейтинга'''
        self.db.users.update_one({"user_id": user_id}, {'$pull': {'data_rating_companion': {'message_id': message_id}}})

    def delete_data_premium_rating_companion(self, user_id, message_id):
        self.db.users.update_one({"user_id": user_id}, {'$pull': {'data_premium_rating_companion': {'message_id': message_id}}})

    def inc_rating(self, user_id, count):
        '''Изменяет рейтинг'''
        self.db.users.update_one({'user_id': user_id}, {'$inc': {'rating': count}})

    def helper(self, user_id, help_bool):
        '''Изменяет строчку helper'''
        return self.db.users.update_one({'user_id': user_id}, {'$set': {'helper': help_bool}})

    def search_companion(self, user_id):
        '''Поиск собеседника'''
        user = self.get_user_by_id(user_id)
        mongo_filter = {'user_id': {'$nin': [user['user_id'], user['last_companion_id']] + user['block_companion']},
                        'block_companion': {'$ne': user['user_id']},
                        'search_companion': True,
                        'last_companion_id': {'$ne': user['user_id']},
                        'companion_id': None}
        if user['helper']:      # Включает в поиск противоположную категорию helper
            mongo_filter['helper'] = False
        else:
            mongo_filter['helper'] = True
        
        if user['helper'] is True and user['verified_psychologist'] != True:
            mongo_filter['premium_search'] = False

        if user['helper'] is False and user['premium_search'] is True:
            mongo_filter['verified_psychologist'] = True
        elif user['helper'] is True and user['premium_search'] is True:
            mongo_filter['balance'] = {'$gt': 1} 

        if self.db.users.find_one(mongo_filter):     # Если хоть один юзер находится в поиске
            for item in self.db.users.aggregate([{'$match': mongo_filter}, {'$sample' : {'size': 1}}]):
                companion_user = item
            self.db.users.update_one({'user_id': user['user_id']}, {'$set': {'search_companion': False, 'companion_id': companion_user['user_id']}})      # Выключаем поиск и присваиваем юзерам собеседника
            self.db.users.update_one({'user_id': companion_user['user_id']}, {'$set': {'search_companion': False, 'companion_id': user['user_id']}})      # Для обоих юзеров
            return True
        else:   # Если никого в поиске нет
            self.db.users.update_one({'user_id': user['user_id']}, {'$set': {'search_companion': True, 'companion_id': None}})    # Ставим юзера на ожидание собеседника
            return False

    def block_companion(self, user_id):
        '''Заблокировать собеседника - в приложении пока не используется'''
        user = self.get_user_by_id(user_id)
        if not user['companion_id']:
            return
        self.db.users.update_one({'user_id': user['user_id']}, {'$push': {'block_companion': user['companion_id']}, '$set': {'search_companion': False, 'companion_id': None}})
        self.db.users.update_one({'user_id': user['companion_id']}, {'$set': {'search_companion': False, 'companion_id': None}})

    def next_companion(self, user_id):
        '''Поиск следующего собесендика'''
        user = self.get_user_by_id(user_id)
        self.db.users.update_one({'user_id': user['user_id']}, {'$set': {'last_companion_id': user['companion_id'], 'companion_id': None}})
        self.db.users.update_one({'user_id': user['companion_id']}, {'$set': {'last_companion_id': user['user_id'], 'search_companion': False, 'companion_id': None}})
    
    def update_last_action_date(self, user_id):
        '''Обнавляет дату и время последнего действия'''
        self.db.users.update_one({'user_id': user_id}, {'$set': {'statistic.last_action_date': datetime.now().replace(microsecond=0)}})
    
    def push_date_in_start_dialog_time(self, user_id):
        '''Добавляет в массив дату и время начала диалога'''

        time_dict = {
            'start': str(datetime.now().isoformat(' ', 'seconds')),
            'end': None,
            'delta': None,
            'count_message': 0
        }
        self.db.users.update_one({'user_id': user_id}, {"$push": {'dialog_time': time_dict }})

    def update_count_message_dialog_time(self, user_id):
        '''Обновляет счетчик сообщений в диалоге'''
        user = self.db.users.find_one({'user_id': user_id}, {'dialog_time':{'$slice': -1}})
        clear_last_date = user['dialog_time'][0]
        self.db.users.update_one({'user_id': user_id, 'dialog_time.start': clear_last_date['start']}, {'$inc': {'dialog_time.$.count_message': 1}})

    def push_date_in_end_dialog_time(self, user_id):
        # "%Y-%m-%d %H:%M:%S"
        '''Добавляет в массив дату и время конца диалога'''
        user = self.db.users.find_one({'user_id': user_id}, {'dialog_time':{'$slice': -1}})
        clear_last_date = user['dialog_time'][0]
        last_date = clear_last_date.copy()
        last_date['end'] = str(datetime.now().isoformat(' ', 'seconds'))
        delta = datetime.now() - datetime.strptime(last_date['start'], "%Y-%m-%d %H:%M:%S")
        last_date['delta'] = int(delta.total_seconds())
        self.db.users.update_one({'user_id': user_id}, {'$pull': {'dialog_time': clear_last_date}})
        self.db.users.update_one({'user_id': user_id}, {'$push': {'dialog_time': last_date}})

    def set_value(self, user_id, key, value):
        self.db.users.update_one({'user_id': user_id}, {'$set': {key: value}})

    def inc_value(self, user_id, key, value):
        self.db.users.update_one({'user_id': user_id}, {'$inc': {key: value}})

    def push_value(self, user_id, key, value):
        self.db.users.update_one({'user_id': user_id}, {'$push': {key: value}})

    def push_shadowing_message(self, message):
        '''Добавляет или хранит в массиве только последние 100 сообщений пользователя с плохим рейтингом'''
        user = db.get_user_by_id(message.chat.id)
        temp_message = user['temp_message']
        print(temp_message)
        if len(temp_message) <= 100:
            db.push_value(user_id=user['user_id'], key='temp_message', value=(message.text or message.caption))
        else:
            temp_message.append((message.text or message.caption))
            temp_message = temp_message[1:]
            db.set_value(user_id=user['user_id'], key='temp_message', value=temp_message)

    def get_favorite_chat(self, user_id, favorite_id):
        return db.db.users.find_one({'user_id': user_id, 'favorite_chat.user_id': favorite_id}, {'favorite_chat.$': 1})['favorite_chat'][0]
        

db = DBclient()

