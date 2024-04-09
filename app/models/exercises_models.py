from pydantic import BaseModel, ConfigDict


class BaseExercise(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class ExerciseInDB(BaseExercise):
    id: str
    name: str
    body_parts: list[str]
    creator: str


class ExerciseInCreate(BaseExercise):
    name: str
