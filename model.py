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
    archivos = db.relationship('File')

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
    materia_id = db.Column(db.Integer)

    def __init__(self, tema):
        self.tema = tema

class Materia(db.Model):
    __tablename__ = 'materias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), unique=True)
    mat_fav = db.relationship('Materia_Favorito')

    def __init__(self, nombre):
        self.nombre = nombre

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    materia_id = db.Column(db.Integer)
    titulo = db.Column(db.String(60))
    descripcion = db.Column(db.Text)
    archivo = db.Column(db.Text)
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    favorito = db.relationship('Favorito')
    like = db.relationship('Like')

    def __init__(self, user_id, materia_id, titulo, descripcion, archivo, likes, dislikes):
        self.user_id = user_id
        self.materia_id = materia_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.archivo = archivo
        self.likes = likes
        self.dislikes = dislikes

class Favorito(db.Model):
    __tablename__ = 'favoritos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))

    def __init__(self, user_id, file_id):
        self.user_id = user_id
        self.file_id = file_id

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    like = db.Column(db.Integer)
    dislike = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self, file_id, like, dislike, user_id):
        self.file_id = file_id
        self.like = like
        self.dislike = dislike
        self.user_id = user_id

class Materia_Favorito(db.Model):
    __tablename__ = 'materias_fav'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'))
    file_id = db.Column(db.Integer)

    def __init__(self, user_id, materia_id, file_id):
        self.user_id = user_id
        self.materia_id = materia_id
        self.file_id = file_id
