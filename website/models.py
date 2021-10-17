from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String(100))
    date = db.Column(db.Date, default=func.current_date())
    duration = db.Column(db.Integer) # Minutes spent on project on particular project session
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    entries = db.relationship('Entry')