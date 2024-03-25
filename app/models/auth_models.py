from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    token: str
    provider: str

    class Config:
        populate_by_name = True
