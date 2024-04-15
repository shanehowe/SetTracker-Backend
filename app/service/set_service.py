from uuid import uuid4

from app.data_access.set import SetDataAccess
from app.exceptions import ExerciseDoesNotExistException, UserDoesNotExistException
from app.models.set_models import SetInCreate, SetInDB
from app.service.exercise_service import ExerciseService
from app.service.user_service import UserService


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

    def get_users_sets_by_exercise_id(self, exercise_id: str, user_id: str):
        return self.set_data_access.get_users_sets_by_exercise_id(
            exercise_id=exercise_id, user_id=user_id
        )

    def create_set(self, set_in_create: SetInCreate, user_id: str):
        """
        Create a new set
        :param set_in_create: The set to create
        :param user_id: The ID of the user creating the set
        :return: The created set
        :raises UserDoesNotExistException: If the user does not exist.
        :raises ExerciseDoesNotExistException: If the exercise does not exist.
        """
        if self.user_service.get_user_by_id(user_id) is None:
            raise UserDoesNotExistException(f"User with ID {user_id} does not exist")
        elif (
            self.exercise_service.get_exercise_by_id(set_in_create.exercise_id) is None
        ):
            raise ExerciseDoesNotExistException(
                f"Exercise with ID {set_in_create.exercise_id} does not exist"
            )
        set_id = str(uuid4())
        set_to_create = SetInDB(
            id=set_id, **set_in_create.model_dump(), user_id=user_id
        )
        return self.set_data_access.create_set(set_to_create)


def get_set_service():
    return SetService()
