from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Tempo(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    eccentric: int
    concentric: int
    pause: int


class BaseSetModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
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
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    sets: list[SetInDB]
    date_created: str