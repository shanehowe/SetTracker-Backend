from pydantic import BaseModel, EmailStr


class AppleAuth(BaseModel):
    email: EmailStr
    identity_token: str

    class Config:
        allow_population_by_field_name = True
