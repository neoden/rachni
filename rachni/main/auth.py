from bson.objectid import ObjectId
from flask import url_for, render_template, flash, request, redirect
from flask.ext.login import UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
import wtforms.validators as v
from sqlalchemy.orm.exc import NoResultFound

from rachni.core import mongo, login_manager, db
from rachni.main.models import User

from . import mod


@login_manager.user_loader
def load_user(user_id):  
    return User.query.get(user_id)


class LoginForm(Form):
    email = StringField('Email', validators=[v.required()])
    password = PasswordField('Password', validators=[v.required()])


@mod.route('/login', methods=['GET', 'POST'])
def login():  
    form = LoginForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if user and User.validate_login(user.password_hash, form.password.data):
                login_user(user)
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
                user = User.query.filter_by(email=form.email.data).first()
                if user:
                    flash("User with this email is already registered", category="warning")
                else:
                    user = User(
                        email=form.email.data,
                        password_hash=generate_password_hash(form.password.data),
                        name=form.nickname.data
                    )
                    db.session.add(user)
                    db.session.commit()

                    login_user(user)
                    flash("Logged in successfully", category='success')

                    return redirect(request.args.get("next") or url_for('.index'))

    return render_template('register.html', form=form)