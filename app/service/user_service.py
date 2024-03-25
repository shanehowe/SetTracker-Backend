from uuid import uuid4
from jwt.exceptions import PyJWTError

from app.auth.tokens import decode_and_verify_token, encode_jwt
from app.data_access.user import UserDataAccess
from app.exceptions import UnsupportedProviderException, AuthenticationException
from app.models.auth_models import AuthRequest
from app.models.user_models import BaseUser, UserInDB


class UserService:
    def __init__(self, user_data_access=UserDataAccess()) -> None:
        self.user_data_access = user_data_access

    def authenticate(self, auth_data: AuthRequest) -> dict[str, str] | None:
        """
        Authenticate a user based on the auth data provided

        :param auth_data: The authentication data
        :return: The authenticated user or None
        :raises AuthenticationException: If the authentication fails
        """
        try:
            decoded_provider_token = decode_and_verify_token(
                auth_data.token, auth_data.provider
            )
        except UnsupportedProviderException:
            raise AuthenticationException("oAuth provider not supported")
        except ValueError | PyJWTError:
            raise AuthenticationException("Invalid token data")

        email_from_token = decoded_provider_token.get("email")
        if email_from_token is None:
            raise AuthenticationException("Invalid token data")

        user_for_auth = self.user_data_access.get_user_by_email(email_from_token)
        if user_for_auth is None:
            user_to_create = BaseUser(
                email=email_from_token, provider=auth_data.provider
            )
            user_for_auth = self.create_user(user_to_create)
        
        return {
            "id": user_for_auth.id,
            "token": encode_jwt({"id": user_for_auth.id, "email": user_for_auth.email})
        }

    def create_user(self, user: BaseUser):
        user_id = str(uuid4())
        user_for_creation = UserInDB(**user.model_dump(), id=user_id)
        return self.user_data_access.create_user(user_for_creation)
