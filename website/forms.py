from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.core import IntegerField
from wtforms.fields.html5 import DateField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError, NumberRange
from .models import User
from . import db

class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('This name is already taken. Please choose another name.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This name is already taken. Please choose another name.')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
    
class AddProjectForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(), Length(min=1, max=30)])
    notes = StringField('Notes')
    submit = SubmitField('Add Project')
    
class EntryForm(FlaskForm):
    date = DateField('Date')
    duration = IntegerField('Duration (in minutes)', validators=[DataRequired(), NumberRange(min=1, max=None, message='Enter atleast 1 minute')])
    project = HiddenField(default="{{ current_project.id }}")
    submit = SubmitField('Add Time to the Project')    
