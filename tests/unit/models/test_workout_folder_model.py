import pytest
from pydantic import ValidationError

from app.models.workout_folder_models import (
    WorkoutFolderInDB,
    WorkoutFolderInRequest,
    WorkoutFolderInUpdate,
)


@pytest.fixture
def name_too_long():
    return "a" * 21


@pytest.fixture
def name_empty():
    return ""


def test_workout_folder_in_db_raises_exception_when_name_is_empty(name_empty):
    with pytest.raises(ValidationError):
        WorkoutFolderInDB(id="1", name=name_empty, user_id="1")


def test_workout_folder_in_db_raises_exception_when_name_is_too_long(name_too_long):
    with pytest.raises(ValidationError):
        WorkoutFolderInDB(
            id="1",
            name=name_too_long,
            user_id="1",
        )


@pytest.mark.parametrize("name", ["a", "a" * 20])
def test_workout_folder_in_db_handles_boundary_cases(name):
    try:
        WorkoutFolderInDB(id="1", name=name, user_id="1")
    except ValidationError:
        pytest.fail(f"ValidationError was raised. Failed on: {name}")


def test_workout_folder_in_request_raises_exception_when_name_is_empty(name_empty):
    with pytest.raises(ValidationError):
        WorkoutFolderInRequest(name=name_empty, exercises=[])


def test_workout_folder_in_request_raises_exception_when_name_is_too_long(
    name_too_long,
):
    with pytest.raises(ValidationError):
        WorkoutFolderInRequest(
            name=name_too_long,
            exercises=[],
        )


@pytest.mark.parametrize("name", ["a", "a" * 20])
def test_workout_folder_in_request_handles_boundary_cases(name):
    try:
        WorkoutFolderInRequest(name=name, exercises=[])
    except ValidationError:
        pytest.fail(f"ValidationError was raised. Failed on: {name}")


def test_workout_folder_in_update_raises_exception_when_name_is_empty(name_empty):
    with pytest.raises(ValidationError):
        WorkoutFolderInUpdate(name=name_empty, exercises=[])


def test_workout_folder_in_update_raises_exception_when_name_is_too_long(name_too_long):
    with pytest.raises(ValidationError):
        WorkoutFolderInUpdate(
            name=name_too_long,
            exercises=[],
        )


def test_workout_folder_in_update_allows_none_value_for_name():
    try:
        WorkoutFolderInUpdate(name=None, exercises=[])
    except ValidationError:
        pytest.fail("ValidationError was raised. Failed on: None")
