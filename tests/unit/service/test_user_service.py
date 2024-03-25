import pytest
from unittest.mock import MagicMock
from app.service.user_service import UserService
from app.models.user_models import BaseUser, UserInDB
from app.models.auth_models import AuthRequest
from app.exceptions import AuthenticationException
import app.auth.tokens


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
    monkeypatch.setattr(
        app.auth.tokens,
        "decode_and_verify_token",
        MagicMock(side_effect=app.auth.tokens.UnsupportedProviderException)
    )

    with pytest.raises(AuthenticationException, match="oAuth provider not supported"):
        user_service.authenticate(AuthRequest(token="token", provider="invalid_provider"))
    assert not mock_user_data_access.get_user_by_email.called
