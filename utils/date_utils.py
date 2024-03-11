from datetime import datetime, timedelta


def add_days_to_date(date: datetime, days: int) -> datetime:
    return date + timedelta(days=days)
