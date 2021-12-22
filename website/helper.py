
""" 
creating 12-element "these_12weeks_d" list, even if "raw_these_12weeks_d" is shorter,
when originally some data skipped
and there is no data in db for some weeks among those last 12
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