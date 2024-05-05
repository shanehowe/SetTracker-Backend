from uuid import uuid4

from azure.cosmos.exceptions import CosmosResourceNotFoundError
from jwt.exceptions import PyJWTError

from app.auth.passwords import check_password, get_password_hash
from app.auth.tokens import decode_and_verify_token, encode_jwt
from app.data_access.user import UserDataAccess
from app.exceptions import (
    AuthenticationException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    UnsupportedProviderException,
)
from app.models.auth_models import AuthRequest
from app.models.user_models import (
    Preferences,
    UserEmailAuth,
    UserEmailAuthInSignUpAndIn,
    UserInDB,
    UserInResponse,
    UserOAuth,
)


class UserService:
    def __init__(self, user_data_access=UserDataAccess()) -> None:
        self.user_data_access = user_data_access

    def get_user_by_id(self, user_id: str) -> UserInDB | None:
        """
        Get a user by their ID
        :param user_id: The ID of the user
        :return: The user or None if not found
        """
        try:
            return self.user_data_access.get_user_by_id(user_id)
        except CosmosResourceNotFoundError:
            return None

    def authenticate_oauth(self, auth_data: AuthRequest) -> UserInResponse:
        """
        Authenticate a user based on the auth data provided

        :param auth_data: The authentication data
        :return: The authenticated user
        :raises AuthenticationException: If the authentication fails
        """
        try:
            decoded_provider_token = decode_and_verify_token(
                auth_data.token, auth_data.provider
            )
        except UnsupportedProviderException:
            raise AuthenticationException("oAuth provider not supported")
        except (ValueError, PyJWTError) as e:
            raise AuthenticationException("Unable to decode token")

        email_from_token = decoded_provider_token.get("email")
        if email_from_token is None:
            raise AuthenticationException("Invalid token data")

        user_for_auth = self.user_data_access.get_user_by_email(email_from_token)
        if user_for_auth is None:
            user_to_create = UserOAuth(
                email=email_from_token, provider=auth_data.provider
            )
            user_for_auth = self.create_user(user_to_create)

        return UserInResponse(
            id=user_for_auth.id,
            token=encode_jwt({"id": user_for_auth.id, "email": user_for_auth.email}),
            preferences=user_for_auth.preferences,
        )

    def authenticate_email_password_auth(
        self, user: UserEmailAuthInSignUpAndIn
    ) -> UserInResponse:
        """
        Authenticate a user through email and password

        :param user: The user to authenticate
        :return: The authenticated user
        :raises AuthenticationException: If the user doesnt exist or password is incorrect
        or user previously signed up with oAuth provider
        """
        user_in_db = self.user_data_access.get_user_by_email(user.email)
        if user_in_db is None:
            raise AuthenticationException("Invalid email or password")
        elif user_in_db.password_hash is None:
            raise AuthenticationException(
                f"Please sign in with {user_in_db.provider} to continue"
            )
        elif not check_password(user.password, user_in_db.password_hash):
            raise AuthenticationException("Invalid email or password")

        return UserInResponse(
            id=user_in_db.id,
            token=encode_jwt({"id": user_in_db.id, "email": user_in_db.email}),
            preferences=user_in_db.preferences,
        )

    def sign_up_user(self, user: UserEmailAuthInSignUpAndIn) -> UserInResponse:
        if self.user_data_access.get_user_by_email(user.email) is not None:
            raise EntityAlreadyExistsException(
                "An account already exists with this email. Sign in to continue"
            )
        hashed_password = get_password_hash(user.password)
        user_to_create = UserEmailAuth(email=user.email, password_hash=hashed_password)
        created_user = self.create_user(user_to_create)
        return UserInResponse(
            id=created_user.id,
            token=encode_jwt({"id": created_user.id, "email": created_user.email}),
            preferences=created_user.preferences,
        )

    def create_user(self, user: UserOAuth | UserEmailAuth):
        user_id = str(uuid4())
        user_for_creation = UserInDB(**user.model_dump(), id=user_id)
        return self.user_data_access.create_user(user_for_creation)

    def update_user_preferences(self, preferences: Preferences, user_id: str) -> None:
        """
        Update users preferences.
        :param updated_preferences: The preferences object with the data to update
        :param user_id: The ID of the user to preform the operation on.
        :raises EntityNotFoundException: The user_id does not belong to an existing user.
        """
        user_to_update = self.get_user_by_id(user_id)
        if user_to_update is None:
            raise EntityNotFoundException(f"No user with ID: {user_id}")
        # Get the current preferences
        # add the current preferences into the ones to be updated
        # if its not already in there.
        current_preferences = user_to_update.preferences.model_dump()
        updating_preferences = preferences.model_dump()
        for key in current_preferences:
            if updating_preferences.get(key) is None:
                updating_preferences[key] = current_preferences[key]
        user_to_update.preferences = Preferences(**updating_preferences)
        self.user_data_access.update_user(user_to_update)


def get_user_service() -> UserService:
    return UserService()
