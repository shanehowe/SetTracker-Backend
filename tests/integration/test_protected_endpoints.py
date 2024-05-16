from datetime import datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.auth.tokens import SECRET
from tests.integration.helpers import client, logged_in_client, user_data_access

GET_ENDPOINTS = [
    "/workout-folders/",
    "/workout-folders/123",
    "/sets/123",
    "/exercises/",
]

POST_ENDPOINTS = [
    "/workout-folders/",
    "/sets/",
    "/exercises/",
]

PUT_ENDPOINTS = [
    "/workout-folders/123",
    "/me/preferences",
]

DELETE_ENDPOINTS = [
    "/workout-folders/123",
    "/sets/123",
]


@pytest.fixture
def expired_token():
    payload = {
        "exp": datetime.now() - timedelta(days=1),
        "id": "123",
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


@pytest.fixture
def invalid_token_payload():
    payload = {
        "id": "123",
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


@pytest.mark.parametrize(
    "endpoint",
    GET_ENDPOINTS,
)
def test_protected_get_endpoints_with_no_token(client: TestClient, endpoint: str):
    response = client.get(endpoint)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.parametrize(
    "endpoint",
    POST_ENDPOINTS,
)
def test_protected_post_endpoints_with_no_token(client: TestClient, endpoint: str):
    response = client.post(endpoint)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.parametrize(
    "endpoint",
    PUT_ENDPOINTS,
)
def test_protected_put_endpoints_with_no_token(client: TestClient, endpoint: str):
    response = client.put(endpoint)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.parametrize(
    "endpoint",
    DELETE_ENDPOINTS,
)
def test_protected_delete_endpoints_with_no_token(client: TestClient, endpoint: str):
    response = client.delete(endpoint)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.parametrize(
    "endpoint",
    GET_ENDPOINTS,
)
def test_protected_get_endpoints_with_bad_token(client: TestClient, endpoint: str):
    response = client.get(endpoint, headers={"Authorization": "Bad Token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid authorization scheme"}


@pytest.mark.parametrize(
    "endpoint",
    POST_ENDPOINTS,
)
def test_protected_post_endpoints_with_bad_token(client: TestClient, endpoint: str):
    response = client.post(endpoint, headers={"Authorization": "Bad Token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid authorization scheme"}


@pytest.mark.parametrize(
    "endpoint",
    PUT_ENDPOINTS,
)
def test_protected_put_endpoints_with_bad_token(client: TestClient, endpoint: str):
    response = client.put(endpoint, headers={"Authorization": "Bad Token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid authorization scheme"}


@pytest.mark.parametrize(
    "endpoint",
    DELETE_ENDPOINTS,
)
def test_protected_delete_endpoints_with_bad_token(client: TestClient, endpoint: str):
    response = client.delete(endpoint, headers={"Authorization": "Bad Token"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid authorization scheme"}


@pytest.mark.parametrize(
    "endpoint",
    GET_ENDPOINTS,
)
def test_protected_get_endpoints_with_expired_token(
    client: TestClient, endpoint: str, expired_token: str
):
    response = client.get(
        endpoint, headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}


@pytest.mark.parametrize(
    "endpoint",
    POST_ENDPOINTS,
)
def test_protected_post_endpoints_with_expired_token(
    client: TestClient, endpoint: str, expired_token: str
):
    response = client.post(
        endpoint, headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}


@pytest.mark.parametrize(
    "endpoint",
    PUT_ENDPOINTS,
)
def test_protected_put_endpoints_with_expired_token(
    client: TestClient, endpoint: str, expired_token: str
):
    response = client.put(
        endpoint, headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}


@pytest.mark.parametrize(
    "endpoint",
    DELETE_ENDPOINTS,
)
def test_protected_delete_endpoints_with_expired_token(
    client: TestClient, endpoint: str, expired_token: str
):
    response = client.delete(
        endpoint, headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}


@pytest.mark.parametrize(
    "endpoint",
    GET_ENDPOINTS,
)
def test_protected_get_endpoints_with_invalid_token_payload(
    client: TestClient, endpoint: str, invalid_token_payload: str
):
    response = client.get(
        endpoint, headers={"Authorization": f"Bearer {invalid_token_payload}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token payload"}


@pytest.mark.parametrize(
    "endpoint",
    POST_ENDPOINTS,
)
def test_protected_post_endpoints_with_invalid_token_payload(
    client: TestClient, endpoint: str, invalid_token_payload: str
):
    response = client.post(
        endpoint, headers={"Authorization": f"Bearer {invalid_token_payload}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token payload"}


@pytest.mark.parametrize(
    "endpoint",
    PUT_ENDPOINTS,
)
def test_protected_put_endpoints_with_invalid_token_payload(
    client: TestClient, endpoint: str, invalid_token_payload: str
):
    response = client.put(
        endpoint, headers={"Authorization": f"Bearer {invalid_token_payload}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token payload"}


@pytest.mark.parametrize(
    "endpoint",
    DELETE_ENDPOINTS,
)
def test_protected_delete_endpoints_with_invalid_token_payload(
    client: TestClient, endpoint: str, invalid_token_payload: str
):
    response = client.delete(
        endpoint, headers={"Authorization": f"Bearer {invalid_token_payload}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token payload"}
