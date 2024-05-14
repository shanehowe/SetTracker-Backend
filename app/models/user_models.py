from typing import Annotated, Literal

from pydantic import BeforeValidator, EmailStr, Field

from app.models.base_model import CustomBaseModel
from app.utils.string_utils import strip_and_lower


class Preferences(CustomBaseModel):
    theme: Literal["system", "dark", "light"]


class BaseUser(CustomBaseModel):
    email: Annotated[EmailStr, BeforeValidator(strip_and_lower)]


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


class UserEmailAuthInSignUpAndIn(BaseUser):
    password: str = Field(..., min_length=6)
