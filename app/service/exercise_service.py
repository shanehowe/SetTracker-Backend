from uuid import uuid4

from app.data_access.exercise import ExerciseDataAccess
from app.exceptions import ExerciseAlreadyExistsException
from app.models.exercises_models import ExerciseInCreate, ExerciseInDB


class ExerciseService:
    def __init__(self, exercise_data_access: ExerciseDataAccess = ExerciseDataAccess()):
        self.exercise_data_access = exercise_data_access

    def get_system_and_user_exercises(self, user_id: str):
        return self.exercise_data_access.get_system_and_user_exercises(user_id)

    def create_custom_exercise(self, exercise: ExerciseInCreate, user_id: str):
        if (
            self.exercise_data_access.get_exercise_by_name(exercise.name, user_id)
            is not None
        ):
            raise ExerciseAlreadyExistsException(f"{exercise.name} already exists")
        exercise_id = str(uuid4())
        exercise_to_create = ExerciseInDB(
            id=exercise_id, name=exercise.name, body_parts=[], creator=user_id
        )
        return self.exercise_data_access.create_custom_exercise(exercise_to_create)


def get_exercise_service():
    return ExerciseService()
