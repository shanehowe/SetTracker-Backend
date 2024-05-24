import pytest

from app.data_access.exercise import ExerciseDataAccess
from app.data_access.set import SetDataAccess
from app.models.set_models import SetInDB


@pytest.fixture
def exercise_data_access():
    return ExerciseDataAccess()


@pytest.fixture
def set_data_access():
    return SetDataAccess()


@pytest.fixture
def set_with_different_user_id(set_data_access, single_exercise):
    set_ = SetInDB(
        exercise_id=single_exercise.id,
        reps=10,
        weight=100,
        user_id="999999",
        id="1",
        date_created="i know its wrong but i dont care",
    )
    yield set_data_access.create_set(set_)
    set_data_access.delete_set(set_.id)


@pytest.fixture
def single_exercise(exercise_data_access, user):
    exercise = exercise_data_access.get_exercise_by_name("Bench Press", user.id)
    assert exercise is not None
    return exercise


def test_get_sets_returns_status_200_and_json_list(logged_in_client, single_exercise):
    response = logged_in_client.get(f"/sets/{single_exercise.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_set_returns_status_201_and_json_dict(logged_in_client, single_exercise):
    response = logged_in_client.post(
        "/sets/",
        json={
            "exercise_id": single_exercise.id,
            "reps": 10,
            "weight": 100,
        },
    )
    assert response.status_code == 201
    assert isinstance(response.json(), dict)


def test_create_set_when_exercise_does_not_exist_returns_status_400_and_error_message(
    logged_in_client,
):
    response = logged_in_client.post(
        "/sets/",
        json={
            "exercise_id": "non_existent_id",
            "reps": 10,
            "weight": 100,
        },
    )
    assert response.status_code == 400
    assert "Exercise with ID non_existent_id does not exist" in response.text


def test_delete_set_returns_status_204(logged_in_client, single_exercise):
    response = logged_in_client.post(
        "/sets/",
        json={
            "exercise_id": single_exercise.id,
            "reps": 10,
            "weight": 100,
        },
    )
    set_id = response.json()["id"]
    response = logged_in_client.delete(f"/sets/{set_id}")
    assert response.status_code == 204


def test_delete_set_when_set_does_not_exist_returns_status_400_and_error_message(
    logged_in_client,
):
    response = logged_in_client.delete("/sets/non_existent_id")
    assert response.status_code == 400
    assert response.json()["detail"] == "Set with ID non_existent_id does not exist"


def test_delete_set_when_set_belongs_to_different_user_returns_status_401_and_error_message(
    logged_in_client, set_with_different_user_id
):
    response = logged_in_client.delete(f"/sets/{set_with_different_user_id.id}")
    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Only the person who created this set can delete it"
    )
