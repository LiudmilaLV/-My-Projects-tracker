from flask import Blueprint, render_template, flash, redirect, url_for
from werkzeug.utils import redirect
from .models import User
from . import db, bcrypt, mail
from flask_login import login_user, login_required, logout_user, current_user
from .forms import RegistrationForm, LoginForm
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime
from .emails import confirm_mail_text

auth = Blueprint('auth', __name__)

def generate_confirmation_token(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email

# Get data via sing-up form for creating a new user
@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password, confirmed=False)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        send_confirmation_email(new_user.email)
        flash(f'Email confirmation link has been sent to {new_user.email}. Please check your email.', category='info')
        return redirect(url_for('views.home'))
    return render_template('sign_up.html', form=form)

# Email with a link for email confirmation
def send_confirmation_email(email):
    token = generate_confirmation_token(email)
    msg = Message('Email confirmation', recipients=[email])
    msg.html = confirm_mail_text(token)
    mail.send(msg)

# Url for email confirmation
@auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is expired. Try to sign up again', category='warning')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
        return redirect(url_for('auth.login'))
    else:
        user.confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash(f'Account for {user.name} successfully confirmed!', category='success')
    return redirect(url_for('views.home'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('views.home'))
    flash('Please confirm your account!', category='warning')
    return render_template('unconfirmed.html')

@auth.route('/resend')
@login_required
def resend_confirmation():
    send_confirmation_email(current_user.email)
    flash('A new confirmation email has been sent.', category='info')
    return redirect(url_for('auth.unconfirmed'))

# Implementation of login function
@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = LoginForm()
    if form.validate_on_submit():  
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):        
            flash('You logged in successfully!', category='success')
            login_user(user, remember=form.remember.data)            
            return redirect(url_for('views.home')) 
        else:
            flash('Login unsuccessful. Please check email and password', category='warning')    
    return render_template('login.html', form=form, user=current_user)

# Logout user
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!', category='info')
    return redirect(url_for('views.welcome'))
