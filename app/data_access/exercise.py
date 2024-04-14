from typing import Optional

from app.data_access.base import BaseDataAccess
from app.models.exercises_models import ExerciseInDB


class ExerciseDataAccess(BaseDataAccess):
    def __init__(self):
        super().__init__(container_name="exercises")

    def get_system_and_user_exercises(self, user_id: str) -> list[ExerciseInDB]:
        query = (
            "SELECT * FROM exercises e "
            "WHERE e.creator='system' OR e.creator=@user_id"
        )
        items = self.container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}],
            enable_cross_partition_query=True,
        )
        return [ExerciseInDB(**item) for item in items]

    def create_custom_exercise(self, exercise: ExerciseInDB) -> ExerciseInDB:
        created_exercise = self.container.create_item(body=exercise.model_dump())
        return ExerciseInDB(**created_exercise)

    def get_exercise_by_name(self, name: str, user_id: str) -> Optional[ExerciseInDB]:
        query = "SELECT * FROM exercises e WHERE e.name=@name AND (e.creator='system' OR e.creator=@user_id)"
        items = list(
            self.container.query_items(
                query=query,
                parameters=[
                    {"name": "@name", "value": name},
                    {"name": "@user_id", "value": user_id},
                ],
                enable_cross_partition_query=True,
            )
        )
        if not items:
            return None
        return ExerciseInDB(**items[0])
