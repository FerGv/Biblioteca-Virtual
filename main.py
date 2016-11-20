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

from helper import date_format

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['UPLOAD_FOLDER'] = 'Archivos/'
csrf = CsrfProtect()

@app.before_request
def before_request():
    if 'username' not in session and request.endpoint in ['upload', 'archivos', 'uploads', 'borrar_archivo', 'comentarios', 'bienvenida', 'temas', 'crear_tema', 'logout', 'favoritos', 'like', 'dislike', 'favorito']:
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
#    mypath = '/home/fer_gv/GitHub/Biblioteca-Virtual/Archivos/'
#    archivos = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

    archivos = File.query.all()

    title = 'Biblioteca'
    return render_template('archivos.html', archivos = archivos, title = title)

@app.route('/borrar_archivo/<filename>')
def borrar_archivo(filename):
    mypath = '/home/fer_gv/GitHub/Biblioteca-Virtual/Archivos/'
    os.remove(os.path.join(mypath, filename))

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

@app.route('/favoritos', methods = ['GET', 'FORM'])
def favoritos():
    title = 'Favoritos'
    return render_template('favoritos.html', title = title)

@app.route('/like/<int:id>', methods = ['GET', 'FORM'])
def like(id):
    archivo = File.query.filter_by(id = id).first()
    archivo.likes = archivo.likes + 1
    db.session.commit()

    return redirect(url_for('archivos'))

@app.route('/dislike/<int:id>', methods = ['GET', 'FORM'])
def dislike(id):
    archivo = File.query.filter_by(id = id).first()
    archivo.dislikes = archivo.dislikes + 1
    db.session.commit()

    return redirect(url_for('archivos'))

@app.route('/favorito/<int:id>', methods = ['GET', 'FORM'])
def favorito(id):

    return redirect(url_for('archivos'))

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.run(port = 5000)
