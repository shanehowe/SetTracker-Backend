import pytest
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from fastapi.testclient import TestClient

from app.data_access.workout_folder import WorkoutFolderDataAccess
from app.models.exercises_models import ExerciseInDB
from app.models.user_models import UserInDB
from app.models.workout_folder_models import WorkoutFolderInDB


@pytest.fixture
def list_of_workout_folders(user: UserInDB):
    return [
        WorkoutFolderInDB(
            id="1",
            name="Folder 1",
            user_id=user.id,
            exercises=[],
        ),
        WorkoutFolderInDB(
            id="2",
            name="Folder 2",
            user_id=user.id,
            exercises=[],
        ),
        # WorkoutFolder not belonging to the user
        WorkoutFolderInDB(
            id="3",
            name="Folder 3",
            user_id="2",
            exercises=[],
        ),
    ]


@pytest.fixture(autouse=True)
def setup_module(
    workout_folder_data_access: WorkoutFolderDataAccess,
    list_of_workout_folders: list[WorkoutFolderInDB],
):
    for folder in list_of_workout_folders:
        workout_folder_data_access.create_workout_folder(folder)
    yield list_of_workout_folders
    for folder in list_of_workout_folders:
        try:
            workout_folder_data_access.delete_workout_folder(folder.id)
        except CosmosResourceNotFoundError:
            pass  # Folder was already deleted


def test_get_users_folders(logged_in_client: TestClient, user: UserInDB):
    """
    Test that the endpoint returns the correct workout folders for the user
    API returns json in camelCase
    """
    response = logged_in_client.get("/workout-folders/")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
    assert json_response == [
        {"id": "1", "name": "Folder 1", "exercises": [], "userId": user.id},
        {"id": "2", "name": "Folder 2", "exercises": [], "userId": user.id},
    ]


def test_get_folder_by_id(logged_in_client: TestClient):
    """
    Test that the endpoint returns the correct workout folder for the user
    """
    response = logged_in_client.get("/workout-folders/1")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response == {
        "id": "1",
        "name": "Folder 1",
        "exercises": [],
        "userId": "1",
    }


def test_get_folder_by_id_not_found(logged_in_client: TestClient):
    """
    Test that the endpoint returns 400 if the folder does not exist
    """
    response = logged_in_client.get("/workout-folders/100")
    assert response.status_code == 400
    assert response.json() == {"detail": "Folder with requested id does not exist"}


def test_get_folder_by_id_not_authorized(logged_in_client: TestClient):
    """
    Test that the endpoint returns 401 if the folder does not belong to the user
    """
    response = logged_in_client.get("/workout-folders/3")
    assert response.status_code == 401
    assert response.json() == {"detail": "You do not have access to this folder"}


def test_create_workout_folder(
    logged_in_client: TestClient,
    user: UserInDB,
    workout_folder_data_access: WorkoutFolderDataAccess,
    setup_module,
):
    """
    Test that the endpoint creates a workout folder
    """
    response = logged_in_client.post(
        "/workout-folders/",
        json={"name": "New Folder", "exercises": []},
    )
    assert response.status_code == 201
    json_response = response.json()
    assert json_response == {
        "id": json_response["id"],
        "name": "New Folder",
        "exercises": [],
        "userId": user.id,
    }
    assert (
        workout_folder_data_access.get_folder_by_id(json_response["id"]).name
        == "New Folder"
    )
    # Cleanup
    workout_folder_data_access.delete_workout_folder(json_response["id"])


@pytest.mark.parametrize(
    "folder_name, message",
    [
        ("a" * 21, "name: should have at most 20 characters"),
        ("" * 0, "name: should have at least 1 character"),
    ],
)
def test_create_folder_with_invalid_folder_name(
    logged_in_client: TestClient, folder_name, message, setup_module
):
    """
    Test that the endpoint returns 422 if the folder name is invalid
    """
    response = logged_in_client.post(
        "/workout-folders/",
        json={"name": folder_name, "exercises": []},
    )
    assert response.status_code == 422
    assert response.json() == {"detail": [message]}


