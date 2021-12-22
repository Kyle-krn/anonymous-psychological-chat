from flask_sqlalchemy import SQLAlchemy
from settings import app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

sql_db = SQLAlchemy(app)

class Users(sql_db.Model, UserMixin):
    id = sql_db.Column(sql_db.Integer, primary_key=True)
    login = sql_db.Column(sql_db.String(50), unique=True)
    psw = sql_db.Column(sql_db.String(500), nullable=False)
 
    def __repr__(self):
        return '<User %r>' % self.id

    def set_password(self, new_psw):
        self.psw = generate_password_hash(new_psw)

    def check_password(self, raw_psw):
        return check_password_hash(self.psw, raw_psw)
