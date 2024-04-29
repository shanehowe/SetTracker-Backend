from unittest.mock import MagicMock

import pytest
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

from app.exceptions import EntityNotFoundException, UnauthorizedAccessException
from app.models.exercises_models import ExerciseInDB
from app.models.workout_folder_models import (
    WorkoutFolderInDB,
    WorkoutFolderInRequest,
    WorkoutFolderInUpdate,
)
from app.service.workout_folder_service import WorkoutFolderService


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
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        return_value=WorkoutFolderInDB(
            id="123", user_id="123", name="test folder", exercises=[]
        )
    )
    folder = workout_folder_service.get_folder_by_id("123", "123")
    assert folder.id == "123"
    assert folder.user_id == "123"
    assert folder.name == "test folder"
    assert folder.exercises == []
    mock_workout_folder_data_access.get_folder_by_id.assert_called_once_with("123")


def test_get_workout_folder_by_id_returns_none_when_folder_not_found(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        side_effect=CosmosResourceNotFoundError()
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
    mock_workout_folder_data_access.get_users_workout_folders = MagicMock(
        return_value=[
            WorkoutFolderInDB(id="123", user_id="123", name="test folder", exercises=[])
        ]
    )
    folders = workout_folder_service.get_users_workout_folders("123")
    assert len(folders) == 1
    assert folders[0].id == "123"
    assert folders[0].user_id == "123"
    assert folders[0].name == "test folder"
    assert folders[0].exercises == []


def test_create_workout_folder_adds_empty_list_when_exercises_field_is_none(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.create_workout_folder = MagicMock(
        return_value=WorkoutFolderInDB(id="1", name="name", user_id="1", exercises=[])
    )
    workout_folder_service.create_workout_folder(
        WorkoutFolderInRequest(name="name", exercises=None), "1"
    )
    created_folder = (
        mock_workout_folder_data_access.create_workout_folder.call_args.args[0]
    )
    assert isinstance(created_folder, WorkoutFolderInDB)
    assert isinstance(created_folder.exercises, list)
    assert len(created_folder.exercises) == 0


def test_update_workout_folder(mock_workout_folder_data_access, workout_folder_service):
    mock_workout_folder_data_access.get_folder_by_id.return_value = WorkoutFolderInDB(
        id="123", user_id="123", name="test folder", exercises=[]
    )
    mock_workout_folder_data_access.update_workout_folder = MagicMock(
        return_value=(
            WorkoutFolderInDB(
                id="123",
                user_id="123",
                name="updated folder",
                exercises=[
                    ExerciseInDB(id="1", name="test", body_parts=[], creator="123")
                ],
            )
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


def test_update_folder_raises_value_error_when_name_and_exercises_are_none(
    workout_folder_service,
):
    data_to_update = WorkoutFolderInUpdate(name=None, exercises=None)
    with pytest.raises(ValueError):
        workout_folder_service.update_workout_folder("1", data_to_update, "123")


def test_update_workout_folder_raises_unauthorized_exception(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        return_value=WorkoutFolderInDB(
            id="123", user_id="123", name="test folder", exercises=[]
        )
    )
    with pytest.raises(UnauthorizedAccessException):
        workout_folder_service.update_workout_folder(
            "123",
            WorkoutFolderInUpdate(name="updated folder", exercises=[]),
            "456",
        )
    assert not mock_workout_folder_data_access.update_workout_folder.called


def test_update_workout_folder_returns_none_when_resource_doesnt_exist(
    mock_workout_folder_data_access, workout_folder_service
):
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        side_effect=CosmosResourceNotFoundError()
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
    assert not mock_workout_folder_data_access.update_workout_folder.called


def test_delete_folder_returns_true_when_folder_exists(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        return_value=WorkoutFolderInDB(id="1", user_id="1", name="folder", exercises=[])
    )
    result = workout_folder_service.delete_workout_folder("1", "1")
    assert result is True
    mock_workout_folder_data_access.get_folder_by_id.assert_called_with("1")


def test_delete_folder_raises_value_error_when_folder_doesnt_exist(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        side_effect=(CosmosResourceNotFoundError())
    )
    with pytest.raises(EntityNotFoundException):
        workout_folder_service.delete_workout_folder("1", "1")
    assert not mock_workout_folder_data_access.delete_workout_folder.called


def test_delete_folder_returns_false_when_cosmos_errors(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        return_value=WorkoutFolderInDB(id="1", user_id="1", name="folder", exercises=[])
    )
    mock_workout_folder_data_access.delete_workout_folder.side_effect = (
        CosmosHttpResponseError()
    )

    assert workout_folder_service.delete_workout_folder("1", "1") is False
    mock_workout_folder_data_access.delete_workout_folder.assert_called_once_with("1")


def test_delete_folder_raises_unauthorized_access_exception_when_folder_does_not_belong_to_user(
    workout_folder_service, mock_workout_folder_data_access
):
    mock_workout_folder_data_access.get_folder_by_id = MagicMock(
        return_value=WorkoutFolderInDB(id="1", user_id="2", name="folder", exercises=[])
    )

    with pytest.raises(UnauthorizedAccessException):
        workout_folder_service.delete_workout_folder("1", "1")
