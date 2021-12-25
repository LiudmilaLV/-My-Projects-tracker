from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError, NumberRange, Optional
from datetime import datetime
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
            raise ValidationError('This name is already taken. Please, choose another name.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already taken. Please, choose another name.')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
    
class AddProjectForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(), Length(min=1, max=30)])
    goal = IntegerField('Weekly Goal (optional)', render_kw={"placeholder": "10"}, validators=[Optional()])
    notes = StringField('Notes (optional)', render_kw={"placeholder": "description"})
    submit = SubmitField('Add New Project')
    
class EntryForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today)
    duration = IntegerField('Duration (at least 1 minute)', default=1,validators=[DataRequired(), NumberRange(min=1, max=None, message='Enter atleast 1 minute')])
    project = HiddenField(default="{{ current_project.id }}")
    submit = SubmitField('Add Time to the Project')

class EditProjectForm(FlaskForm):
    project_name = StringField('Edit Project Name', validators=[DataRequired(), Length(min=1, max=30)])
    goal = IntegerField('Weekly Goal (optional)', render_kw={"placeholder": "10"}, validators=[Optional()])
    notes = StringField('Notes (optional)', render_kw={"placeholder": "description"})
    submit = SubmitField('Submit Changes')
    
class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset password request')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')