from itertools import chain
from bson.objectid import ObjectId
from flask import render_template, flash, abort, request, redirect, url_for
from flask.ext.login import login_required, current_user
from flask_wtf import Form
from wtforms import StringField, PasswordField
import wtforms.validators as v

from rachni.core import mongo

from . import mod


@mod.route('/')
def index():
    form = CreateChannelForm()
    return render_template('index.html', create_form=form)


@login_required
@mod.route('/channel/<id>/')
def channel(id):
    form = CreateChannelForm()
    channel_id = ObjectId(id)
    if channel_id in current_user.channels:
        channel = mongo.db.channels.find_one_or_404({'_id': channel_id})
        return render_template('index.html', channel=channel, create_form=form)
    else:
        abort(404)


class CreateChannelForm(Form):
    name = StringField('Name', validators=[v.required()])


@login_required
@mod.route('/channel/create/', methods=['POST'])
def create_channel():
    form = CreateChannelForm(request.form)

    if form.validate_on_submit():
        channel = {'name': request.form['name']}
        channel_id = mongo.db.channels.insert_one(channel).inserted_id
        mongo.db.users.find_one_and_update(
            {'_id': current_user.get_id()}, 
            {'$push': {'channels': channel_id}})
        channel['_id'] = channel_id
        current_user.channels.append(channel_id)
        return redirect(url_for('.channel', id=channel_id))
    else:
        return redirect(url_for('.index'))


@login_required
@mod.route('/channel/<id>/leave/', methods=['POST'])
def leave_channel(id):
    pass


@login_required
@mod.route('/channel/<id>/invite/')
def invite_to_channel(id):
    return url_for('.join_channel', token='+{}'.format(id), _external=True)


@login_required
@mod.route('/join/<token>/')
def join_channel(token):
    channel_id = ObjectId(token[1:])
    mongo.db.users.find_one_and_update(
        {'_id': current_user.get_id()}, 
        {'$push': {'channels': channel_id}})
    current_user.channels.append(channel_id)

    return redirect(url_for('.channel', id=channel_id))