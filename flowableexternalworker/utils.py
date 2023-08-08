from datetime import datetime

def parse_date_time(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") if date is not None else None
