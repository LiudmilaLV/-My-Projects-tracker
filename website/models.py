from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.orm import backref
from sqlalchemy.sql.expression import null
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import current_app
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    confirmed = db.Column(db.Boolean)
    confirmed_on = db.Column(db.DateTime)
    projects = db.relationship('Project', backref='owner')

    def get_token(self, expires_sec=600):
        s = Serializer(
            current_app.config['SECRET_KEY'], expires_in=expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.projects}')"


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(30), nullable=False)
    goal = db.Column(db.Integer)
    notes = db.Column(db.String(1000), nullable=False, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entries = db.relationship('Entry')

    def __repr__(self):
        return f"Project('{self.project_name}')"


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date = db.Column(db.Date, default=func.current_date(), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)

    def __repr__(self):
        return f"Model('{self.date}', '{self.duration}')"
