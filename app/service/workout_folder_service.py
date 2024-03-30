from uuid import uuid4
from app.data_access.workout_folder import WorkoutFolderDataAccess
from app.models.workout_folder_models import WorkoutFolderInDB, WorkoutFolderInRequest


class WorkoutFolderService:
    def __init__(
        self,
        workout_folder_data_access: WorkoutFolderDataAccess = WorkoutFolderDataAccess(),
    ) -> None:
        self.workout_folder_data_access = workout_folder_data_access

    def get_users_workout_folders(self, user_id: str) -> list[WorkoutFolderInDB]:
        return self.workout_folder_data_access.get_users_workout_folders(user_id)

    def create_workout_folder(self, folder: WorkoutFolderInRequest, user_id: str):
        if folder.exercises is None:
            folder.exercises = []
        folder_id = str(uuid4())
        folder_for_creation = WorkoutFolderInDB(
            **folder.model_dump(), user_id=user_id, id=folder_id
        )
        return self.workout_folder_data_access.create_workout_folder(
            folder_for_creation
        )


def get_workout_folder_service() -> WorkoutFolderService:
    return WorkoutFolderService()
