from pydantic import Field

from app.models.base_model import CustomBaseModel

GREATER_EQUAL_TO_ZERO = Field(ge=0)
GREATER_THAN_ZERO = Field(gt=0)


class Tempo(CustomBaseModel):
    eccentric: int = GREATER_EQUAL_TO_ZERO
    concentric: int = GREATER_EQUAL_TO_ZERO
    pause: int = GREATER_EQUAL_TO_ZERO


class BaseSetModel(CustomBaseModel):
    exercise_id: str
    weight: float = GREATER_THAN_ZERO
    reps: int = GREATER_THAN_ZERO
    notes: str = ""
    tempo: Tempo | None = None


class SetInDB(BaseSetModel):
    id: str
    date_created: str
    user_id: str


class SetInCreate(BaseSetModel):
    pass


class SetGroup(CustomBaseModel):
    sets: list[SetInDB]
    date_created: str
