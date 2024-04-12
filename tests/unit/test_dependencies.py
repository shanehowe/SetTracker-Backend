from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request, status

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
