from uuid import uuid4

from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

from app.data_access.set import SetDataAccess
from app.exceptions import EntityNotFoundException, UnauthorizedAccessException
from app.models.set_models import SetInCreate, SetInDB
from app.service.exercise_service import ExerciseService
from app.service.user_service import UserService
from app.utils.date_utils import generate_utc_timestamp
from app.utils.set_utils import group_sets_by_date, sorted_set_history


class SetService:
    def __init__(
        self,
        set_data_access: SetDataAccess = SetDataAccess(),
        exercise_service: ExerciseService = ExerciseService(),
        user_service: UserService = UserService(),
    ) -> None:
        self.set_data_access = set_data_access
        self.exercise_service = exercise_service
        self.user_service = user_service

    def get_set_by_id(self, set_id: str):
        """
        Retrieves a set by its ID.

        Args:
            set_id (str): The ID of the set to retrieve.

        Returns:
            dict or None: The set object if found, None otherwise.
        """
        try:
            return self.set_data_access.get_set_by_id(set_id)
        except CosmosResourceNotFoundError:
            return None

    def get_users_sets_by_exercise_id(self, exercise_id: str, user_id: str):
        """
        Retrieves sets for a specific exercise and user, groups them by date, and returns the sorted set history.

        Args:
            exercise_id (str): The ID of the exercise.
            user_id (str): The ID of the user.

        Returns:
            list: The sorted set history, grouped by date.
        """
        retrieved_sets = self.set_data_access.get_users_sets_by_exercise_id(
            exercise_id=exercise_id, user_id=user_id
        )
        grouped_sets = group_sets_by_date(retrieved_sets)
        return sorted_set_history(grouped_sets)

    def create_set(self, set_in_create: SetInCreate, user_id: str):
        """
        Creates a new set for a user.

        Args:
            set_in_create (SetInCreate): The set details to create.
            user_id (str): The ID of the user.

        Returns:
            SetInDB: The created set.

        Raises:
            EntityNotFoundException: If the user or exercise does not exist.
        """
        if self.user_service.get_user_by_id(user_id) is None:
            raise EntityNotFoundException(f"User with ID {user_id} does not exist")
        elif (
            self.exercise_service.get_exercise_by_id(set_in_create.exercise_id) is None
        ):
            raise EntityNotFoundException(
                f"Exercise with ID {set_in_create.exercise_id} does not exist"
            )
        set_id = str(uuid4())
        set_to_create = SetInDB(
            id=set_id,
            **set_in_create.model_dump(),
            user_id=user_id,
            date_created=generate_utc_timestamp(),
        )
        return self.set_data_access.create_set(set_to_create)

    def delete_set(self, set_id: str, user_id: str):
        """
        Deletes a set with the given set_id if it exists and the user_id matches the creator's user_id.

        Args:
            set_id (str): The ID of the set to delete.
            user_id (str): The ID of the user attempting to delete the set.

        Returns:
            bool: True if the set was successfully deleted, False otherwise.

        Raises:
            EntityNotFoundException: If the set with the given set_id does not exist.
            UnauthorizedAccessException: If the user attempting to delete the set is not the creator.
        """
        set_to_delete = self.get_set_by_id(set_id)
        if set_to_delete is None:
            raise EntityNotFoundException(f"Set with ID: {set_id} does not exist")
        elif set_to_delete.user_id != user_id:
            raise UnauthorizedAccessException(
                "Only the person who created this set can delete it"
            )
        try:
            self.set_data_access.delete_set(set_id)
            return True
        except CosmosHttpResponseError:
            return False


def get_set_service():
    return SetService()
