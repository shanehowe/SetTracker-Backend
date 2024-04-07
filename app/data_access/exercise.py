from app.data_access.base import BaseDataAccess
from app.models.exercises_models import ExerciseInDB


class ExerciseDateAccess(BaseDataAccess):
    def __init__(self):
        super().__init__(container_name="exercises")

    def get_system_and_user_exercises(self, user_id: str) -> list[ExerciseInDB]:
        query = (
            "SELECT * FROM exercises e "
            "WHERE e.creator='system' OR e.creator=@user_id "
            "ORDER BY ASC"
        )
        items = self.container.query_items(
            query=query, parameters=[{"name": "@user_id", "value": user_id}], enable_cross_partition_query=True
        )
        return [ExerciseInDB(**item) for item in items]

    def create_custom_exercise(self, exercise: ExerciseInDB) -> ExerciseInDB:
        return self.container.create_item(body=exercise.model_dump())
