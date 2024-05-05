from typing import Literal

from pydantic import EmailStr

from app.models.base_model import CustomBaseModel


class Preferences(CustomBaseModel):
    theme: Literal["system", "dark", "light"]


class BaseUser(CustomBaseModel):
    email: EmailStr


class UserInDB(BaseUser):
    id: str
    preferences: Preferences = Preferences(theme="system")
    provider: str | None = None
    password_hash: str | None = None


class UserInResponse(CustomBaseModel):
    id: str
    token: str
    preferences: Preferences


class UserOAuth(BaseUser):
    provider: str


class UserEmailAuth(BaseUser):
    password_hash: str


class UserEmailAuthInSignUp(BaseUser):
    password: str