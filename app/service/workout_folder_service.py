from uuid import uuid4

from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

from app.data_access.workout_folder import WorkoutFolderDataAccess
from app.exceptions import EntityNotFoundException, UnauthorizedAccessException
from app.models.workout_folder_models import (
    WorkoutFolderInDB,
    WorkoutFolderInRequest,
    WorkoutFolderInUpdate,
)


class WorkoutFolderService:
    def __init__(
        self,
        workout_folder_data_access: WorkoutFolderDataAccess = WorkoutFolderDataAccess(),
    ) -> None:
        self.workout_folder_data_access = workout_folder_data_access

    def get_folder_by_id(self, folder_id: str, user_requesting_folder: str):
        try:
            retrieved_folder = self.workout_folder_data_access.get_folder_by_id(
                folder_id
            )
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

    def update_workout_folder(
        self, folder_id: str, data_to_update: WorkoutFolderInUpdate, user_id: str
    ):
        if data_to_update.name is None and data_to_update.exercises is None:
            raise ValueError(
                "Folder name or exercises must be provided to update folder"
            )
        try:
            retrieved_folder = self.workout_folder_data_access.get_folder_by_id(
                folder_id
            )
        except CosmosResourceNotFoundError:
            return None

        if retrieved_folder.user_id != user_id:
            raise UnauthorizedAccessException("This folder does not belong to the user")

        if data_to_update.name is not None:
            retrieved_folder.name = data_to_update.name
        if data_to_update.exercises is not None:
            retrieved_folder.exercises = data_to_update.exercises

        return self.workout_folder_data_access.update_workout_folder(retrieved_folder)

    def delete_workout_folder(self, folder_id: str, user_id: str):
        """
        :param folder_id: The id of the folder that is to be deleted
        :param user_id: The id of the user that is requesting the folder to be deleted
        :returns: True if operation was successful, False if not
        :raises ValueError: When the id does not belong to an existing folder
        :raises UnauthorizedAccessException: When the user does not own the folder
        """
        folder_to_delete = self.get_folder_by_id(folder_id, user_id)
        if folder_to_delete is None:
            raise EntityNotFoundException("Folder with requested id does not exist")
        try:
            self.workout_folder_data_access.delete_workout_folder(folder_id)
            return True
        except CosmosHttpResponseError:
            return False


def get_workout_folder_service() -> WorkoutFolderService:
    return WorkoutFolderService()
