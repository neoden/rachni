from flask import url_for, render_template, flash, request, redirect
from flask.ext.login import UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash
from sqlalchemy.orm.exc import NoResultFound

from rachni.core import login_manager, db
from rachni.main.models import User
from rachni.main.forms import LoginForm, RegisterForm

from . import mod


@login_manager.user_loader
def load_user(user_id):  
    return User.query.get(user_id)


@mod.route('/login', methods=['POST'])
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

    return redirect(url_for('.index'))


@mod.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.index'))


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
