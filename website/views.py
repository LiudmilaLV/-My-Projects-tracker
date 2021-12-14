from flask import Blueprint, render_template, flash, abort, url_for, request
from werkzeug.utils import redirect
from flask_login import login_required, current_user
from .models import User, Project, Entry
from . import db, mail, bcrypt
from .forms import AddProjectForm, EditProjectForm, EntryForm, ResetRequestForm, ResetPasswordForm
from sqlalchemy import extract, and_, or_
from flask_mail import Message
import json
from datetime import datetime, timedelta
import math

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST']) 
@login_required
def home():
    # Getting data for pie-chart(recent projects)
    current_day = datetime.now().date()
    a_month_ago = current_day - timedelta(days=30)
    recent_projects = (db.session.query(Project.project_name, db.func.sum(Entry.duration))
                        .join(Entry)
                        .filter(and_(Project.owner==current_user, Entry.date.between(a_month_ago, current_day)))
                        .group_by(Project.project_name)
                        .all()
                        )
    user_projects_l = []
    user_projects_d = []
    for project_name, project_duration in recent_projects:
        user_projects_l.append(project_name)
        user_projects_d.append(project_duration)
    no_entries_yet = True
    if user_projects_d:
        no_entries_yet = False
    user_projects_labels = json.dumps(user_projects_l)
    user_projects_data = json.dumps(user_projects_d)
    
    project_form = AddProjectForm()
    if project_form.validate_on_submit():    
        user = Project.query.filter(Project.project_name==project_form.project_name.data, Project.user_id==current_user.id).first()
        if user:
            flash('Project already exists! Use another name', category='warning')
        else:
            new_project = Project(project_name = project_form.project_name.data, goal = project_form.goal.data, notes = project_form.notes.data, user_id = current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('New project added!', category='success')
    #else:
        #flash('Project not added. Please, fill the fields correctly.', category='danger')
    return render_template("home.html", 
                            user = current_user,
                            project_form = project_form,
                            user_projects_labels = user_projects_labels, user_projects_data = user_projects_data,
                            no_entries_yet = no_entries_yet,
                            )

@views.route('project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project(project_id):
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    if current_project.owner != current_user:
        abort(403)
    last5 = Entry.query.join(Project).filter(and_(Entry.project_id==current_project.id, Project.owner==current_user)).order_by(Entry.timestamp.desc()).limit(5).all()
    current_day = datetime.now().date()
    
    # Getting data for a "this week" chart
    a_week_ago = current_day - timedelta(days=7)
    this_week_enries = (db.session.query(db.func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, Entry.date.between(a_week_ago, current_day)))
                        .group_by(Entry.date)
                        .order_by(Entry.date)
                        .all()
                        )
    this_week_d =[]
    this_week_l =[]
    for minute, date in this_week_enries:
        this_week_d.append(minute)
        this_week_l.append(date.strftime("%B %d"))
    thisweek_summ_hours = round((sum(this_week_d) / 60))
    this_week_data = json.dumps(this_week_d)
    this_week_labels = json.dumps(this_week_l)
    
    # Getting data for a "this month" chart
    a_month_ago = current_day - timedelta(days=30)
    this_month_enries = (db.session.query(db.func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, Entry.date.between(a_month_ago, current_day)))
                        .group_by(Entry.date)
                        .order_by(Entry.date)
                        .all()
                        )
    this_month_d = []
    this_month_l = []
    for minute, date in this_month_enries:
        this_month_d.append(math.ceil(minute / 60))
        this_month_l.append(date.strftime("%b %e"))
    thismonth_summ_hours = sum(this_month_d)
    this_month_data = json.dumps(this_month_d)
    this_month_labels = json.dumps(this_month_l)
    
    # Getting data for a "last 12weeks" chart
    a_day_91_days_ago = current_day - timedelta(days=91)
    this_12weeks_entries = []
    this_12weeks_entries = (db.session.query(db.func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, Entry.date.between(a_day_91_days_ago, current_day)))
                        .group_by(extract('week', Entry.date))
                        .order_by(Entry.date)
                        .all()
                        )
    this_12weeks_d = []
    this_12weeks_l = []
    for minute, date in this_12weeks_entries:
        this_12weeks_d.append(math.ceil(minute / 60))
        this_12weeks_l.append(date.strftime("%b %e") + " - " + (date + timedelta(days=7)).strftime("%b %e"))
    this_12weeks_labels = json.dumps(this_12weeks_l)
    
    # Hours per week (shows at "This 12weeks" chart)
    week_goal = current_project.goal
    this_12weeks_d_goal = [week_goal]
    this_12weeks_p = []
    if this_12weeks_d != []:
        this_12weeks_p =[this_12weeks_d[0]]
    for week, _ in enumerate(this_12weeks_d):
        if week == 0:
            continue
        this_12weeks_p.append(this_12weeks_d[week] + this_12weeks_p[week - 1])
        this_12weeks_d_goal.append(week_goal*(week+1))    
    this_12weeks_progress = json.dumps(this_12weeks_p)
    this_12weeks_data_goal = json.dumps(this_12weeks_d_goal)
    this12weeks_summ_hours = sum(this_12weeks_d)
    
    # Getting data for a "this year" chart
    year_now = datetime.now().year
    this_year_entries = (db.session.query(db.func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, extract('year', Entry.date)==year_now))
                        .group_by(extract('month', Entry.date))
                        .order_by(Entry.date)
                        .all()
                        )
    this_year_d = []
    this_year_l = []
    for minute, date in this_year_entries:
        this_year_d.append(math.ceil(minute / 60))
        this_year_l.append(date.strftime("%B"))
    thisyear_summ_hours = sum(this_year_d)
    this_year_data = json.dumps(this_year_d)
    this_year_labels = json.dumps(this_year_l)
    
    # Getting data for a "all time" chart
    alltime_entries = (db.session.query(db.func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id))
                        .group_by(extract('month', Entry.date))
                        .order_by(Entry.date)
                        .all()
                        )
    alltime_d = []
    alltime_l = []
    for minute, date in this_year_entries:
        alltime_d.append(math.ceil(minute / 60))
        alltime_l.append(date.strftime("%B, %Y"))
    alltime_summ_hours = sum(alltime_d)
    alltime_data = json.dumps(alltime_d)
    alltime_labels = json.dumps(alltime_l)
    
    return render_template("project.html",
                            user = current_user, project_id = current_project.id,
                            name = current_project.project_name, notes = current_project.notes, week_goal = week_goal,
                            last5 = last5,
                            this_week_data = this_week_data, this_week_labels = this_week_labels,
                            this_month_data = this_month_data, this_month_labels = this_month_labels,
                            this_12weeks_data_goal = this_12weeks_data_goal,
                            this_12weeks_progress = this_12weeks_progress,
                            this_12weeks_labels = this_12weeks_labels,
                            this_year_data = this_year_data,
                            this_year_labels = this_year_labels,
                            alltime_data = alltime_data,
                            alltime_labels =alltime_labels,
                            thisweek_summ_hours = thisweek_summ_hours,
                            thismonth_summ_hours = thismonth_summ_hours,
                            this12weeks_summ_hours = this12weeks_summ_hours,
                            thisyear_summ_hours = thisyear_summ_hours,
                            alltime_summ_hours = alltime_summ_hours
                            )

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

