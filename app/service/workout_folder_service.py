from uuid import uuid4

from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

from app.data_access.workout_folder import WorkoutFolderDataAccess
from app.exceptions import UnauthorizedAccessException
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
        """
        Retrieves a workout folder by its ID.

        Args:
            folder_id (str): The ID of the folder to retrieve.
            user_requesting_folder (str): The ID of the user requesting the folder.

        Returns:
            WorkoutFolder: The retrieved workout folder.

        Raises:
            UnauthorizedAccessException: If the folder does not belong to the user.
        """
        try:
            retrieved_folder = self.workout_folder_data_access.get_folder_by_id(
                folder_id
            )
        except CosmosResourceNotFoundError:
            return None
        if retrieved_folder.user_id != user_requesting_folder:
            raise UnauthorizedAccessException("You do not have access to this folder")
        return retrieved_folder

    def get_users_workout_folders(self, user_id: str) -> list[WorkoutFolderInDB]:
        """
        Retrieves the workout folders for a specific user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            list[WorkoutFolderInDB]: A list of workout folders associated with the user.
        """
        return self.workout_folder_data_access.get_users_workout_folders(user_id)

    def create_workout_folder(self, folder: WorkoutFolderInRequest, user_id: str):
        """
        Creates a new workout folder.

        Args:
            folder (WorkoutFolderInRequest): The workout folder to be created.
            user_id (str): The ID of the user creating the folder.

        Returns:
            WorkoutFolderInDB: The created workout folder.
        """
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
        """
        Updates a workout folder with the provided data.

        Args:
            folder_id (str): The ID of the folder to update.
            data_to_update (WorkoutFolderInUpdate): The data to update the folder with.
            user_id (str): The ID of the user performing the update.

        Returns:
            WorkoutFolder: The updated workout folder.

        Raises:
            ValueError: If neither the folder name nor the exercises are provided.
            UnauthorizedAccessException: If the folder does not belong to the user.
        """
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
        Deletes a workout folder with the specified folder_id for the given user_id.

        Args:
            folder_id (str): The ID of the folder to delete.
            user_id (str): The ID of the user who owns the folder.

        Returns:
            bool: True if the folder was successfully deleted, False otherwise.

        Raises:
            ValueError: If the folder with the requested ID does not exist.
        """
        folder_to_delete = self.get_folder_by_id(folder_id, user_id)
        if folder_to_delete is None:
            raise ValueError("Folder with requested id does not exist")
        try:
            self.workout_folder_data_access.delete_workout_folder(folder_id)
            return True
        except CosmosHttpResponseError:
            return False


def get_workout_folder_service() -> WorkoutFolderService:
    return WorkoutFolderService()
