from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import selectin_polymorphic
from flask_sqlalchemy import SQLAlchemy
from .models import User, Project, Entry
from . import db
from .forms import AddProjectForm, EntryForm

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST']) 
@login_required
def home():
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
    return render_template("home.html", user=current_user, project_form=project_form)

@views.route('project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project(project_id):
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    entry_form = EntryForm()       
    if entry_form.validate_on_submit():    
        new_entry = Entry(date=entry_form.date.data, duration=entry_form.duration.data, project_id=current_project.id)
        db.session.add(new_entry)
        db.session.commit()
        flash(f'{entry_form.duration.data} minutes added to the project!', category='success')
    return render_template("project.html", user=current_user, project_id=current_project.id, name=current_project.project_name, notes=current_project.notes, entry_form=entry_form)