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
        try:
            return self.set_data_access.get_set_by_id(set_id)
        except CosmosResourceNotFoundError:
            return None

    def get_users_sets_by_exercise_id(self, exercise_id: str, user_id: str):
        retrieved_sets = self.set_data_access.get_users_sets_by_exercise_id(
            exercise_id=exercise_id, user_id=user_id
        )
        grouped_sets = group_sets_by_date(retrieved_sets)
        return sorted_set_history(grouped_sets)

    def create_set(self, set_in_create: SetInCreate, user_id: str):
        """
        Create a new set
        :param set_in_create: The set to create
        :param user_id: The ID of the user creating the set
        :return: The created set
        :raises EntityNotFoundException: If the user or exercise does not exist
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
        Deletes a set with the given set_id if it exists and belongs to the specified user.

        :param set_id (str): The ID of the set to be deleted.
        :param user_id (str): The ID of the user who owns the set.

        :returns bool: True if the set is successfully deleted, False otherwise.

        :raises EntityNotFoundException: If the set does not exist.
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
