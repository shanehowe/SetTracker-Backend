from datetime import datetime, timedelta


def add_days_to_date(date: datetime, days: int) -> datetime:
    return date + timedelta(days=days)


def to_camel(string: str) -> str:
    return "".join(
        word.capitalize() if i else word for i, word in enumerate(string.split("_"))
    )
