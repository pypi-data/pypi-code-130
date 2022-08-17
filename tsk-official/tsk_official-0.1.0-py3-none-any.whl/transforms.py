from datetime import datetime


def mkdate(date: str) -> datetime:
    if date:
        return datetime.strptime(date, '%m/%d/%y')
    return None
