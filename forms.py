 #!/usr/bin/python
 # -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import TextAreaField
from wtforms import validators

from model import User

class Login_Form(Form):
    user = StringField('Usuario', [validators.Required(message='Este campo es obligatorio.'), validators.length(min=4, max=25, message='4 - 25 caracteres.')])
    pwd = PasswordField('Password', [validators.Required(message='Este campo es obligatorio')])

class User_Form(Form):
    user = StringField('Usuario', [validators.Required(message='Este campo es obligatorio.'), validators.length(min=4, max=25, message='4 - 25 caracteres.')])
    pwd = PasswordField('New_Password', [validators.Required(message='Este campo es obligatorio')])
    pwd3 = PasswordField('Current_Password', [validators.Required(message='Este campo es obligatorio')])

    def validate_user(form, field):
        user = field.data
        usuario = User.query.filter_by(username = user).first()

        if usuario is not None:
            raise validators.ValidationError('Usuario ya existente')

class Create_Form(Form):
    user = StringField('Usuario', [validators.Required(message='Este campo es obligatorio.'), validators.length(min=4, max=25, message='4 - 25 caracteres.')])
    pwd = PasswordField('Password', [validators.Required(message='Este campo es obligatorio')])

    def validate_user(form, field):
        user = field.data
        usuario = User.query.filter_by(username = user).first()

        if usuario is not None:
            raise validators.ValidationError('Usuario ya existente')

class Comment_Form(Form):
    comment = TextAreaField('Comentario', [validators.Required(message='Este campo es obligatorio')])

class Theme_Form(Form):
    theme = TextAreaField('Tema', [validators.Required(message='Este campo es obligatorio')])

class Materia_Form(Form):
    materia = StringField('Materia', [validators.Required(message='Este campo es obligatorio')])

class UploadFile_Form(Form):
    titulo = StringField('Titulo', [validators.Required(message='Este campo es obligatorio.'), validators.length(min=4, max=25, message='4 - 25 caracteres.')])
    descripcion = TextAreaField('Descripcion', [validators.Required(message='Este campo es obligatorio')])
