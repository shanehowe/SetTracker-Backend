from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request, status
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from app.dependencies import extract_token, get_current_user


@pytest.fixture
def mock_request():
    def _mock_request(headers=None):
        request = MagicMock(spec=Request)
        request.headers = headers or {}
        return request

    return _mock_request


def test_extract_token_raises_401_exception_when_no_auth_header(mock_request):
    with pytest.raises(
        HTTPException, match="Could not validate credentials"
    ) as exc_info:
        extract_token(mock_request())
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(("scheme"), ("", "bearer", "Basic", "APIKey", "Token"))
def test_extract_token_raises_400_exception_when_wrong_auth_scheme(
    scheme, mock_request
):
    request = mock_request(headers={"Authorization": f"{scheme} token"})
    with pytest.raises(HTTPException) as exc_info:
        extract_token(request)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_extract_token_returns_token_when_valid_auth_scheme(mock_request):
    request = mock_request(headers={"Authorization": "Bearer token"})
    token = extract_token(request)
    assert token == "token"


def test_get_current_user_raises_401_exception_when_token_expired():
    with patch("jwt.decode") as mock_decode_jwt:
        mock_decode_jwt.side_effect = ExpiredSignatureError()
        with pytest.raises(HTTPException, match="Token expired") as exc_info:
            get_current_user(token="token")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_raises_400_exception_when_token_invalid():
    with patch("jwt.decode") as mock_decode_jwt:
        mock_decode_jwt.side_effect = PyJWTError()
        with pytest.raises(HTTPException, match="Could not decode token") as exc_info:
            get_current_user(token="token")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("payload", ({}, {"id": 1}, {"email": ""}))
def test_get_current_user_raises_400_exception_when_invalid_payload(payload):
    with patch("jwt.decode") as mock_decode_jwt:
        mock_decode_jwt.return_value = payload
        with pytest.raises(HTTPException, match="Invalid token payload") as exc_info:
            get_current_user(token="token")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_get_current_user_returns_payload_when_valid_token():
    payload = {"id": 1, "email": "some_email@notanemail.com"}
    with patch("jwt.decode") as mock_decode_jwt:
        mock_decode_jwt.return_value = payload
        user = get_current_user(token="token")
        assert user == payload
