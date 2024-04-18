from unittest.mock import MagicMock

import pytest
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError

from app.exceptions import (
    ExerciseDoesNotExistException,
    SetDoesNotExistException,
    UnauthorizedAccessException,
    UserDoesNotExistException,
)
from app.models.exercises_models import ExerciseInDB
from app.models.set_models import SetInCreate, SetInDB
from app.models.user_models import UserInDB
from app.service.set_service import SetService


@pytest.fixture
def mock_set_data_access():
    return MagicMock()


@pytest.fixture
def mock_user_service():
    return MagicMock()


@pytest.fixture
def mock_exercise_service():
    return MagicMock()


@pytest.fixture
def set_service(mock_set_data_access, mock_user_service, mock_exercise_service):
    return SetService(mock_set_data_access, mock_user_service, mock_exercise_service)


def test_get_set_by_id_calls_data_access_class_method(
    set_service, mock_set_data_access
):
    mock_set_data_access.get_set_by_id = MagicMock()
    set_service.get_set_by_id("1")

    mock_set_data_access.get_set_by_id.assert_called_once_with("1")


def test_get_sed_by_id_returns_none_when_cosmos_resource_not_found_exception(
    set_service, mock_set_data_access
):
    mock_set_data_access.get_set_by_id = MagicMock(
        side_effect=CosmosResourceNotFoundError()
    )
    assert set_service.get_set_by_id("1") is None


def test_get_users_sets_by_exercise_id(set_service, mock_set_data_access):
    mock_set_data_access.get_users_sets_by_exercise_id = MagicMock(return_value=[])
    set_service.get_users_sets_by_exercise_id("1", "2")
    mock_set_data_access.get_users_sets_by_exercise_id.assert_called_once_with(
        exercise_id="1", user_id="2"
    )
    mock_set_data_access.get_users_sets_by_exercise_id.assert_called_once()


def test_create_set_raises_exception_when_user_doesnt_exist(
    set_service, mock_user_service
):
    mock_user_service.get_user_by_id = MagicMock(return_value=None)
    set_service.user_service = mock_user_service
    with pytest.raises(UserDoesNotExistException):
        set_to_create = SetInCreate(exercise_id="1", reps=10, weight=100)
        set_service.create_set(set_to_create, "2")
    mock_user_service.get_user_by_id.assert_called_once_with("2")


def test_create_set_raises_exception_when_exercise_doesnt_exist(
    set_service, mock_user_service, mock_exercise_service
):
    # Just so we don't raise an exception for user not existing
    mock_user_service.get_user_by_id = MagicMock(return_value="user")
    mock_exercise_service.get_exercise_by_id = MagicMock(
        side_effect=ExerciseDoesNotExistException()
    )
    # We need to set the exercise service to the mock exercise service
    # and the user service to the mock user service
    set_service.exercise_service = mock_exercise_service
    set_service.user_service = mock_user_service
    with pytest.raises(ExerciseDoesNotExistException):
        set_to_create = SetInCreate(exercise_id="1", reps=10, weight=100)
        set_service.create_set(set_to_create, "2")
    mock_user_service.get_user_by_id.assert_called_once_with("2")


def test_create_set_creates_set(
    set_service, mock_user_service, mock_exercise_service, mock_set_data_access
):
    mock_user_service.get_user_by_id = MagicMock(
        return_value=UserInDB(id="2", email="something@something.com", provider="apple")
    )
    mock_exercise_service.get_exercise_by_id = MagicMock(
        return_value=ExerciseInDB(
            id="1", name="Bench Press", body_parts=[], creator="system"
        )
    )
    set_service.user_service = mock_user_service
    set_service.exercise_service = mock_exercise_service
    mock_set_data_access.create_set = MagicMock(
        return_value=SetInDB(
            exercise_id="1",
            reps=10,
            weight=100,
            date_created="2021-01-01",
            user_id="1",
            id="1",
        )
    )
    set_to_create = SetInCreate(exercise_id="1", reps=10, weight=100)
    set_service.create_set(set_to_create, "2")
    mock_set_data_access.create_set.assert_called_once()
    mock_user_service.get_user_by_id.assert_called_once_with("2")
    mock_exercise_service.get_exercise_by_id.assert_called_once_with("1")


def test_delete_set_raises_exception_when_set_does_not_exist(set_service):
    set_service.get_set_by_id = MagicMock(return_value=None)

    with pytest.raises(SetDoesNotExistException):
        set_service.delete_set("1", "1")


def test_delete_set_raises_exception_when_set_doesnt_belong_to_user_requesting(
    set_service,
):
    user_id = "1"
    sets_user_id = "9"
    set_service.get_set_by_id = MagicMock(
        return_value=SetInDB(
            id="1",
            exercise_id="1",
            weight=10,
            reps=10,
            date_created="",
            user_id=sets_user_id,
        )
    )

    with pytest.raises(UnauthorizedAccessException):
        set_service.delete_set("1", user_id)


def test_delete_set_returns_false_when_cosmos_http_error(
    set_service, mock_set_data_access
):
    mock_set_data_access.get_set_by_id = MagicMock(
        return_value=SetInDB(
            id="1",
            exercise_id="1",
            weight=10,
            reps=10,
            date_created="",
            user_id="1",
        )
    )
    mock_set_data_access.delete_set = MagicMock(side_effect=CosmosHttpResponseError())
    assert set_service.delete_set("1", "1") is False


def test_delete_set_returns_true_when_all_goes_well(set_service, mock_set_data_access):
    mock_set_data_access.get_set_by_id = MagicMock(
        return_value=SetInDB(
            id="1",
            exercise_id="1",
            weight=10,
            reps=10,
            date_created="",
            user_id="1",
        )
    )
    mock_set_data_access.delete_set = MagicMock()
    assert set_service.delete_set("1", "1") is True