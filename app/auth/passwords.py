import bcrypt


def get_password_hash(plain_text_password: str) -> bytes:
    return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt())


def check_password(plain_text_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_text_password.encode(), hashed_password.encode())
