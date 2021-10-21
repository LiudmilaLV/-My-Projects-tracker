from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.utils import redirect
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from .forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            new_user = User(email=form.email.data, name=form.name.data, password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(f'Account for {form.name.data} successfully created!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash('Email already exists.', category='warning')
    return render_template('sign_up.html', form=form)

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  
        user = User.query.filter_by(email=form.email.data).first()
        if user:        
            if check_password_hash(user.password, form.password.data):
                flash('You logged in successfully!', category='success')
                login_user(user, remember=True)            
                return redirect(url_for('views.home')) 
            else:
                flash('Incorrect password.', category='warning')
        else:
            flash('Email doesn\'t exist', category='warning')       
    return render_template('login.html', form=form, user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!', category='info')
    return redirect(url_for('auth.login'))
