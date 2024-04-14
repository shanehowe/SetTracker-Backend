from datetime import datetime, timedelta, timezone


def add_days_to_date(date: datetime, days: int) -> datetime:
    return date + timedelta(days=days)


def generate_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
