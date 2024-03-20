from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    identity_token: str
    provider: str

    class Config:
        allow_population_by_field_name = True
