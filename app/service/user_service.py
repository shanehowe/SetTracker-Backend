from app.data_access.user import UserDataAccess
from app.models.user_models import UserInDB, BaseUser
from app.models.auth_models import AuthRequest
from app.auth.tokens import encode_jwt, decode_and_verify_token
from app.exceptions import UnsupportedProviderException

from uuid import uuid4


class UserService:
    def __init__(self) -> None:
        self.user_data_access = UserDataAccess()

    def authenticate(self, auth_data: AuthRequest) -> str | None:
        """
        Authenticate a user based on the auth data provided

        :param auth_data: The authentication data
        :return: The JWT token if the user is authenticated, None otherwise
        """
        try:
            decoded_provider_token = decode_and_verify_token(auth_data.identity_token, auth_data.provider)
        except UnsupportedProviderException:
            return None

        if decoded_provider_token is None:
            return None

        email_from_token = decoded_provider_token.get("email")
        if email_from_token is None:
            return None

        user_for_auth = self.user_data_access.get_user_by_email(email_from_token)
        if user_for_auth is None:
            user_to_create = BaseUser(email=email_from_token, provider=auth_data.provider)
            user_for_auth = self.create_user(user_to_create)
        
        return encode_jwt(user_for_auth)

    def create_user(self, user: BaseUser):
        user_id = str(uuid4())
        user_for_creation = UserInDB(**user.model_dump(), id=user_id)
        return self.user_data_access.create_user(user_for_creation)
