from app.data_access.user import UserDataAccess
from app.models.user_models import UserInRequest


class UserService:
    def __init__(self) -> None:
        self.user_data_access = UserDataAccess()

    def authenticate(self, user: UserInRequest):
        existing_user = self.user_data_access.get_user_by_email(user.email)
        # TODO: 
        if existing_user:
            pass
        else:
            pass
