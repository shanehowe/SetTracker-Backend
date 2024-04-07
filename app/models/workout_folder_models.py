from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.models.exercises_models import ExerciseInDB


class BaseWorkoutFolder(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class WorkoutFolderInDB(BaseWorkoutFolder):
    id: str
    name: str
    user_id: str
    exercises: Optional[list[ExerciseInDB]] = None


class WorkoutFolderInRequest(BaseWorkoutFolder):
    name: str
    exercises: Optional[list[ExerciseInDB]] = None


class WorkoutFolderInUpdate(BaseWorkoutFolder):
    name: Optional[str] = None
    exercises: Optional[list[ExerciseInDB]] = None
