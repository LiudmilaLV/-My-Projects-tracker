from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import selectin_polymorphic
from .models import Project
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
    entry_form = EntryForm()        
    return render_template("home.html", user=current_user, project_form=project_form, entry_form=entry_form)