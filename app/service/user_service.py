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
        Retrieve a user from the database by their ID.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            UserInDB | None: The user object if found, None otherwise.
        """
        try:
            return self.user_data_access.get_user_by_id(user_id)
        except CosmosResourceNotFoundError:
            return None

    def authenticate_oauth(self, auth_data: AuthRequest) -> UserInResponse:
        """
        Authenticates a user using OAuth.

        Args:
            auth_data (AuthRequest): The authentication request data.

        Returns:
            UserInResponse: The user information response.

        Raises:
            AuthenticationException: If the OAuth provider is not supported,
                the token cannot be decoded, or the token data is invalid.
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
        Authenticates a user using email and password.

        Args:
            user (UserEmailAuthInSignUpAndIn): The user object containing email and password.

        Returns:
            UserInResponse: The user response object containing user information and token.

        Raises:
            AuthenticationException: If the email or password is invalid, or if the user is not signed in with the correct provider.
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
        """
        Signs up a new user with the provided email and password.

        Args:
            user (UserEmailAuthInSignUpAndIn): The user object containing the email and password.

        Returns:
            UserInResponse: The response object containing the created user's information.

        Raises:
            EntityAlreadyExistsException: If an account already exists with the provided email.
        """
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
        """
        Creates a new user.

        Args:
            user (UserOAuth | UserEmailAuth): The user object containing the user information.

        Returns:
            User: The created user object.

        """
        user_id = str(uuid4())
        user_for_creation = UserInDB(**user.model_dump(), id=user_id)
        return self.user_data_access.create_user(user_for_creation)

    def update_user_preferences(self, preferences: Preferences, user_id: str) -> None:
        """
        Updates the preferences of a user with the given user ID.

        Args:
            preferences (Preferences): The new preferences to be updated.
            user_id (str): The ID of the user to update.

        Raises:
            EntityNotFoundException: If no user with the given user ID is found.

        Returns:
            None
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
