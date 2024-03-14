import jwt
import datetime
from app.utils import add_days_to_date


def encode_jwt(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    today = datetime.datetime.now()
    twenty_four_hours = add_days_to_date(today, 1)
    updated_payload = {**payload, "exp": twenty_four_hours}
    return jwt.encode(updated_payload, secret, algorithm=algorithm)


def decode_jwt(token: str, secret: str, algorithm: str = "HS256") -> dict:
    return jwt.decode(token, secret, algorithms=[algorithm])
