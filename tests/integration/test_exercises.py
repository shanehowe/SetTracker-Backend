import pytest


@pytest.fixture
def created_exercise(logged_in_client, exercises_cosmos_client):
    response = logged_in_client.post("/exercises/", json={"name": "Exercise"})
    json = response.json()
    yield json
    exercises_cosmos_client.delete_item(json["id"], partition_key=json["id"])


def test_get_all_exercises_returns_status_200_and_list_of_exercises(
    logged_in_client, created_exercise, user
):
    """
    Test that get all exercises returns a 200 status code and list of exercises including
    custom ones.
    """
    response = logged_in_client.get("/exercises/")
    exercise_list = response.json()
    assert response.status_code == 200
    assert isinstance(exercise_list, list)

    custom_exercises = list(filter(lambda x: x["creator"] == user.id, exercise_list))
    assert len(custom_exercises) == 1


@pytest.mark.parametrize("name", ["" "aaaa" "a" * 31])
def test_create_custom_exercise_with_invalid_names(logged_in_client, name):
    """
    Test that creating a custom exercise with invalid names returns a 422 status code.
    """
    response = logged_in_client.post("/exercises/", json={"name": name})
    assert response.status_code == 422


def test_create_custom_with_valid_name(logged_in_client, exercises_cosmos_client):
    """
    Test that creating a custom exercise with a valid name returns a 201 status code and the
    created exercise.
    """
    response = logged_in_client.post("/exercises/", json={"name": "Exercise"})
    json_resp = response.json()

    assert response.status_code == 201
    assert json_resp["name"] == "Exercise"

    # Clean up
    exercise_id = json_resp["id"]
    exercises_cosmos_client.delete_item(exercise_id, partition_key=exercise_id)


def test_create_custom_exercise_already_exists(logged_in_client, created_exercise):
    """
    Test that creating a custom exercise with a name that already exists returns a 400 status code.
    """
    response = logged_in_client.post(
        "/exercises/", json={"name": created_exercise["name"]}
    )
    json = response.json()

    assert response.status_code == 400
    assert json["detail"] == f"{created_exercise.get('name')} already exists"
