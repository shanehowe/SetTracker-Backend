from pydantic import BaseModel, ConfigDict


class AuthRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str
    provider: str
