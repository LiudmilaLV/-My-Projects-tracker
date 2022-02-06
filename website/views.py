from flask import Blueprint, render_template, flash, abort, url_for, request
from werkzeug.utils import redirect
from flask_login import login_required, current_user
from .models import User, Project, Entry
from . import db, mail, bcrypt
from .forms import AddProjectForm, EditProjectForm, EntryForm, ResetRequestForm, ResetPasswordForm
from .helper import adjust_data, check_confirmed
from sqlalchemy import extract, and_
from sqlalchemy.sql import func
from flask_mail import Message
import json
from datetime import datetime, timedelta
from .emails import reset_email_text

views = Blueprint('views', __name__)

@views.route('/')
def welcome():
    return render_template('welcome.html')


@views.route('/home', methods=['GET', 'POST']) 
@login_required
@check_confirmed
def home():
    # Get data for pie-chart (for last 30 days projects)
    current_day = datetime.utcnow().date()
    a_day_30_days_ago = current_day - timedelta(days=30)
    recent_projects = (db.session.query(Project.project_name, db.func.sum(Entry.duration))
                        .join(Entry)
                        .filter(and_(Project.owner==current_user, Entry.date.between(a_day_30_days_ago, current_day)))
                        .group_by(Project.project_name)
                        .all()
                        )
    user_projects_l = []
    user_projects_d = []
    for project_name, minutes in recent_projects:
        user_projects_l.append(project_name)
        user_projects_d.append(round((minutes / 60),1))
    no_entries_yet = True
    if user_projects_d:
        no_entries_yet = False
    user_projects_labels = json.dumps(user_projects_l)
    user_projects_data = json.dumps(user_projects_d)
    
    # Get data from "Add new project form", if the button pressed = POST request sent
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

    return render_template("home.html", 
                            user = current_user,
                            project_form = project_form,
                            user_projects_labels = user_projects_labels, user_projects_data = user_projects_data,
                            no_entries_yet = no_entries_yet,
                            )


