from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import selectin_polymorphic
from .models import Project
from . import db
from .forms import AddProjectForm

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST']) 
@login_required
def home():
    form = AddProjectForm()
    if form.validate_on_submit():    
        user = Project.query.filter(Project.project_name==form.project_name.data, Project.user_id==current_user.id).first()
        if user:
            flash('Project already exists! Use another name', category='warning')
        else:
            new_project = Project(project_name = form.project_name.data, notes = form.notes.data, user_id = current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project added!', category='success')        
    return render_template("home.html", form=form, user=current_user)