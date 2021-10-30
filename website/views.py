from flask import Blueprint, render_template, flash, abort, url_for
from werkzeug.utils import redirect
from flask_login import login_required, current_user
from .models import User, Project, Entry
from . import db
from .forms import AddProjectForm, EditProjectForm, EntryForm
from sqlalchemy import and_

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