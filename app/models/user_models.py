from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    email: EmailStr
    provider: str

    class Config:
        allow_population_by_field_name = True


class UserInDB(BaseUser):
    id: str

