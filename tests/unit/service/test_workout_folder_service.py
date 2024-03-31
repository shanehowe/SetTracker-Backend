import pytest
from unittest.mock import MagicMock
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.exceptions import UnauthorizedAccessException
from app.service.workout_folder_service import WorkoutFolderService
from app.models.workout_folder_models import WorkoutFolderInDB, WorkoutFolderInRequest


@pytest.fixture
def mock_workout_folder_data_access():
    return MagicMock()


@pytest.fixture
def workout_folder_service(mock_workout_folder_data_access):
    return WorkoutFolderService(
        workout_folder_data_access=mock_workout_folder_data_access
    )


def test_get_workout_folder_by_id(mock_workout_folder_data_access, workout_folder_service):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="123", user_id="123", name="test folder", exercises=[]
    )
    folder = workout_folder_service.get_folder_by_id("123", "123")
    assert folder.id == "123"
    assert folder.user_id == "123"
    assert folder.name == "test folder"
    assert folder.exercises == []


def test_get_workout_folder_by_id_returns_none_when_folder_not_found(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id.side_effect = CosmosResourceNotFoundError()
    folder = workout_folder_service.get_folder_by_id("123", "123")
    assert folder is None


def test_get_workout_folder_by_id_raises_unauthorized_exception(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="123", user_id="123", name="test folder", exercises=[]
    )
    with pytest.raises(UnauthorizedAccessException):
        workout_folder_service.get_folder_by_id("123", "456")
