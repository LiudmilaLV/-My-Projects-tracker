from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Project
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST']) 
@login_required
def home():
    if request.method == 'POST':
        # form = AddProject
        project_name = request.form.get('project_name')
        notes = request.form.get('notes')
        if len(project_name) < 1:
            flash('Name is too short!', category='warning')
        elif  Project.query.filter_by(project_name = project_name).first():
            flash('Project elready exists!', category='warning')
        else:
            new_project = Project(project_name = project_name, notes = notes, user_id = current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project added!', category='success')
        
    return render_template("home.html", user=current_user)