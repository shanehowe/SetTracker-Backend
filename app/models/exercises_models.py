from pydantic import Field

from app.models.base_model import CustomBaseModel

STR_5_TO_30 = Field(min_length=5, max_length=30)


class ExerciseInDB(CustomBaseModel):
    id: str
    name: str
    body_parts: list[str]
    creator: str


class ExerciseInCreate(CustomBaseModel):
    name: str = STR_5_TO_30
