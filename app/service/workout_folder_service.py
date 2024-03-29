from app.data_access.workout_folder import WorkoutFolderDataAccess
from app.models.workout_folder_models import WorkoutFolderInDB


class WorkoutFolderService:
    def __init__(
        self,
        workout_folder_data_access: WorkoutFolderDataAccess = WorkoutFolderDataAccess(),
    ) -> None:
        self.workout_folder_data_access = workout_folder_data_access

    def get_users_workout_folders(self, user_id: str) -> list[WorkoutFolderInDB]:
        return self.workout_folder_data_access.get_users_workout_folders(user_id)

    def create_workout_folder(self):
        pass


def get_workout_folder_service() -> WorkoutFolderService:
    return WorkoutFolderService()
