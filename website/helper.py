from functools import wraps
from flask import redirect, url_for
from flask_login import current_user

# Set a decorator for checking if a user's email was confirmed
def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function





""" 
creating 12-element "these_12weeks_d" list, even if "raw_these_12weeks_d" is shorter,
when originally some data skipped by user
and there is no data in db for those skipped weeks among those last 12
"""
def adjust_data(week_of_year_for_data, raw_these_12weeks_d, week_of_year_for_labels):
    buff_data_list = []
    for i, d_element in enumerate(week_of_year_for_data):
        if week_of_year_for_data.index(d_element) == week_of_year_for_labels.index(d_element):
            buff_data_list.append(raw_these_12weeks_d[i])
        else:
            for j, l_element in enumerate(week_of_year_for_labels):
                if d_element == l_element:
                    for k in range(len(buff_data_list), j):
                        buff_data_list.append(0)
                    buff_data_list.append(raw_these_12weeks_d[i])
                    
    if len(week_of_year_for_labels) > len(buff_data_list) and buff_data_list != []:
        for i in range(len(buff_data_list), len(week_of_year_for_labels)):
            buff_data_list.append(0)
    return buff_data_list.copy()