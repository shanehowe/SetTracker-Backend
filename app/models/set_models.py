from pydantic import BaseModel, ConfigDict


class Tempo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    eccentric: int
    concentric: int
    pause: int


class BaseSetModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    exercise_id: str
    weight: float
    reps: int
    notes: str = ""
    tempo: Tempo | None = Tempo(eccentric=0, concentric=0, pause=0)


class SetInDB(BaseSetModel):
    id: str
    date_created: str
    user_id: str


class SetInCreate(BaseSetModel):
    pass


class SetGroup(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    sets: list[SetInDB]
    date_created: str