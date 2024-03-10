from pydantic import BaseModel, EmailStr
from utils.string_utils import to_camel


class AppleAuth(BaseModel):
    email: EmailStr
    identity_token: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
