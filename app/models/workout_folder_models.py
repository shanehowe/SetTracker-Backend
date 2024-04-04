from pydantic import BaseModel
from typing import Optional


class BaseWorkoutFolder(BaseModel):
    class Config:
        populate_by_name = True


class WorkoutFolderInDB(BaseWorkoutFolder):
    id: str
    name: str
    user_id: str
    exercises: list[str]


class WorkoutFolderInRequest(BaseWorkoutFolder):
    name: str
    exercises: Optional[list[str]] = None


class WorkoutFolderInUpdate(BaseWorkoutFolder):
    name: Optional[str] = None
    exercises: Optional[list[str]] = None
