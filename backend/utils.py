from datetime import datetime

def parse_dates(date_str: str):
    return datetime.strptime(date_str, '%d.%m.%Y')