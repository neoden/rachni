from rachni.core import db
from flask.ext.login import UserMixin
from werkzeug.security import check_password_hash


channel_users_table = db.Table('channel_users', db.metadata,
    db.Column('channel_id', db.ForeignKey('channels.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
    db.Column('user_id', db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(255))

    channels = db.relationship('Channel', secondary=channel_users_table, back_populates='users')

    def get_id(self):
        return self.id

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    def __repr__(self):
        return '<User %d:%s>' % (self.id or 0, self.name)


class Channel(db.Model):
    __tablename__ = 'channels'

    id = db.Column(db.Integer(), primary_key=True)
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    users = db.relationship('User', secondary=channel_users_table, back_populates='channels')

    def __repr__(self):
        return '<Channel %d:%s>' % (self.id or 0, self.name)


class Message(db.Model):
    __tablename__ = 'messages'

    ts = db.Column(db.DateTime, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False, primary_key=True)
    text = db.Column(db.Text)