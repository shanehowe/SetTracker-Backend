from unittest.mock import MagicMock

import pytest
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.exceptions import ExerciseAlreadyExistsException
from app.models.exercises_models import ExerciseInCreate, ExerciseInDB
from app.service.exercise_service import ExerciseService


@pytest.fixture
def mock_exercise_data_access():
    return MagicMock()


@pytest.fixture
def exercise_service(mock_exercise_data_access):
    return ExerciseService(mock_exercise_data_access)


def test_get_exercise_by_id_returns_none_when_exercise_not_found(
    exercise_service, mock_exercise_data_access
):
    mock_exercise_data_access.get_exercise_by_id = MagicMock(
        side_effect=CosmosResourceNotFoundError()
    )
    result = exercise_service.get_exercise_by_id("123")
    assert result is None
    mock_exercise_data_access.get_exercise_by_id.assert_called_once_with("123")


def test_get_exercise_by_id_returns_exercise_when_found(
    exercise_service, mock_exercise_data_access
):
    mock_exercise_data_access.get_exercise_by_id = MagicMock(
        return_value=ExerciseInDB(
            id="123", name="name", body_parts=[], creator="system"
        )
    )
    result = exercise_service.get_exercise_by_id("123")
    assert isinstance(result, ExerciseInDB)
    mock_exercise_data_access.get_exercise_by_id.assert_called_once_with("123")


def test_get_system_and_user_exercises(exercise_service, mock_exercise_data_access):
    mock_exercise_data_access.get_system_and_user_exercises = MagicMock(return_value=[])

    exercise_service.get_system_and_user_exercises("1")
    mock_exercise_data_access.get_system_and_user_exercises.assert_called_once_with("1")


def test_create_custom_exercise_raises_exception_when_exercise_exists(
    exercise_service, mock_exercise_data_access
):
    mock_exercise_data_access.get_exercise_by_name = MagicMock(
        return_value=ExerciseInDB(
            id="1", name="some name", body_parts=[], creator="system"
        )
    )
    with pytest.raises(ExerciseAlreadyExistsException):
        exercise_service.create_custom_exercise(
            ExerciseInCreate(name="some name"), "12"
        )
    assert not mock_exercise_data_access.create_custom_exercise.called


def test_create_custom_exercise_creates_exercise_with_same_name_as_pass_in_argument(
    exercise_service, mock_exercise_data_access
):
    exercise_name = "exercise"
    mock_exercise_data_access.get_exercise_by_name = MagicMock(return_value=None)
    mock_exercise_data_access.create_custom_exercise = MagicMock(
        return_value=ExerciseInDB(
            id="123", name=exercise_name, body_parts=[], creator="1"
        )
    )
    # Discard return type as its mocked. Do assertions on the call args.
    exercise_service.create_custom_exercise(ExerciseInCreate(name=exercise_name), "1")
    mock_exercise_data_access.create_custom_exercise.assert_called_once()
    arg = mock_exercise_data_access.create_custom_exercise.call_args.args[0]
    assert isinstance(arg, ExerciseInDB)
    assert arg.name == exercise_name
    assert arg.creator == "1"
