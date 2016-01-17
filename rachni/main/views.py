import uuid
import json
from itertools import chain
from flask import render_template, flash, abort, request, redirect, url_for, jsonify, current_app
from flask.ext.login import login_required, current_user
from flask_wtf import Form
from wtforms import StringField, PasswordField
import wtforms.validators as v

from rachni.core import redis, db
from rachni.main.models import User, Channel

from rachni.main.forms import LoginForm

from . import mod


@mod.route('/')
def index():
    create_form = CreateChannelForm()
    login_form = LoginForm()
    return render_template('index.html', create_form=create_form, login_form=login_form)


@mod.route('/channel/<id>/')
@login_required
def channel(id):
    form = CreateChannelForm()
    channel = Channel.query.get_or_404(id)

    if channel in current_user.channels:
        return render_template('index.html', channel=channel, create_form=form)
    else:
        abort(404)


class CreateChannelForm(Form):
    name = StringField('Name', validators=[v.required()])


@mod.route('/channel/create/', methods=['POST'])
@login_required
def create_channel():
    form = CreateChannelForm(request.form)

    if form.validate_on_submit():
        channel = Channel(name=form.name.data)
        channel.users = [current_user]
        db.session.add(channel)
        db.session.commit()

        return redirect(url_for('.channel', id=channel.id))
    else:
        return redirect(url_for('.index'))


@mod.route('/channel/<id>/leave/', methods=['POST'])
@login_required
def leave_channel(id):
    pass


@mod.route('/channel/<id>/invite/')
@login_required
def invite_to_channel(id):
    channel = Channel.query.get_or_404(id)
    token = uuid.uuid4().hex
    redis.set('invite:' + token, channel.id, 60 * 60 * 24)    # TTL 24 hours
    return url_for('.join_channel', token=token, _external=True)


@mod.route('/join/<token>/')
@login_required
def join_channel(token):
    try:
        key = 'invite:' + token
        channel_id = int(redis.get(key))
        redis.delete(key)
        channel = Channel.query.get_or_404(channel_id)
        channel.users.append(current_user)
        db.session.commit()
    except (ValueError, TypeError):
        flash('Link is invalid', category='error')

    return redirect(url_for('.channel', id=channel_id))


@mod.route('/channel/<id>/connect')
@login_required
def connect_to_channel(id):
    channel = Channel.query.get_or_404(id)
    token = uuid.uuid4().hex
    payload = json.dumps({
        'current_channel': {
            'id': channel.id, 
            'name': channel.name
        },
        'channels': [{'id': c.id, 'name': c.name} for c in current_user.channels],
        'user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email
        }
    })
    redis.set('auth:' + token, payload, 60)      # TTL 1 minute

    websocket_uri = 'ws://{}:{}/{}'.format(
        current_app.config['HOSTNAME'],
        current_app.config['WEBSOCKET_PORT'],
        token)

    return jsonify(status='ok', websocket_uri=websocket_uri)