from datetime import datetime, timedelta

def parse_dates(date_str: str):
    return datetime.strptime(date_str, '%d.%m.%Y')

def parse_datetimes(datetime_str: str):
    return datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")

def add_hours(date_time:datetime, hours):
    return date_time + timedelta(hours=hours)