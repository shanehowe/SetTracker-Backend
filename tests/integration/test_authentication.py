import uuid

import pytest
from fastapi.testclient import TestClient

from app.auth.passwords import get_password_hash
from app.data_access.user import UserDataAccess
from app.models.user_models import UserInDB
from tests.integration.helpers import client

CLEAN_UP_IDS = []


def teardown_module():
    user_data_access = UserDataAccess()
    for user_id in CLEAN_UP_IDS:
        user_data_access.delete_user(user_id)


@pytest.fixture
def user_data_access():
    return UserDataAccess()


@pytest.fixture
def created_user(user_data_access: UserDataAccess):
    user = UserInDB(
        id=str(uuid.uuid4()),
        email="someone@email.com",
        password_hash=get_password_hash("valid_password"),
    )
    created = user_data_access.create_user(user)
    CLEAN_UP_IDS.append(created.id)
    return created


def test_sign_up_with_invalid_credentials(client: TestClient):
    response = client.post(
        "/auth/signup",
        json={"email": "bad_email", "password": "1"},
    )
    assert response.status_code == 422
    json_response = response.json()
    assert json_response["detail"][0].startswith("email")
    assert json_response["detail"][1].startswith("password")


def test_sign_up_with_valid_credentials(
    client: TestClient, user_data_access: UserDataAccess
):
    response = client.post(
        "/auth/signup",
        json={"email": "valid@email.com", "password": "valid_password"},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"]
    assert json_response["preferences"]
    assert json_response["token"]
    CLEAN_UP_IDS.append(json_response["id"])

    # User was actually created
    user = user_data_access.get_user_by_id(json_response["id"])
    assert user.id == json_response["id"]
    assert user.password_hash != "valid_password"


def test_sign_in_with_invalid_credentials(client):
    response = client.post(
        "/auth/signin",
        json={"email": "bad_email", "password": "1"},
    )
    assert response.status_code == 422
    json_response = response.json()
    assert json_response["detail"][0].startswith("email")
    assert json_response["detail"][1].startswith("password")


def test_sign_in_with_valid_credentials(client: TestClient, created_user: UserInDB):
    response = client.post(
        "/auth/signin", json={"email": created_user.email, "password": "valid_password"}
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"] == created_user.id
    assert json_response["preferences"]
    assert json_response["token"]


def test_sign_in_with_invalid_password(client: TestClient, created_user: UserInDB):
    response = client.post(
        "/auth/signin",
        json={"email": created_user.email, "password": "invalid_password"},
    )
    assert response.status_code == 401
    json_response = response.json()
    assert json_response["detail"] == "Invalid email or password"


def test_sign_in_with_invalid_email(client: TestClient):
    response = client.post(
        "/auth/signin",
        json={"email": "thisdoesntexist@email.com", "password": "valid_password"},
    )
    assert response.status_code == 401
    json_response = response.json()
    assert json_response["detail"] == "Invalid email or password"
