from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.exceptions import AuthenticationException, EntityAlreadyExistsException
from app.models.auth_models import AuthRequest
from app.models.user_models import UserEmailAuthInSignUpAndIn, UserInResponse
from app.service.user_service import UserService, get_user_service

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/signin/oauth", status_code=status.HTTP_200_OK, response_model=UserInResponse
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
def sign_in(
    user_for_sign_in: UserEmailAuthInSignUpAndIn,
    user_service: UserService = Depends(get_user_service),
):
    try:
        return user_service.authenticate_email_password_auth(user_for_sign_in)
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@auth_router.post("/signup")
def sign_up(
    user_for_sign_up: UserEmailAuthInSignUpAndIn,
    user_service: UserService = Depends(get_user_service),
):
    try:
        return user_service.sign_up_user(user_for_sign_up)
    except EntityAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
