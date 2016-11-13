 #!/usr/bin/python
 # -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import validators

class Login_Form(Form):
    user = StringField('Usuario', [validators.Required(message='Este campo es obligatorio.'), validators.length(min=4, max=25, message='Ingrese un usuario valido.')])
    pwd = PasswordField('Password', [validators.Required(message='Este campo es obligatorio')])
