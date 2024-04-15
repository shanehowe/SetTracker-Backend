from unittest.mock import MagicMock

import pytest
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.data_access.user import UserDataAccess
from app.exceptions import AuthenticationException
from app.models.auth_models import AuthRequest
from app.models.user_models import BaseUser, UserInDB
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
    user_for_creation = BaseUser(email="example@email.com", provider="apple")
    # Call the service method
    result = user_service.create_user(user_for_creation)
    assert isinstance(result, UserInDB)

    # Assert `create_user` was called correctly, focus on `email` and `provider`
    args, _ = mock_user_data_access.create_user.call_args
    assert args[0].email == "example@email.com"
    assert args[0].provider == "apple"
    assert mock_user_data_access.create_user.called_once


def test_authenticate_raises_exception_when_given_invalid_provider(
    user_service, mock_user_data_access
):
    mock_user_data_access.get_user_by_email = MagicMock(return_value=None)
    with pytest.raises(AuthenticationException, match="oAuth provider not supported"):
        user_service.authenticate(
            AuthRequest(token="token", provider="invalid_provider")
        )
    assert not mock_user_data_access.get_user_by_email.called


def test_authenticate_raises_exception_when_given_invalid_token(
    user_service, mock_user_data_access, monkeypatch, mock_decode_and_verify_token
):
    mock_decode_and_verify_token.side_effect = ValueError("Invalid token")
    monkeypatch.setattr(
        "app.service.user_service.decode_and_verify_token", mock_decode_and_verify_token
    )

    with pytest.raises(AuthenticationException, match="Unable to decode token"):
        user_service.authenticate(AuthRequest(token="token", provider="apple"))
    assert not mock_user_data_access.get_user_by_email.called


def test_authenticate_raises_exception_when_token_data_doesnt_contain_email_field(
    monkeypatch, user_service, mock_user_data_access, mock_decode_and_verify_token
):
    mock_user_data_access.get_user_by_email = MagicMock()
    mock_decode_and_verify_token.return_value = {"not an email field": 42}
    monkeypatch.setattr(
        "app.service.user_service.decode_and_verify_token", mock_decode_and_verify_token
    )

    with pytest.raises(AuthenticationException, match="Invalid token data"):
        user_service.authenticate(AuthRequest(token="token", provider="apple"))

    assert not mock_user_data_access.get_user_by_email.called


def test_authenticate_calls_create_user_when_user_for_auth_doesnt_exist(
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

    user_service.authenticate(auth_request)

    assert mock_user_data_access.create_user.called_once


def test_authenticate_returns_dict_with_id_and_token_field(
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

    result = user_service.authenticate(auth_request)
    assert isinstance(result, dict)
    assert result.get("id") is not None
    assert result.get("token") is not None
    assert mock_user_data_access.get_user_by_email.called_once
