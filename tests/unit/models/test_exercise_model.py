import pytest
from pydantic import ValidationError

from app.models.exercises_models import ExerciseInCreate


def test_exercise_in_create_raises_exception_when_name_is_empty():
    with pytest.raises(ValidationError):
        ExerciseInCreate(name="")


def test_exercise_in_create_raises_exception_when_name_is_too_long():
    with pytest.raises(ValidationError):
        ExerciseInCreate(name="a" * 31)


@pytest.mark.parametrize("name", ["aaaaa", "a" * 30])
def test_exercise_in_create_handles_boundary_cases(name):
    try:
        ExerciseInCreate(name=name)
    except ValidationError:
        pytest.fail(f"ValidationError was raised. Failed on: {name}")