@views.route('project/delete/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    current_entry = Entry.query.join(Project).filter(and_(Entry.id==entry_id, Project.owner==current_user)).first_or_404(entry_id)
    db.session.delete(current_entry)
    db.session.commit()
    plural = ''
    if current_entry.duration != 1:
            plural = 's'
    flash(f'{current_entry.duration} minute{plural} has been deleted!', category='success')
    return redirect(url_for('views.project', project_id=current_entry.project_id))

@views.route('project/<int:project_id>/addtime', methods=['GET','POST'])
@login_required
def add_time(project_id):
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    if current_project.owner != current_user:
        abort(403)
    entry_form = EntryForm()       
    if entry_form.validate_on_submit():    
        new_entry = Entry(date=entry_form.date.data, duration=entry_form.duration.data, project_id=current_project.id)
        db.session.add(new_entry)
        db.session.commit()
        plural = ''
        if entry_form.duration.data != 1:
            plural = 's'
        flash(f'{entry_form.duration.data} minute{plural} added to the project!', category='success')
        return redirect(url_for('views.project', project_id=current_project.id))
    return render_template('addtime.html', user = current_user, project_id=current_project.id, entry_form=entry_form)

@views.route('project/<int:project_id>/edit', methods=['GET','POST'])
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
    elif request.method == "GET":
        edit_project_form.project_name.data = current_project.project_name
        edit_project_form.notes.data = current_project.notes
    return render_template('edit_project.html', user = current_user, project_id=current_project.id, edit_project_form=edit_project_form)

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