from uuid import uuid4

from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.data_access.exercise import ExerciseDataAccess
from app.exceptions import EntityAlreadyExistsException
from app.models.exercises_models import ExerciseInCreate, ExerciseInDB


class ExerciseService:
    def __init__(self, exercise_data_access: ExerciseDataAccess = ExerciseDataAccess()):
        self.exercise_data_access = exercise_data_access

    def get_system_and_user_exercises(self, user_id: str):
        """
        Retrieves the exercises for a given user from both the system and user-specific exercises.

        Args:
            user_id (str): The ID of the user.

        Returns:
            list: A list of exercises for the user, including both system and user-specific exercises.
        """
        return self.exercise_data_access.get_system_and_user_exercises(user_id)

    def create_custom_exercise(self, exercise: ExerciseInCreate, user_id: str):
        """
        Creates a custom exercise.

        Args:
            exercise (ExerciseInCreate): The exercise details.
            user_id (str): The ID of the user creating the exercise.

        Returns:
            ExerciseInDB: The created exercise.

        Raises:
            EntityAlreadyExistsException: If an exercise with the same name already exists.
        """
        if (
            self.exercise_data_access.get_exercise_by_name(exercise.name, user_id)
            is not None
        ):
            raise EntityAlreadyExistsException(f"{exercise.name} already exists")
        exercise_id = str(uuid4())
        exercise_to_create = ExerciseInDB(
            id=exercise_id, name=exercise.name, body_parts=[], creator=user_id
        )
        return self.exercise_data_access.create_custom_exercise(exercise_to_create)

    def get_exercise_by_id(self, exercise_id: str):
        """
        Retrieves an exercise by its ID.

        Args:
            exercise_id (str): The ID of the exercise to retrieve.

        Returns:
            Exercise or None: The exercise object if found, None otherwise.
        """
        try:
            return self.exercise_data_access.get_exercise_by_id(exercise_id)
        except CosmosResourceNotFoundError:
            return None


def get_exercise_service():
    return ExerciseService()
