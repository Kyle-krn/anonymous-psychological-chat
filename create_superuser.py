from database import sql_db, Users
import os

def create_user():
    log = input('Введите имя пользователя: ')
    psw = input('Введите пароль: ')
    user = Users(login=log)
    user.set_password(psw)
    return user

def start_db():
    path = str(os.getcwd()) + '/psy_chat.db'
    if os.path.exists(path):
        answer = input('База данных уже создана, создать нового юзера? [Y/n] ')
        if answer.lower() == 'y':
            user = create_user()
        else:
            return
    else:
        sql_db.create_all()
        user = create_user()
    sql_db.session.add(user)
    sql_db.session.commit()
    print('Успешно!')

if __name__ == '__main__':
    start_db()
