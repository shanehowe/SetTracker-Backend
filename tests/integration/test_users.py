from fastapi.testclient import TestClient

from app.data_access.user import UserDataAccess


def test_update_preferences_with_bad_key(logged_in_client: TestClient):
    """
    Test that updating preferences with a bad key returns a 422 response.
    Pydantic will validate the request body and FastAPI will return a 422 response if the request body is invalid.
    """
    response = logged_in_client.put("/me/preferences", json={"bad_key": "dark"})
    assert response.status_code == 422
    assert response.json() == {"detail": ["theme: required"]}


def test_update_preferences_with_bad_value(logged_in_client: TestClient):
    """
    Test that updating preferences with a bad value returns a 422 response.
    Pydantic will validate the request body and FastAPI will return a 422 response if the request body is invalid.
    """
    response = logged_in_client.put("/me/preferences", json={"theme": "banana"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": ["theme: should be 'system', 'dark' or 'light'"]
    }


def test_update_preferences(
    logged_in_client: TestClient, user_data_access: UserDataAccess
):
    """
    Test that updating preferences with a valid token and request body returns a 204 response.
    Validate that the user's preferences have been updated in the database.
    """
    response = logged_in_client.put("/me/preferences", json={"theme": "dark"})
    assert response.status_code == 204
    user = user_data_access.get_user_by_email("test@test.com")
    assert user.preferences.theme == "dark"


def test_update_preferences_with_deleted_user_but_valid_token(
    logged_in_client: TestClient, user_data_access: UserDataAccess
):
    """
    Test that updating preferences with a valid token and request body returns a 404 response.
    This is an unlikely scenario but nonetheless should be handled.
    """
    user = user_data_access.get_user_by_email("test@test.com")
    user_data_access.delete_user(user.id)
    response = logged_in_client.put("/me/preferences", json={"theme": "dark"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
