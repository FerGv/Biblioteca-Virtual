#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
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
import forms

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['UPLOAD_FOLDER'] = 'Archivos/'
csrf = CsrfProtect()

@app.before_request
def before_request():
    if 'username' not in session and request.endpoint in ['index', 'upload', 'archivos']:
        return redirect(url_for('login'))
    elif 'username' in session and request.endpoint in ['login', 'registro']:
        return redirect(url_for('index'))

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/registro', methods = ['GET', 'POST'])
def registro():
    create_form = forms.Login_Form(request.form)

    if request.method == 'POST' and create_form.validate():
        username = create_form.user.data
        password = create_form.pwd.data

        user = User(username, password)

        db.session.add(user)
        db.session.commit()

        session['username'] = username
        return redirect(url_for('index'))
    else:
        print "Error"

    return render_template('create.html', form = create_form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = forms.Login_Form(request.form)

    if request.method == 'POST' and login_form.validate():
        username = login_form.user.data
        password = login_form.pwd.data

        user = User.query.filter_by(username = username).first()

        if user is not None and user.verify_password(password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('error_message')

    return render_template('login.html', form = login_form)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
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
            return redirect(url_for('archivos'))
    else:
        return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/archivos')
def archivos():
    mypath = '/home/fer_gv/GitHub/Biblioteca-Virtual/Archivos/'
    archivos = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

    return render_template('archivos.html', archivos = archivos)

@app.route('/borrar_archivo/<filename>')
def borrar_archivo():
    mypath = '/home/fer_gv/GitHub/Biblioteca-Virtual/Archivos/'
    os.remove(os.path.join(mypath, filename))

    return redirect(url_for('archivos'))

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.run(port = 5000)
