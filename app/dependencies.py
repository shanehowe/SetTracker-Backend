from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from app.auth.tokens import decode_jwt


def extract_token(request: Request) -> str:
    """
    Extracts the token from the request headers.

    Args:
        request (Request): The incoming request object.

    Returns:
        str: The extracted token.

    Raises:
        HTTPException: If the token is missing or has an invalid authorization scheme.
    """
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization scheme",
        )
    return token[7:]  # Strip away "Bearer "


def get_current_user(token: str = Depends(extract_token)) -> dict:
    """
    Retrieves the current user based on the provided token.

    Args:
        token (str): The JWT token used for authentication.

    Returns:
        dict: The payload of the decoded JWT token, representing the current user.

    Raises:
        HTTPException: If the token has expired or could not be decoded, or if the token payload is invalid.
    """
    try:
        payload = decode_jwt(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Could not decode token"
        )
    if payload.get("id") is None or payload.get("email") is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload"
        )
    return payload
