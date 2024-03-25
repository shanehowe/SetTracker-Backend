from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    email: EmailStr
    provider: str

    class Config:
        populate_by_name = True


class UserInDB(BaseUser):
    id: str


class UserInResponse(BaseModel):
    id: str
    token: str
