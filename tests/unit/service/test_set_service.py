from unittest.mock import MagicMock

import pytest

from app.exceptions import ExerciseDoesNotExistException, UserDoesNotExistException
from app.models.set_models import SetInCreate, SetInDB
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
def set_service(mock_set_data_access):
    return SetService(mock_set_data_access)


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
