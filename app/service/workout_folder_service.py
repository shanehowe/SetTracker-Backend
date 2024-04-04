from uuid import uuid4
from app.data_access.workout_folder import WorkoutFolderDataAccess
from app.models.workout_folder_models import WorkoutFolderInDB, WorkoutFolderInRequest, WorkoutFolderInUpdate
from app.exceptions import UnauthorizedAccessException
from azure.cosmos.exceptions import CosmosResourceNotFoundError


class WorkoutFolderService:
    def __init__(
        self,
        workout_folder_data_access: WorkoutFolderDataAccess = WorkoutFolderDataAccess(),
    ) -> None:
        self.workout_folder_data_access = workout_folder_data_access

    def get_folder_by_id(self, folder_id: str, user_requesting_folder: str):
        try:
            retrieved_folder = self.workout_folder_data_access.get_folder_by_id(folder_id)
        except CosmosResourceNotFoundError:
            return None
        if retrieved_folder.user_id != user_requesting_folder:
            raise UnauthorizedAccessException("This folder does not belong to the user")
        return retrieved_folder

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

    def update_workout_folder(self, folder_id: str, data_to_update: WorkoutFolderInUpdate, user_id: str):
        if data_to_update.name is None and data_to_update.exercises is None:
            raise ValueError("Folder name or exercises must be provided to update folder")
        try:
            retrieved_folder = self.workout_folder_data_access.get_folder_by_id(folder_id)
        except CosmosResourceNotFoundError:
            return None

        if retrieved_folder.user_id != user_id:
            raise UnauthorizedAccessException("This folder does not belong to the user")

        if data_to_update.name is not None:
            retrieved_folder.name = data_to_update.name
        if data_to_update.exercises is not None:
            retrieved_folder.exercises = data_to_update.exercises

        return self.workout_folder_data_access.update_workout_folder(retrieved_folder)


def get_workout_folder_service() -> WorkoutFolderService:
    return WorkoutFolderService()
