import pytest
from unittest.mock import MagicMock
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from app.exceptions import UnauthorizedAccessException
from app.models.exercises_models import ExerciseInDB
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
            id="123",
            user_id="123",
            name="updated folder",
            exercises=[ExerciseInDB(id="1", name="test", body_parts=[], creator="123")],
        )
    )
    updated_folder = workout_folder_service.update_workout_folder(
        "123",
        WorkoutFolderInUpdate(
            name="updated folder",
            exercises=[ExerciseInDB(id="1", name="test", body_parts=[], creator="123")],
        ),
        "123",
    )
    assert updated_folder.id == "123"
    assert updated_folder.user_id == "123"
    assert updated_folder.name == "updated folder"
    assert updated_folder.exercises == [
        ExerciseInDB(id="1", name="test", body_parts=[], creator="123")
    ]
    mock_workout_folder_data_access.update_workout_folder.assert_called_with(
        WorkoutFolderInDB(
            id="123",
            user_id="123",
            name="updated folder",
            exercises=[ExerciseInDB(id="1", name="test", body_parts=[], creator="123")],
        )
    )


def test_update_workout_folder_raises_unauthorized_exception(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="123", user_id="123", name="test folder", exercises=[]
    )
    with pytest.raises(UnauthorizedAccessException):
        workout_folder_service.update_workout_folder(
            "123",
            WorkoutFolderInUpdate(name="updated folder", exercises=[]),
            "456",
        )


def test_update_workout_folder_returns_none_when_resource_doesnt_exist(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id.side_effect = (
        CosmosResourceNotFoundError()
    )

    assert (
        workout_folder_service.update_workout_folder(
            "123",
            WorkoutFolderInUpdate(
                name="updated folder",
                exercises=[
                    ExerciseInDB(id="1", name="test", body_parts=[], creator="123")
                ],
            ),
            "123",
        )
        is None
    )


def test_delete_folder_returns_true_when_folder_exists(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="1", user_id="1", name="folder", exercises=[]
    )
    result = workout_folder_service.delete_workout_folder("1", "1")
    assert result is True
    mock_workout_folder_data_access.get_folder_by_id.assert_called_with("1")


def test_delete_folder_raises_value_error_when_folder_doesnt_exist(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id.side_effect = (
        CosmosResourceNotFoundError()
    )
    with pytest.raises(ValueError):
        workout_folder_service.delete_workout_folder("1", "1")


def test_delete_folder_returns_false_when_cosmos_errors(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="1", user_id="1", name="folder", exercises=[]
    )
    mock_workout_folder_data_access.delete_workout_folder.side_effect = (
        CosmosHttpResponseError()
    )

    assert workout_folder_service.delete_workout_folder("1", "1") is False


def test_delete_folder_raises_unauthorized_access_exception_when_folder_does_not_belong_to_user(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="1", user_id="2", name="folder", exercises=[]
    )

    with pytest.raises(UnauthorizedAccessException):
        workout_folder_service.delete_workout_folder("1", "1")