# Individual page with a particular project data
@views.route('project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def project(project_id):
    # Check page accessibility rights
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    if current_project.owner != current_user:
        abort(403)
        
    # Get last 5 queries made by the user to show in a table on the page
    last5 = Entry.query.join(Project).filter(and_(Entry.project_id==current_project.id, Project.owner==current_user)).order_by(Entry.timestamp.desc()).limit(5).all()
    current_day = datetime.now().date()
    
    # Get data for a "this week" chart
    last_monday = current_day - timedelta(days=current_day.weekday())
    current_week = last_monday.strftime("%b %e") + ' - ' + (last_monday + timedelta(days = 6)).strftime("%b %e")
    this_week_enries = (db.session.query(db.func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, Entry.date.between(last_monday, current_day)))
                        .group_by(Entry.date)
                        .order_by(Entry.date)
                        .all()
                        )
    this_week_d =[]
    this_week_l =[]
    for minute, date in this_week_enries:
        this_week_d.append(minute)
        this_week_l.append(date.strftime("%B %d"))
    thisweek_summ_hours = round((sum(this_week_d) / 60),1)
    this_week_data = json.dumps(this_week_d)
    this_week_labels = json.dumps(this_week_l)
    
    # Get data for a "Last 30 days" chart
    a_day_30_days_ago = current_day - timedelta(days=30)
    this_month_enries = (db.session.query(db.func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, Entry.date.between(a_day_30_days_ago, current_day)))
                        .group_by(Entry.date)
                        .order_by(Entry.date)
                        .all()
                        )
    this_month_d = []
    this_month_l = []
    for minute, date in this_month_enries:
        this_month_d.append(round((minute / 60),1))
        this_month_l.append(date.strftime("%b %e"))
    thismonth_summ_hours = round(sum(this_month_d),1)
    this_month_data = json.dumps(this_month_d)
    this_month_labels = json.dumps(this_month_l)

    
    # Get data for a "Last 12 weeks" chart from database 
    next_monday = current_day - timedelta(days=current_day.weekday()) + timedelta(days=7) 
    a_monday_84_days_ago = next_monday - timedelta(days=84)
    these_12weeks_entries = []
    these_12weeks_entries = (db.session.query(func.sum(Entry.duration), extract('week', Entry.date), extract('year', Entry.date))
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, Entry.date.between(a_monday_84_days_ago, next_monday)))
                        .group_by(extract('week', Entry.date))
                        .order_by(Entry.date)
                        .all()
                        )
    raw_these_12weeks_d = []
    these_12weeks_l = []
    raw_week_of_year_for_data = []
    add_to_adjacent = 0

    # If first few days of a year are recognized by database not as belonged to the first week of the year, but to a week 0,
    # in that case minutes worked on these days will be added to the last week of a previous year. 
    # Or to the first week of a new year, if the last week is not present on the "Last 12 Weeks" chart.
    week_52 = False
    for minute, week, year in these_12weeks_entries:
        if week == 0:
            add_to_adjacent = round((minute/ 60),1)
        else:
            if week == 52:
                week_52 = True
            raw_these_12weeks_d.append(round((minute/ 60),1))
            raw_week_of_year_for_data.append([week,year])
        
    if not week_52:
        for i, week_and_year in enumerate(raw_week_of_year_for_data):
            if 1 in week_and_year:
                buff = raw_these_12weeks_d.pop(i)
                buff = buff + add_to_adjacent
                raw_these_12weeks_d.insert(i, buff)
    else:
        for i, week_and_year in enumerate(raw_week_of_year_for_data):
            if 52 in week_and_year:
                buff = raw_these_12weeks_d.pop(i)
                buff = buff + add_to_adjacent
                raw_these_12weeks_d.insert(i, buff)
                
    week_of_year_for_data = raw_week_of_year_for_data.copy()
    
            
    # Get 12 labels for "Last 12 weeks" chart, counting from current week Monday
    last_monday = current_day - timedelta(days=current_day.weekday())
    reversed_12weeks_l = [last_monday.strftime("%b %e") + ' - ' + (last_monday + timedelta(days=6)).strftime("%b %e")]
    for week in range(1,12):
        reversed_12weeks_l.append((last_monday - timedelta(days = 7 * week)).strftime("%b %e") + ' - ' + (last_monday - timedelta(days =7 * week) + timedelta(days=6)).strftime("%b %e"))
    reversed_12weeks_l.reverse()
    these_12weeks_l = reversed_12weeks_l.copy()

    # Get numbers of weeks and years of those 12 labels got above
    week_of_year_for_labels = [[last_monday.isocalendar()[1], last_monday.isocalendar()[0]]]
    for week in range(1, len(these_12weeks_l)):
        week_of_year_for_labels.append([(last_monday - timedelta(days = 7 * week)).isocalendar()[1], (last_monday - timedelta(days = 7 * week)).isocalendar()[0]])
    week_of_year_for_labels.reverse()
    
    # Adjust data-set according to it's week labels by adding zeros to the skipped weeks without data:
    these_12weeks_d = adjust_data(week_of_year_for_data, raw_these_12weeks_d, week_of_year_for_labels)
    
    week_goal = 0
    # If hours per week Goal set(shows at "Last 12 Weeks" chart), additional data needed:
    # 1. Get the ideal expected progress line on the chart
    these_12weeks_d_goal = []
    # 2. Get the actual user progress line on the same chart
    these_12weeks_p = []
    if current_project.goal:
        goal = True
        week_goal = current_project.goal
        these_12weeks_d_goal = [week_goal]
        if these_12weeks_d:
            these_12weeks_p =[these_12weeks_d[0]]
        for week, _ in enumerate(these_12weeks_d):
            if week == 0:
                continue
            these_12weeks_p.append(these_12weeks_d[week] + these_12weeks_p[week - 1])
            these_12weeks_d_goal.append(week_goal*(week+1))
    else: goal = False

    # Pass all the data related to "Last 12 Weeks" chart to html
    these_12weeks_labels = json.dumps(these_12weeks_l)
    these_12weeks_data = json.dumps(these_12weeks_d)
    these12weeks_summ_hours = round(sum(these_12weeks_d),1)
    these_12weeks_progress = json.dumps(these_12weeks_p)
    these_12weeks_data_goal = json.dumps(these_12weeks_d_goal)    
    
    # Get data for a "This Year" chart
    year_now = datetime.now().year
    this_year_entries = (db.session.query(func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id, extract('year', Entry.date)==year_now))
                        .group_by(extract('month', Entry.date))
                        .order_by(Entry.date)
                        .all()
                        )
    this_year_d = []
    this_year_l = []
    for minute, date in this_year_entries:
        this_year_d.append(round((minute / 60),1))
        this_year_l.append(date.strftime("%B"))
    thisyear_summ_hours = round(sum(this_year_d),1)
    this_year_data = json.dumps(this_year_d)
    this_year_labels = json.dumps(this_year_l)
    
    # Gett data for a "All time" chart
    alltime_entries = (db.session.query(func.sum(Entry.duration), Entry.date)
                        .join(Project)
                        .filter(and_(Project.owner==current_user, Entry.project_id==project_id))
                        .group_by(extract('month', Entry.date))
                        .order_by(Entry.date)
                        .all()
                        )
    alltime_d = []
    alltime_l = []
    for minute, date in alltime_entries:
        alltime_d.append(round((minute / 60),1))
        alltime_l.append(date.strftime("%B, %Y"))
    alltime_summ_hours = round(sum(alltime_d),1)
    alltime_data = json.dumps(alltime_d)
    alltime_labels = json.dumps(alltime_l)
    
    footerfalse = True
    return render_template("project.html",
                            user = current_user, project_id = current_project.id,
                            name = current_project.project_name, notes = current_project.notes, week_goal = week_goal,
                            last5 = last5,
                            this_week_data = this_week_data, this_week_labels = this_week_labels,
                            this_month_data = this_month_data, this_month_labels = this_month_labels,
                            goal = goal,
                            current_week = current_week,
                            these_12weeks_data_goal = these_12weeks_data_goal,
                            these_12weeks_progress = these_12weeks_progress,
                            these_12weeks_labels = these_12weeks_labels,
                            these_12weeks_data = these_12weeks_data,
                            this_year_data = this_year_data,
                            this_year_labels = this_year_labels,
                            alltime_data = alltime_data,
                            alltime_labels =alltime_labels,
                            thisweek_summ_hours = thisweek_summ_hours,
                            thismonth_summ_hours = thismonth_summ_hours,
                            these12weeks_summ_hours = these12weeks_summ_hours,
                            thisyear_summ_hours = thisyear_summ_hours,
                            alltime_summ_hours = alltime_summ_hours,
                            footerfalse = footerfalse
                            )


