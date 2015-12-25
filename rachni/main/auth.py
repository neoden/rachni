import uuid
from flask import url_for, render_template, flash, request, redirect
from flask.ext.login import UserMixin, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
import wtforms.validators as v

from rachni.core import mongo, login_manager

from . import mod


class User(UserMixin):
    def __init__(self, user):
        for k, v in user.items():
            setattr(self, k, v)

    def get_id(self):
        return self._id

    def todict(self):
        return self.__dict__

    def websocket_uri(self):
        return 'ws://127.0.0.1:5678/{}'.format(self.uuid)

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)


@login_manager.user_loader
def load_user(username):  
    u = mongo.db.users.find_one({"_id": username})
    if not u:
        return None
    return User(u)


class LoginForm(Form):
    email = StringField('Email', validators=[v.required()])
    password = PasswordField('Password', validators=[v.required()])


@mod.route('/login', methods=['GET', 'POST'])
def login():  
    form = LoginForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = mongo.db.users.find_one({"_id": form.email.data})

            if user and User.validate_login(user['password'], form.password.data):
                user_obj = User(user)
                login_user(user_obj)
                flash("Logged in successfully", category='success')
                return redirect(request.args.get("next") or url_for('.index'))
            else:
                flash("Wrong username or password", category='error')

    return render_template('login.html', form=form)


@mod.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.login'))


class RegisterForm(Form):
    nickname = StringField('Nickname', validators=[v.required()])
    email = EmailField('Email', validators=[v.required()])
    password = PasswordField('Password', validators=[v.required()])
    password2 = PasswordField('Password2', validators=[v.required()])


@mod.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.password.data != form.password2.data:
                flash("Passwords are not identical", category='error')
            else:
                user = mongo.db.users.find_one({"_id": form.email.data})
                if user:
                    flash("User with this email is already registered", category="warning")
                else:
                    user = {
                        '_id': form.email.data,
                        'password': generate_password_hash(form.password.data),
                        'nickname': form.nickname.data,
                        'uuid': uuid.uuid4().hex
                    }
                    mongo.db.users.insert_one(user)
                    user_obj = User(user)
                    login_user(user_obj)
                    flash("Logged in successfully", category='success')
                    return redirect(request.args.get("next") or url_for('.index'))

    return render_template('register.html', form=form)