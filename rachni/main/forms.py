from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
import wtforms.validators as v


class LoginForm(Form):
    email = StringField('Email', validators=[v.required()])
    password = PasswordField('Password', validators=[v.required()])


class RegisterForm(Form):
    nickname = StringField('Nickname', validators=[v.required()])
    email = EmailField('Email', validators=[v.required()])
    password = PasswordField('Password', validators=[v.required()])
    password2 = PasswordField('Password2', validators=[v.required()])
