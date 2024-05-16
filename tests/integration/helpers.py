import uuid
import pytest
from fastapi.testclient import TestClient

from app.auth.passwords import get_password_hash
from app.main import fast_app
from app.data_access.user import UserDataAccess
from app.models.user_models import UserInDB


@pytest.fixture
def client():
    yield TestClient(fast_app)


@pytest.fixture
def user_data_access():
    return UserDataAccess()


@pytest.fixture
def logged_in_client(client: TestClient, user_data_access: UserDataAccess):
    user = UserInDB(
        id=str(uuid.uuid4()),
        email="test@test.com",
        password_hash=get_password_hash("password"),
    )
    user_data_access.create_user(user)
    response = client.post(
        "/auth/signin",
        json={"email": user.email, "password": "password"},
    )
    assert response.status_code == 200
    token = response.json()["token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    yield client
    user_data_access.delete_user(user.id)