import datetime
import random
import string

def russian_str_date(str_time):
    if 'days' in str_time:
        str_time = str_time.replace('days', 'дней')
    elif 'day' in str_time:
        str_time = str_time.replace('day', 'день')
    return str_time

def delete_microseconds(delta):
    '''Удаляет микросекунды из дельты'''
    return delta - datetime.timedelta(microseconds=delta.microseconds)

def generate_alphanum_random_string(length):
    """Генератор рандомных строк типа - s4Knf3Lf35"""
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string