from flask import Blueprint, render_template, flash, abort, url_for
from werkzeug.utils import redirect
from flask_login import login_required, current_user
from .models import User, Project, Entry
from . import db, mail, bcrypt
from .forms import AddProjectForm, EditProjectForm, EntryForm, ResetRequestForm, ResetPasswordForm
from sqlalchemy import and_
from flask_mail import Message
import json
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST']) 
@login_required
def home():
    current_day = datetime.now().date()
    a_month_ago = current_day - timedelta(days=30)
    recent_projects = (db.session.query(Project.project_name, db.func.sum(Entry.duration))
                        .join(Entry)
                        .filter(and_(Project.owner==current_user, Entry.date.between(a_month_ago, current_day)))
                        .group_by(Project.project_name)
                        .all()
                        )
    user_projects_labels = []
    user_projects_data = []
    for project_name, project_duration in recent_projects:
        user_projects_labels.append(project_name)
        user_projects_data.append(project_duration)
        
    user_projects_labels = json.dumps(user_projects_labels)
    user_projects_data = json.dumps(user_projects_data)
    
    project_form = AddProjectForm()
    if project_form.validate_on_submit():    
        user = Project.query.filter(Project.project_name==project_form.project_name.data, Project.user_id==current_user.id).first()
        if user:
            flash('Project already exists! Use another name', category='warning')
        else:
            new_project = Project(project_name = project_form.project_name.data, notes = project_form.notes.data, user_id = current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project added!', category='success')
    return render_template("home.html", user=current_user, project_form=project_form, user_projects_labels=user_projects_labels, user_projects_data=user_projects_data)

@views.route('project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project(project_id):
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    last10 = Entry.query.join(Project).filter(and_(Entry.project_id==project_id, Project.owner==current_user)).order_by(Entry.date.desc()).limit(10).all()
    entry_form = EntryForm()       
    if entry_form.validate_on_submit():    
        new_entry = Entry(date=entry_form.date.data, duration=entry_form.duration.data, project_id=current_project.id)
        db.session.add(new_entry)
        db.session.commit()
        flash(f'{entry_form.duration.data} minutes added to the project!', category='success')
        return redirect(url_for('views.project', project_id=current_project.id))
    edit_project_form = EditProjectForm()
    edit_project_form.project_name.data = current_project.project_name
    edit_project_form.notes.data = current_project.notes
    return render_template("project.html", user=current_user, project_id=current_project.id, name=current_project.project_name, notes=current_project.notes, entry_form=entry_form, edit_project_form=edit_project_form, last10=last10)

@views.route('project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    if current_project.owner != current_user:
        abort(403)
    current_project_entries=Entry.query.filter(Entry.project_id==project_id).all()
    for entry in current_project_entries:
        db.session.delete(entry)
    db.session.delete(current_project)
    db.session.commit()
    flash(f'Project "{current_project.project_name} has been deleted!', category='success')
    return redirect(url_for('views.home'))

@views.route('project/<int:project_id>/edit', methods=['POST'])
@login_required
def edit_project(project_id):
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    if current_project.owner != current_user:
        abort(403)
    edit_project_form = EditProjectForm()
    if edit_project_form.validate_on_submit():
        current_project.project_name = edit_project_form.project_name.data
        current_project.notes = edit_project_form.notes.data
        db.session.commit()
        flash('Changes has been saved!', category='success')
        return redirect(url_for('views.project', project_id=current_project.id)) 
    
@views.route('project/delete/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    current_entry = Entry.query.join(Project).filter(and_(Entry.id==entry_id, Project.owner==current_user)).first_or_404(entry_id)
    db.session.delete(current_entry)
    db.session.commit()
    flash(f'{current_entry.duration} minutes has been deleted!', category='success')
    return redirect(url_for('views.project', project_id=current_entry.project_id))

def send_reset_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request', sender='yourprojecttracker@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('views.reset_token', token=token, _external=True)}
    
If you did not make this password reset request, please ignore this email.
'''
    mail.send(msg)

@views.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_mail(user)
            flash('Reset request has been sent. Check you email.', category='info')
            return redirect(url_for('auth.login'))
    return render_template('reset_request.html', form=form)

@views.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = User.verify_token(token)
    if user is None:
        flash('The reset password link is expired', category='warning')
        return redirect(url_for('views.reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password has been updated! You are now able to log in.', category='success')
        return redirect(url_for('auth.login'))
    return render_template('change_password.html', form=form)