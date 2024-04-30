from typing import Optional

from pydantic import Field, field_validator

from app.models.base_model import CustomBaseModel
from app.models.exercises_models import ExerciseInDB

VALID_LENGTH = Field(min_length=1, max_length=25)


class WorkoutFolderInDB(CustomBaseModel):
    id: str
    name: str = VALID_LENGTH
    user_id: str
    exercises: Optional[list[ExerciseInDB]] = None


class WorkoutFolderInRequest(CustomBaseModel):
    name: str = VALID_LENGTH
    exercises: Optional[list[ExerciseInDB]] = None


class WorkoutFolderInUpdate(CustomBaseModel):
    name: Optional[str] = None
    exercises: Optional[list[ExerciseInDB]] = None

    @field_validator("name")
    @classmethod
    def check_name_if_not_none(cls, name: Optional[str]):
        # If name is none, we don't need to check it
        # might just be updating exercises
        if name is None:
            return
        assert len(name) >= 1 and len(name) <= 25