# Page for adding working time to a project manually or using timer (stop watch)
@views.route('project/<int:project_id>/addtime', methods=['GET','POST'])
@login_required
@check_confirmed
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

# Page for editing a project
@views.route('project/<int:project_id>/edit', methods=['GET','POST'])
@login_required
@check_confirmed
def edit_project(project_id):
    current_project = Project.query.filter(Project.id==project_id, Project.owner==current_user).first_or_404()
    if current_project.owner != current_user:
        abort(403)
    edit_project_form = EditProjectForm()
    if edit_project_form.validate_on_submit():
        current_project.project_name = edit_project_form.project_name.data
        current_project.notes = edit_project_form.notes.data
        current_project.goal = edit_project_form.goal.data
        db.session.commit()
        flash('Changes has been saved!', category='success')
        return redirect(url_for('views.project', project_id=current_project.id))
    elif request.method == "GET":
        edit_project_form.project_name.data = current_project.project_name
        edit_project_form.notes.data = current_project.notes
        edit_project_form.goal.data = current_project.goal
    return render_template('edit_project.html', user = current_user, project_id=current_project.id, edit_project_form=edit_project_form)

# Url for deleting a project
@views.route('project/<int:project_id>/delete', methods=['POST'])
@login_required
@check_confirmed
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

# Url for deleting an entry
@views.route('project/delete/<int:entry_id>')
@login_required
@check_confirmed
def delete_entry(entry_id):
    current_entry = Entry.query.join(Project).filter(and_(Entry.id==entry_id, Project.owner==current_user)).first_or_404(entry_id)
    db.session.delete(current_entry)
    db.session.commit()
    plural = ''
    if current_entry.duration != 1:
            plural = 's'
    flash(f'{current_entry.duration} minute{plural} has been deleted!', category='success')
    return redirect(url_for('views.project', project_id=current_entry.project_id))

# Email with a link for changing a password
def send_reset_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request', recipients=[user.email])
    msg.body = reset_email_text(token)
    mail.send(msg)

# Page for requesting password reset
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

# Page user get by the link in the email, changing password
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