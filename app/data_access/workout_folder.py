from app.data_access.base import BaseDataAccess
from app.models.workout_folder_models import WorkoutFolderInDB


class WorkoutFolderDataAccess(BaseDataAccess):
    def __init__(self):
        super().__init__(container_name="workout-folders")

    def get_users_workout_folders(self, user_id: str) -> list[WorkoutFolderInDB]:
        query = "SELECT * FROM workout_folders wf WHERE wf.user_id = @user_id"
        params = [dict(name="@user_id", value=user_id)]
        workout_folders = self.container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True  # type: ignore
        )
        return [WorkoutFolderInDB(**wf) for wf in workout_folders]

    def create_workout_folder(
        self, workout_folder: WorkoutFolderInDB
    ) -> WorkoutFolderInDB:
        created_workout_folder = self.container.create_item(
            body=workout_folder.model_dump()
        )
        return WorkoutFolderInDB(**created_workout_folder)
