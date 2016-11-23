#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import forms

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from flask import send_from_directory
from flask_wtf import CsrfProtect

from werkzeug import secure_filename
from config import DevelopmentConfig

from model import db
from model import User
from model import Comment
from model import Theme
from model import File
from model import Materia
from model import Favorito
from model import Like

from helper import date_format

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['UPLOAD_FOLDER'] = 'Archivos/'
csrf = CsrfProtect()

@app.before_request
def before_request():
    if 'username' not in session and request.endpoint in ['upload', 'archivos', 'uploads', 'borrar_archivo', 'comentarios', 'bienvenida', 'temas', 'crear_tema', 'logout', 'favoritos', 'like', 'dislike', 'like_eliminar', 'dislike_eliminar', 'favorito', 'favorito_eliminar']:
        return redirect(url_for('login'))
    elif 'username' in session and request.endpoint in ['index', 'login', 'registro']:
        return redirect(url_for('bienvenida'))

@app.route('/')
def index():
    title = 'Index'
    return render_template('index.html', title = title)

@app.route('/bienvenida')
def bienvenida():
    title = 'Inicio'
    return render_template('bienvenida.html', title = title)

@app.route('/registro', methods = ['GET', 'POST'])
def registro():
    create_form = forms.Create_Form(request.form)

    if request.method == 'POST' and create_form.validate():
        username = create_form.user.data
        password = create_form.pwd.data

        user = User(username, password)

        db.session.add(user)
        db.session.commit()

        session['username'] = username
        session['user_id'] = user.id
        return redirect(url_for('bienvenida'))

    title = 'Registro'
    return render_template('registro.html', form = create_form, title = title)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = forms.Login_Form(request.form)

    if request.method == 'POST' and login_form.validate():
        username = login_form.user.data
        password = login_form.pwd.data

        user = User.query.filter_by(username = username).first()

        if user is not None and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = username
            return redirect(url_for('bienvenida'))
        else:
            flash('error_message')

    title = 'Login'
    return render_template('login.html', form = login_form, title = title)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        session.pop('user_id')

    return redirect(url_for('index'))

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    upload_file_form = forms.UploadFile_Form(request.form)

    if request.method == 'POST' and upload_file_form.validate():
        if 'file' not in request.files:
            flash('No hay seccion de archivos')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No se selecciono archivo')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            archivo = File(session['user_id'],
                            1,
                            upload_file_form.titulo.data,
                            upload_file_form.descripcion.data,
                            filename,
                            0,
                            0)

            db.session.add(archivo)
            db.session.commit()

            return redirect(url_for('archivos'))
    else:
        title = 'Subir archivo'
        return render_template('upload.html', title = title, form = upload_file_form)

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/archivos')
def archivos():
    favoritos = Favorito.query.join(File).add_columns(Favorito.user_id, File.titulo)
    likes = Like.query.join(File).add_columns(Like.user_id, File.titulo, Like.like)
    current_user = session['user_id']
    fav = []
    like = []
    dislike = []

    for file in favoritos:
        if file.user_id == current_user:
            fav.append(file.titulo)

    for file in likes:
        if file.user_id == current_user:
            if file.like == 1:
                like.append(file.titulo)
            else:
                dislike.append(file.titulo)

    archivos = File.query.all()
    for file in archivos:
        if file.dislikes == 6:
            return redirect(url_for('borrar_archivo', file_id = file.id))

    title = 'Biblioteca'
    return render_template('archivos.html', archivos = archivos, title = title, fav = fav, like = like, dislike = dislike)

@app.route('/borrar_archivo/<int:file_id>')
def borrar_archivo(file_id):
    mypath = '/home/fer_gv/GitHub/Biblioteca-Virtual/Archivos/'
    archivo = File.query.get(file_id)
    os.remove(os.path.join(mypath, archivo.archivo))
    db.session.delete(archivo)
    db.session.commit()

    return redirect(url_for('archivos'))

@app.route('/comentarios/<int:id_tema>', methods = ['GET', 'POST'])
def comentarios(id_tema = 1):
    tema = Theme.query.filter_by(id = id_tema).first()
    comments = Comment.query.join(User).add_columns(User.username, Comment.text, Comment.theme_id, Comment.created_date)

    comment_form = forms.Comment_Form(request.form)

    if request.method == 'POST' and comment_form.validate():
        comentario = Comment(session['user_id'], comment_form.comment.data, id_tema)
        db.session.add(comentario)
        db.session.commit()
        comment_form.comment.data = ""

        title = 'Comentarios'
        return render_template('comentarios.html', title = title, comments = comments, form = comment_form, id_tema = id_tema, date_format = date_format, tema = tema.tema)

    title = 'Comentarios'
    return render_template('comentarios.html', title = title, comments = comments, form = comment_form, id_tema = id_tema, date_format = date_format, tema = tema.tema)

@app.route('/temas')
def temas():
    temas = Theme.query.all()
    title = 'Foro'
    return render_template('temas.html', temas = temas, title = title)

@app.route('/crear_tema', methods = ['GET', 'POST'])
def crear_tema():
    theme_form = forms.Theme_Form(request.form)

    if request.method == 'POST' and theme_form.validate():
        tema = theme_form.theme.data

        theme = Theme(tema)

        db.session.add(theme)
        db.session.commit()

        flash('Tema creado')
        return redirect(url_for('temas'))

    title = 'Crear Tema'
    return render_template('crear_tema.html', form = theme_form, title = title)

