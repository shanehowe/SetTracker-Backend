import pytest
from unittest.mock import MagicMock
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.exceptions import UnauthorizedAccessException
from app.service.workout_folder_service import WorkoutFolderService
from app.models.workout_folder_models import (
    WorkoutFolderInDB,
    WorkoutFolderInUpdate,
)


@pytest.fixture
def mock_workout_folder_data_access():
    return MagicMock()


@pytest.fixture
def workout_folder_service(mock_workout_folder_data_access):
    return WorkoutFolderService(
        workout_folder_data_access=mock_workout_folder_data_access
    )


def test_get_workout_folder_by_id(
    mock_workout_folder_data_access, workout_folder_service
):
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
    mock_workout_folder_data_access.get_folder_by_id.side_effect = (
        CosmosResourceNotFoundError()
    )
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


def test_get_users_workout_folders(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_users_workout_folders.return_value = [
        WorkoutFolderInDB(id="123", user_id="123", name="test folder", exercises=[])
    ]
    folders = workout_folder_service.get_users_workout_folders("123")
    assert len(folders) == 1
    assert folders[0].id == "123"
    assert folders[0].user_id == "123"
    assert folders[0].name == "test folder"
    assert folders[0].exercises == []


def test_update_workout_folder(mock_workout_folder_data_access, workout_folder_service):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="123", user_id="123", name="test folder", exercises=[]
    )
    mock_workout_folder_data_access.update_workout_folder.return_value = (
        WorkoutFolderInDB(
            id="123", user_id="123", name="updated folder", exercises=["exercise1"]
        )
    )
    updated_folder = workout_folder_service.update_workout_folder(
        "123",
        WorkoutFolderInUpdate(name="updated folder", exercises=["exercise1"]),
        "123",
    )
    assert updated_folder.id == "123"
    assert updated_folder.user_id == "123"
    assert updated_folder.name == "updated folder"
    assert updated_folder.exercises == ["exercise1"]


def test_update_workout_folder_raises_unauthorized_exception(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="123", user_id="123", name="test folder", exercises=[]
    )
    with pytest.raises(UnauthorizedAccessException):
        workout_folder_service.update_workout_folder(
            "123",
            WorkoutFolderInUpdate(name="updated folder", exercises=["exercise1"]),
            "456",
        )


def test_update_workout_folder_returns_none_when_resource_doesnt_exist(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id.side_effect = (
        CosmosResourceNotFoundError()
    )

    assert workout_folder_service.update_workout_folder(
        "123",
        WorkoutFolderInUpdate(name="updated folder", exercises=["exercise1"]),
        "123",
    ) is None
