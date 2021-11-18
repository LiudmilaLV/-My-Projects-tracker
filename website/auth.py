from flask import Blueprint, render_template, flash, redirect, url_for
from werkzeug.utils import redirect
from .models import User
from . import db, bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from .forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash(f'Account for {form.name.data} successfully created!', category='success')
        return redirect(url_for('views.home'))
    return render_template('sign_up.html', form=form)

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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!', category='info')
    return redirect(url_for('auth.login'))
