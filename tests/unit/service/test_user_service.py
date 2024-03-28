import pytest
from unittest.mock import MagicMock
from app.service.user_service import UserService
from app.models.user_models import BaseUser, UserInDB
from app.models.auth_models import AuthRequest
from app.exceptions import AuthenticationException


@pytest.fixture
def mock_user_data_access():
    return MagicMock()


@pytest.fixture
def user_service(mock_user_data_access):
    return UserService(user_data_access=mock_user_data_access)


def test_create_user(user_service, mock_user_data_access):
    mock_user_data_access.create_user.return_value = UserInDB(
        id="123",
        email="example@email.com",
        provider="apple"
    )
    user_for_creation = BaseUser(email="example@email.com", provider="apple")
    # Call the service method
    result = user_service.create_user(user_for_creation)
    assert isinstance(result, UserInDB)

    # Assert `create_user` was called correctly, focus on `email` and `provider`
    args, _ = mock_user_data_access.create_user.call_args
    assert args[0].email == "example@email.com"
    assert args[0].provider == "apple"


def test_authenticate_raises_exception_when_given_invalid_provider(user_service, mock_user_data_access, monkeypatch):
    with pytest.raises(AuthenticationException, match="oAuth provider not supported"):
        user_service.authenticate(AuthRequest(token="token", provider="invalid_provider"))
    assert not mock_user_data_access.get_user_by_email.called


def test_authenticate_raises_exception_when_given_invalid_token(user_service, mock_user_data_access, monkeypatch):
    mock_decode_and_verify_token = MagicMock()
    mock_decode_and_verify_token.side_effect = ValueError("Invalid token")
    monkeypatch.setattr("app.service.user_service.decode_and_verify_token", mock_decode_and_verify_token)

    with pytest.raises(AuthenticationException, match="Unable to decode token"):
        user_service.authenticate(AuthRequest(token="token", provider="apple"))
    assert not mock_user_data_access.get_user_by_email.called
