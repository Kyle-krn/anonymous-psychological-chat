import datetime

def russian_str_date(str_time):
    if 'days' in str_time:
        str_time = str_time.replace('days', 'дней')
    elif 'day' in str_time:
        str_time = str_time.replace('day', 'день')
    return str_time

def delete_microseconds(delta):
    '''Удаляет микросекунды из дельты'''
    return delta - datetime.timedelta(microseconds=delta.microseconds)