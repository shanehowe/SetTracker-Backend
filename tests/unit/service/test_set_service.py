from unittest.mock import MagicMock

import pytest

from app.exceptions import ExerciseDoesNotExistException, UserDoesNotExistException
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


def test_get_users_sets_by_exercise_id(set_service, mock_set_data_access):
    mock_set_data_access.get_users_sets_by_exercise_id = MagicMock(return_value=[])
    set_service.get_users_sets_by_exercise_id("1", "2")
    mock_set_data_access.get_users_sets_by_exercise_id.assert_called_once_with(
        exercise_id="1", user_id="2"
    )


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
