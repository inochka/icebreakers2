from datetime import datetime, timedelta
import math

def parse_dates(date_str: str):
    return datetime.strptime(date_str, '%d.%m.%Y')

def parse_datetimes(datetime_str: str):
    return datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")

def add_hours(date_time:datetime, hours):
    return date_time + timedelta(hours=hours)

def timedelta_to_hours(td:timedelta) -> int:
    return td.total_seconds()/3600

def replace_inf_nan(obj):
    if isinstance(obj, float):
        if math.isinf(obj):
            return "Infinity"
        elif math.isnan(obj):
            return "NaN"
    elif isinstance(obj, dict):
        return {k: replace_inf_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_inf_nan(i) for i in obj]
    return obj