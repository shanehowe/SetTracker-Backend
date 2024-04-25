from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.exceptions import EntityNotFoundException
from app.models.user_models import Preferences
from app.service.user_service import UserService, get_user_service


user_router = APIRouter(prefix="/me", tags=["users"])


@user_router.put("/preferences", status_code=status.HTTP_204_NO_CONTENT)
def update_preferences(
    preferences: Preferences,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: dict[str, str] = Depends(get_current_user)
):
    try:
        user_service.update_user_preferences(preferences, current_user["id"])
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))