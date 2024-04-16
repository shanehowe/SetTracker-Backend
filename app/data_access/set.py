from app.data_access.base import BaseDataAccess
from app.models.set_models import SetInDB


class SetDataAccess(BaseDataAccess):
    def __init__(self) -> None:
        super().__init__(container_name="exercise-sets")

    def get_users_sets_by_exercise_id(
        self, exercise_id: str, user_id: str
    ) -> list[SetInDB]:
        query = "SELECT * FROM sets s WHERE s.exercise_id = @exercise_id AND s.user_id = @user_id"
        params = [
            dict(name="@exercise_id", value=exercise_id),
            dict(name="@user_id", value=user_id),
        ]
        sets = self.container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True  # type: ignore
        )
        return [SetInDB(**s) for s in sets]

    def create_set(self, set_to_create: SetInDB) -> SetInDB:
        created_set = self.container.create_item(body=set_to_create.model_dump())
        return SetInDB(**created_set)