@app.route('/favoritos')
def favoritos():
    favoritos = Favorito.query.join(File).add_columns(Favorito.user_id, Favorito.file_id, File.titulo, File.descripcion, File.archivo, File.likes, File.dislikes, File.materia_id)
    current_user = session['user_id']

    likes = Like.query.join(File).add_columns(Like.user_id, File.titulo, Like.like)
    like = []
    dislike = []

    for file in likes:
        if file.user_id == current_user:
            if file.like == 1:
                like.append(file.titulo)
            else:
                dislike.append(file.titulo)

    for file in favoritos:
        if file.dislikes == 6:
            return redirect(url_for('borrar_archivo', file_id = file.id))

    title = 'Favoritos'
    return render_template('favoritos.html', title = title, favoritos = favoritos, current_user = current_user, like = like, dislike = dislike)

@app.route('/like/<int:file_id>')
@app.route('/like/<int:file_id>/<origin>')
def like(file_id, origin = 'files'):
    likes = Like.query.all()
    archivo = File.query.filter_by(id = file_id).first()

    if likes:
        for like in likes:
            if like.user_id == session['user_id'] and like.file_id == file_id:
                archivo.likes = archivo.likes + 1
                archivo.dislikes = archivo.dislikes - 1
                like.like = 1
                like.dislike = 0
                db.session.commit()

                if origin == 'fav':
                    return redirect(url_for('favoritos'))
                else:
                    return redirect(url_for('archivos'))

        nuevo_like = Like(file_id, 1, 0, session['user_id'])
        archivo.likes = archivo.likes + 1
        db.session.add(nuevo_like)
        db.session.commit()

        if origin == 'fav':
            return redirect(url_for('favoritos'))
        else:
            return redirect(url_for('archivos'))

    else:
        nuevo_like = Like(file_id, 1, 0, session['user_id'])
        archivo.likes = archivo.likes + 1
        db.session.add(nuevo_like)
        db.session.commit()

    if origin == 'fav':
        return redirect(url_for('favoritos'))
    else:
        return redirect(url_for('archivos'))

@app.route('/like_eliminar/<int:file_id>')
@app.route('/like_eliminar/<int:file_id>/<origin>')
def like_eliminar(file_id, origin = 'files'):
    likes = Like.query.all()
    archivo = File.query.filter_by(id = file_id).first()

    for like in likes:
        if like.user_id == session['user_id'] and like.file_id == file_id:
            like_id = like.id

    lik = Like.query.get(like_id)
    db.session.delete(lik)
    archivo.likes = archivo.likes - 1
    db.session.commit()

    if origin == 'fav':
        return redirect(url_for('favoritos'))
    else:
        return redirect(url_for('archivos'))

@app.route('/dislike/<int:file_id>')
@app.route('/dislike/<int:file_id>/<origin>')
def dislike(file_id, origin = 'files'):
    likes = Like.query.all()
    archivo = File.query.filter_by(id = file_id).first()

    if likes:
        for like in likes:
            if like.user_id == session['user_id'] and like.file_id == file_id:
                archivo.likes = archivo.likes - 1
                archivo.dislikes = archivo.dislikes + 1
                like.like = 0
                like.dislike = 1
                db.session.commit()

                if origin == 'fav':
                    return redirect(url_for('favoritos'))
                else:
                    return redirect(url_for('archivos'))

        nuevo_like = Like(file_id, 0, 1, session['user_id'])
        archivo.dislikes = archivo.dislikes + 1
        db.session.add(nuevo_like)
        db.session.commit()

        if origin == 'fav':
            return redirect(url_for('favoritos'))
        else:
            return redirect(url_for('archivos'))

    else:
        nuevo_like = Like(file_id, 0, 1, session['user_id'])
        archivo.dislikes = archivo.dislikes + 1
        db.session.add(nuevo_like)
        db.session.commit()

    if origin == 'fav':
        return redirect(url_for('favoritos'))
    else:
        return redirect(url_for('archivos'))

@app.route('/dislike_eliminar/<int:file_id>')
@app.route('/dislike_eliminar/<int:file_id>/<origin>')
def dislike_eliminar(file_id, origin = 'files'):
    likes = Like.query.all()
    archivo = File.query.filter_by(id = file_id).first()

    for like in likes:
        if like.user_id == session['user_id'] and like.file_id == file_id:
            like_id = like.id

    lik = Like.query.get(like_id)
    db.session.delete(lik)
    archivo.dislikes = archivo.dislikes - 1
    db.session.commit()

    if origin == 'fav':
        return redirect(url_for('favoritos'))
    else:
        return redirect(url_for('archivos'))

@app.route('/favorito/<int:file_id>')
def favorito(file_id, origin = 'files'):
    favorito = Favorito(session['user_id'], file_id)
    db.session.add(favorito)
    db.session.commit()

    if origin == 'fav':
        return redirect(url_for('favoritos'))
    else:
        return redirect(url_for('archivos'))

@app.route('/favorito_eliminar/<int:file_id>')
@app.route('/favorito_eliminar/<int:file_id>/<origin>')
def favorito_eliminar(file_id, origin = 'files'):
    favoritos = Favorito.query.all()
    current_user = session['user_id']

    for file in favoritos:
        if file.user_id == current_user and file.file_id == file_id:
            fav_id = file.id

    fav = Favorito.query.get(fav_id)
    db.session.delete(fav)
    db.session.commit()

    if origin == 'fav':
        return redirect(url_for('favoritos'))
    else:
        return redirect(url_for('archivos'))

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.run(port = 5000)
