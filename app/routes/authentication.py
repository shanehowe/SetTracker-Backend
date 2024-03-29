from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status

from app.service.user_service import UserService, get_user_service
from app.models.auth_models import AuthRequest
from app.models.user_models import UserInResponse
from app.exceptions import AuthenticationException


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/signin", status_code=status.HTTP_200_OK, response_model=UserInResponse
)
def sign_in(
    auth_data: AuthRequest, user_service: UserService = Depends(get_user_service)
) -> UserInResponse:
    try:
        authenticated_user = user_service.authenticate(auth_data)
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        return UserInResponse(**authenticated_user)
