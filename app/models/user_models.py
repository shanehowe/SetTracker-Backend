from pydantic import BaseModel, EmailStr, ConfigDict


class BaseUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    provider: str


class UserInDB(BaseUser):
    id: str


class UserInResponse(BaseModel):
    id: str
    token: str
