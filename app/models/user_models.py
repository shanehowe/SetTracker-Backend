from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
    id: str
    email: EmailStr
    povider: str
    first_name: str
    last_name: str

    class Config:
        allow_population_by_field_name = True