from app.data_access.set import SetDataAccess


class SetService:
    def __init__(self, set_data_access: SetDataAccess = SetDataAccess()) -> None:
        self.set_data_access = set_data_access

    def get_users_sets_by_exercise_id(self, exercise_id: str, user_id: str):
        return self.set_data_access.get_users_sets_by_exercise_id(
            exercise_id=exercise_id, user_id=user_id
        )


def get_set_service():
    return SetService()
