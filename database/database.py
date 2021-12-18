from pymongo import MongoClient
from settings import MONGO_LINK

class DBclient:
    def __init__(self):
        self.client = MongoClient(MONGO_LINK)
        self.db = self.client['test_chat']

    def cancel_search(self, user_id):
        '''Выключает поиск'''
        user = self.get_user_on_id(user_id)
        self.db.users.update_one({'user_id': user_id}, {'$set': {'search_companion': False, 'companion_id': None}})
        if user['companion_id']:
            self.db.users.update_one({'user_id': user_id}, {'$set': {'last_companion_id': user['companion_id']}})
            self.db.users.update_one({'user_id': user['companion_id']}, {'$set': {'search_companion': False, 'companion_id': None, 'last_companion_id': user_id}})
            return True

    def get_or_create_user(self, user_data):
        '''Создает и отдает юзера'''
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
                'data_rating_companion': []             # Скалдывается информация о сообщениях рейтинга и к какому юзеру сообщение относится -- типа {'user_id': 0000000000, 'message_id': 0000000}
            }
            self.db.users.insert_one(user)
        return user

    def push_data_rating_companion(self, user_id, data):
        '''Скалдывает инфу о сообщениях рейтинга и к какому юзеру сообщение относится'''
        self.db.users.update_one({'user_id': user_id}, {'$push': {'data_rating_companion': data}})

    def get_data_rating_companion(self, user_id, message_id):
        data = self.db.users.find_one({"user_id": user_id, 'data_rating_companion.message_id': message_id}, {'data_rating_companion.$': 1})
        data = data['data_rating_companion'][0]
        return data
    
    def delete_data_rating_companion(self, user_id, message_id):
        self.db.users.update_one({"user_id": user_id}, {'$pull': {'data_rating_companion': {'message_id': message_id}}})

    def inc_rating(self, user_id, count):
        self.db.users.update_one({'user_id': user_id}, {'$inc': {'rating': count}})

    def helper(self, user_id, help_bool):
        '''Изменяет строчку helper'''
        return self.db.users.update_one({'user_id': user_id}, {'$set': {'helper': help_bool}})

    def get_user_on_id(self, user_id):
        '''Получить пользователя по id'''
        return self.db.users.find_one({'user_id': user_id})


    def search_companion(self, user_id):
        '''Поиск собеседника'''
        user = self.get_user_on_id(user_id)
        mongo_filter = {'user_id': {'$nin': [user['user_id'], user['last_companion_id']] + user['block_companion']},
                        'block_companion': {'$ne': user['user_id']},
                        'search_companion': True,
                        'companion_id': None}
        if user['helper']:      # Включает в поиск противоположную категорию helper
            mongo_filter['helper'] = False
        else:
            mongo_filter['helper'] = True

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
        '''Заблокировать собеседника'''
        user = self.get_user_on_id(user_id)
        if not user['companion_id']:
            return
        self.db.users.update_one({'user_id': user['user_id']}, {'$push': {'block_companion': user['companion_id']}, '$set': {'search_companion': False, 'companion_id': None}})
        self.db.users.update_one({'user_id': user['companion_id']}, {'$set': {'search_companion': False, 'companion_id': None}})

    def next_companion(self, user_id):
        '''Поиск следующего собесендика'''
        user = self.get_user_on_id(user_id)
        self.db.users.update_one({'user_id': user['user_id']}, {'$set': {'last_companion_id': user['companion_id']}})
        self.db.users.update_one({'user_id': user['companion_id']}, {'$set': {'last_companion_id': user['user_id'], 'search_companion': False, 'companion_id': None}})
        # return self.search_companion(user_id)


    

db = DBclient()


