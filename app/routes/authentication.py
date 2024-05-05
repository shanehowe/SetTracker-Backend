from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.exceptions import AuthenticationException, EntityAlreadyExistsException
from app.models.auth_models import AuthRequest
from app.models.user_models import UserInResponse, UserEmailAuthInSignUp
from app.service.user_service import UserService, get_user_service

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/signin/oAuth", status_code=status.HTTP_200_OK, response_model=UserInResponse
)
def sign_in_oAuth(
    auth_data: AuthRequest, user_service: UserService = Depends(get_user_service)
) -> UserInResponse:
    try:
        authenticated_user = user_service.authenticate_oauth(auth_data)
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        return authenticated_user


@auth_router.post(
    "/signin", status_code=status.HTTP_200_OK, response_model=UserInResponse
)
def sign_in(user_service: UserService = Depends(get_user_service)):
    return {"detail": "Working"}


@auth_router.post("/signup")
def sign_up(
    user_for_sign_up: UserEmailAuthInSignUp,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return user_service.sign_up_user(user_for_sign_up)
    except EntityAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
