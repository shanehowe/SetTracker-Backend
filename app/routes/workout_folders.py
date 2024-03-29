from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from app.service.workout_folder_service import (
    get_workout_folder_service,
    WorkoutFolderService,
)
from app.dependencies import get_current_user


workout_folder_router = APIRouter(prefix="/workout-folders", tags=["workout folders"])


@workout_folder_router.get("/")
def get_users_folders(
    workout_folder_service: Annotated[
        WorkoutFolderService, Depends(get_workout_folder_service)
    ],
    decoded_token: dict = Depends(get_current_user),
):
    user_id = decoded_token.get("id")
    if user_id is None:
        raise HTTPException(
            detail="Invalid token payload", status_code=status.HTTP_400_BAD_REQUEST
        )
    return workout_folder_service.get_users_workout_folders(user_id)
