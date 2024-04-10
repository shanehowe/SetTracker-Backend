from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from app.auth.tokens import decode_jwt


async def extract_token(request: Request) -> str:
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


async def get_current_user(token: str = Depends(extract_token)) -> dict:
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