def test_update_workout_folder_name(logged_in_client: TestClient, user: UserInDB):
    """
    Test that the endpoint updates a workout folder
    """
    response = logged_in_client.put(
        "/workout-folders/1",
        json={"name": "Updated Folder", "exercises": []},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response == {
        "id": "1",
        "name": "Updated Folder",
        "exercises": [],
        "userId": user.id,
    }


def test_update_workout_folder_exercises(
    logged_in_client: TestClient, user: UserInDB, setup_module
):
    """
    Test case for updating workout folder exercises.
    """
    exercises = [
        ExerciseInDB(
            id="1", name="Exercise 1", user_id=user.id, body_parts=[], creator="system"
        ).model_dump(by_alias=True),
        ExerciseInDB(
            id="2", name="Exercise 2", user_id=user.id, body_parts=[], creator="system"
        ).model_dump(by_alias=True),
    ]

    response = logged_in_client.put(
        "/workout-folders/1",
        json={"exercises": exercises},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["exercises"] == exercises


def test_update_workout_folder_name_and_exercises(
    logged_in_client: TestClient, user: UserInDB
):
    """
    Test case for updating the name and exercises of a workout folder.
    """
    exercises = [
        ExerciseInDB(
            id="1", name="Exercise 1", user_id=user.id, body_parts=[], creator="system"
        ).model_dump(by_alias=True),
        ExerciseInDB(
            id="2", name="Exercise 2", user_id=user.id, body_parts=[], creator="system"
        ).model_dump(by_alias=True),
    ]

    response = logged_in_client.put(
        "/workout-folders/1",
        json={"name": "Updated Folder", "exercises": exercises},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response == {
        "id": "1",
        "name": "Updated Folder",
        "exercises": exercises,
        "userId": user.id,
    }


def test_update_workout_folder_no_data(logged_in_client: TestClient, setup_module):
    """
    Test that the endpoint returns 422 if no data is provided
    """
    response = logged_in_client.put("/workout-folders/1", json={})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Folder name or exercises must be provided to update folder"
    }


def test_update_workout_folder_not_authorized(
    logged_in_client: TestClient, setup_module
):
    """
    Test that the endpoint returns 401 if the folder does not belong to the user
    """
    response = logged_in_client.put(
        "/workout-folders/3",
        json={"name": "Updated Folder", "exercises": []},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "You do not have access to this folder"}


def test_update_workout_folder_not_found(logged_in_client: TestClient):
    """
    Test that the endpoint returns 400 if the folder does not exist
    """
    response = logged_in_client.put(
        "/workout-folders/100",
        json={"name": "Updated Folder", "exercises": []},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Folder with requested id does not exist"}


def test_delete_workout_folder(
    logged_in_client: TestClient,
    workout_folder_data_access: WorkoutFolderDataAccess,
    setup_module,
):
    """
    Test that the endpoint deletes a workout folder
    """
    response = logged_in_client.delete("/workout-folders/1")
    assert response.status_code == 204

    # Check that the folder is deleted
    with pytest.raises(CosmosResourceNotFoundError):
        workout_folder_data_access.get_folder_by_id("1")


def test_delete_workout_folder_not_found(logged_in_client: TestClient):
    """
    Test that the endpoint returns 400 if the folder does not exist
    """
    response = logged_in_client.delete("/workout-folders/100")
    assert response.status_code == 400
    assert response.json() == {"detail": "Folder with requested id does not exist"}


def test_delete_workout_folder_not_authorized(logged_in_client: TestClient):
    """
    Test that the endpoint returns 401 if the folder does not belong to the user
    """
    response = logged_in_client.delete("/workout-folders/3")
    assert response.status_code == 401
    assert response.json() == {"detail": "You do not have access to this folder"}
