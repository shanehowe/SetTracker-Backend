from typing import Literal

from pydantic import EmailStr

from app.models.base_model import CustomBaseModel


class Preferences(CustomBaseModel):
    theme: Literal["system", "dark", "light"]


class BaseUser(CustomBaseModel):
    email: EmailStr
    provider: str


class UserInDB(BaseUser):
    id: str
    preferences: Preferences = Preferences(theme="system")


class UserInResponse(CustomBaseModel):
    id: str
    token: str
    preferences: Preferences = Preferences(theme="system")
