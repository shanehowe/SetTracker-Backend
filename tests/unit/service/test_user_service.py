from unittest.mock import MagicMock, patch

import pytest
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.data_access.user import UserDataAccess
from app.exceptions import (
    AuthenticationException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.models.auth_models import AuthRequest
from app.models.user_models import (
    Preferences,
    UserEmailAuth,
    UserEmailAuthInSignUp,
    UserInDB,
    UserInResponse,
    UserOAuth,
)
from app.service.user_service import UserService


@pytest.fixture
def mock_user_data_access():
    return MagicMock(spec=UserDataAccess)


@pytest.fixture
def user_service(mock_user_data_access):
    return UserService(user_data_access=mock_user_data_access)


@pytest.fixture
def mock_decode_and_verify_token():
    return MagicMock()


def test_get_user_by_id_returns_user_when_found(user_service, mock_user_data_access):
    mock_user_data_access.get_user_by_id = MagicMock(
        return_value=UserInDB(id="123", email="someting@email.com", provider="apple")
    )
    result = user_service.get_user_by_id("123")
    assert isinstance(result, UserInDB)
    mock_user_data_access.get_user_by_id.assert_called_once_with("123")


def test_get_user_by_id_returns_none_when_user_not_found(
    user_service, mock_user_data_access
):
    mock_user_data_access.get_user_by_id = MagicMock(
        side_effect=CosmosResourceNotFoundError()
    )
    result = user_service.get_user_by_id("123")
    assert result is None
    mock_user_data_access.get_user_by_id.assert_called_once_with("123")


def test_create_user(user_service, mock_user_data_access):
    mock_user_data_access.create_user = MagicMock(
        return_value=UserInDB(id="123", email="example@email.com", provider="apple")
    )
    user_for_creation = UserOAuth(email="example@email.com", provider="apple")
    # Call the service method
    result = user_service.create_user(user_for_creation)
    assert isinstance(result, UserInDB)

    # Assert `create_user` was called correctly, focus on `email` and `provider`
    args, _ = mock_user_data_access.create_user.call_args
    assert args[0].email == "example@email.com"
    assert args[0].provider == "apple"
    assert mock_user_data_access.create_user.called_once


def test_authenticate_oauth_raises_exception_when_given_invalid_provider(
    user_service, mock_user_data_access
):
    mock_user_data_access.get_user_by_email = MagicMock(return_value=None)
    with pytest.raises(AuthenticationException, match="oAuth provider not supported"):
        user_service.authenticate_oauth(
            AuthRequest(token="token", provider="invalid_provider")
        )
    assert not mock_user_data_access.get_user_by_email.called


def test_authenticate_oauth_raises_exception_when_given_invalid_token(
    user_service, mock_user_data_access, monkeypatch, mock_decode_and_verify_token
):
    mock_decode_and_verify_token.side_effect = ValueError("Invalid token")
    monkeypatch.setattr(
        "app.service.user_service.decode_and_verify_token", mock_decode_and_verify_token
    )

    with pytest.raises(AuthenticationException, match="Unable to decode token"):
        user_service.authenticate_oauth(AuthRequest(token="token", provider="apple"))
    assert not mock_user_data_access.get_user_by_email.called


def test_authenticate_oauth_raises_exception_when_token_data_doesnt_contain_email_field(
    monkeypatch, user_service, mock_user_data_access, mock_decode_and_verify_token
):
    mock_user_data_access.get_user_by_email = MagicMock()
    mock_decode_and_verify_token.return_value = {"not an email field": 42}
    monkeypatch.setattr(
        "app.service.user_service.decode_and_verify_token", mock_decode_and_verify_token
    )

    with pytest.raises(AuthenticationException, match="Invalid token data"):
        user_service.authenticate_oauth(AuthRequest(token="token", provider="apple"))

    assert not mock_user_data_access.get_user_by_email.called


def test_authenticate_oauth_calls_create_user_when_user_for_auth_doesnt_exist(
    mock_user_data_access, user_service, monkeypatch, mock_decode_and_verify_token
):
    mock_decode_and_verify_token.return_value = {"email": "some_email@example.com"}
    monkeypatch.setattr(
        "app.service.user_service.decode_and_verify_token", mock_decode_and_verify_token
    )
    # User doesnt exist
    mock_user_data_access.get_user_by_email = MagicMock(return_value=None)
    mock_user_data_access.create_user = MagicMock(
        return_value=UserInDB(
            id="132", email="some_email@example.com", provider="apple"
        )
    )
    auth_request = AuthRequest(token="token", provider="apple")

    user_service.authenticate_oauth(auth_request)

    assert mock_user_data_access.create_user.called_once


def test_authenticate_oauth_returns_model_with_id__token_and_preferences_fields(
    mock_user_data_access, user_service, monkeypatch, mock_decode_and_verify_token
):
    mock_decode_and_verify_token.return_value = {"email": "some_email@example.com"}
    monkeypatch.setattr(
        "app.service.user_service.decode_and_verify_token", mock_decode_and_verify_token
    )
    # User doesnt exist
    mock_user_data_access.get_user_by_email = MagicMock(
        return_value=UserInDB(
            id="132", email="some_email@example.com", provider="apple"
        )
    )
    auth_request = AuthRequest(token="token", provider="apple")

    result = user_service.authenticate_oauth(auth_request)
    assert isinstance(result, UserInResponse)
    dumped_model = result.model_dump()
    assert dumped_model.get("id") is not None
    assert dumped_model.get("token") is not None
    assert dumped_model.get("preferences") is not None
    assert mock_user_data_access.get_user_by_email.called_once


def test_update_preferences_calls_get_user_by_id_in_service_class(user_service):
    user_service.get_user_by_id = MagicMock(
        return_value=UserInDB(
            id="132", email="some_email@example.com", provider="apple"
        )
    )
    preferences_for_update = Preferences(theme="system")
    user_id = "1"

    user_service.update_user_preferences(preferences_for_update, user_id)
    user_service.get_user_by_id.assert_called_once_with(user_id)


def test_update_preferences_raises_exception_when_user_not_found(user_service):
    user_service.get_user_by_id = MagicMock(return_value=None)
    preferences_for_update = Preferences(theme="system")
    user_id = "1"

    with pytest.raises(EntityNotFoundException):
        user_service.update_user_preferences(preferences_for_update, user_id)


def test_update_preferences_calls_data_access_method_with_updated_preferences(
    user_service, mock_user_data_access
):
    user_to_update = UserInDB(
        id="132",
        email="some_email@example.com",
        provider="apple",
        preferences=Preferences(theme="system"),
    )
    user_service.get_user_by_id = MagicMock(return_value=user_to_update)
    mock_user_data_access.update_user = MagicMock()
    preferences_for_update = Preferences(theme="light")
    user_id = "132"

    user_service.update_user_preferences(preferences_for_update, user_id)
    user_after_updating_preferences = UserInDB(
        id="132",
        email="some_email@example.com",
        provider="apple",
        preferences=preferences_for_update,
    )
    mock_user_data_access.update_user.assert_called_once_with(
        user_after_updating_preferences
    )


def test_sign_up_user_raises_exception_when_account_exists_with_requested_email(
    user_service, mock_user_data_access
):
    mock_user_data_access.get_user_by_email = MagicMock(
        return_value=UserInDB(email="something@email.com", id="1")
    )
    with pytest.raises(EntityAlreadyExistsException):
        user_service.sign_up_user(
            UserEmailAuthInSignUp(email="something@email.com", password="badpassword")
        )


def test_sign_up_user_hashes_plain_text_password(user_service, mock_user_data_access):
    mock_user_data_access.get_user_by_email = MagicMock(return_value=None)
    user_for_sign_up = UserEmailAuthInSignUp(
        email="something@email.com", password="badpassword"
    )
    with patch("app.service.user_service.get_password_hash") as mocked_pwrd_hash:
        user_service.sign_up_user(user_for_sign_up)
        mocked_pwrd_hash.assert_called_once_with(user_for_sign_up.password)


def test_sign_up_user_calls_create_user_with_hashed_password(
    user_service, mock_user_data_access
):
    mock_user_data_access.get_user_by_email = MagicMock(return_value=None)
    user_service.create_user = MagicMock()
    user_for_sign_up = UserEmailAuthInSignUp(
        email="something@email.com", password="badpassword"
    )
    with patch("app.service.user_service.get_password_hash", return_value="hashed"):
        user_service.sign_up_user(user_for_sign_up)
        args = user_service.create_user.call_args
        user_that_was_created = args[0][0]
        assert isinstance(user_that_was_created, UserEmailAuth)
        assert user_that_was_created.password_hash == "hashed"


def test_sign_up_user_returns_user_in_response_object(
    user_service, mock_user_data_access
):
    mock_user_data_access.get_user_by_email = MagicMock(return_value=None)
    user_service.create_user = MagicMock(
        return_value=UserInDB(email="doesntmatter@email.com", id="1")
    )
    user_in_response = user_service.sign_up_user(
        UserEmailAuthInSignUp(email="doesntmatter@email.com", password="badpassword")
    )
    assert isinstance(user_in_response, UserInResponse)
