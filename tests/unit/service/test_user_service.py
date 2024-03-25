import pytest
from unittest.mock import MagicMock, ANY
from app.service.user_service import UserService
from app.models.user_models import BaseUser, UserInDB


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
