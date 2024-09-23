from datetime import datetime

def parse_date_time(date):
    try:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") if date is not None else None
    except ValueError:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ") if date is not None else None