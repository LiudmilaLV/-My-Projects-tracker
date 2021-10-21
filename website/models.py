from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    projects = db.relationship('Project', backref='owner')
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.projects}')"
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(1000), nullable=False, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entries = db.relationship('Entry')
    
    def __repr__(self):
        return f"User('{self.project_name}')"
        
    
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=func.current_date(), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    def __repr__(self):
        return f"User('{self.date}', '{self.duration}')"