from typing import Literal
from pydantic import BaseModel, EmailStr, ConfigDict


class Preferences(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    theme: Literal["system", "dark", "light"]


class BaseUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    provider: str


class UserInDB(BaseUser):
    id: str
    preferences: Preferences = Preferences(theme="system")


class UserInResponse(BaseModel):
    id: str
    token: str
    preferences: Preferences = Preferences(theme="system")
