from app.models.base_model import CustomBaseModel


class AuthRequest(CustomBaseModel):
    token: str
    provider: str
