from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    projects = db.relationship('Project')
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(1000), nullable=False, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entries = db.relationship('Entry')
    
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=func.current_date())
    duration = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))