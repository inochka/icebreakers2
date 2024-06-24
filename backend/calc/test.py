from datetime import datetime, timedelta
from backend.utils import timedelta_to_hours

print(timedelta_to_hours(timedelta(days=1, hours=1, minutes=30)))