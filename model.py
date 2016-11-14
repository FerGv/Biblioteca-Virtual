 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(66), unique=True)
    comentarios = db.relationship('Comment')

    def __init__(self, username, password):
        self.username = username
        self.password = self.__create_password(password)

    def __create_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    theme_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default = datetime.datetime.now)

    def __init__(self, user_id, comentario, theme_id):
        self.user_id = user_id
        self.text = comentario
        self.theme_id = theme_id

class Theme(db.Model):
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.Text)

    def __init__(self, tema):
        self.tema = tema
