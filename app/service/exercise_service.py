from app.data_access.exercise import ExerciseDateAccess


class ExerciseService:
    def __init__(self, exercise_data_access: ExerciseDateAccess = ExerciseDateAccess()):
        self.exercise_data_access = exercise_data_access

    def get_system_and_user_exercises(self, user_id: str):
        return self.exercise_data_access.get_system_and_user_exercises(user_id)


def get_exercise_service():
    return ExerciseService()
