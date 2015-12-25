from itertools import chain
from bson.objectid import ObjectId
from flask import render_template, flash, abort
from flask.ext.login import login_required, current_user

from rachni.core import mongo

from . import mod

@mod.route('/')
def index():
    return render_template('index.html')


@mod.route('/channel/<id>')
def channel(id):
    channel_id = ObjectId(id)
    if channel_id in chain([current_user.channels['direct']], current_user.channels['group']):
        channel = mongo.db.channels.find_one_or_404({'_id': channel_id})
        return render_template('index.html', channel=channel)
    else:
        abort(404)