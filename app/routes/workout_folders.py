from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.exceptions import EntityNotFoundException, UnauthorizedAccessException
from app.models.workout_folder_models import (
    WorkoutFolderInRequest,
    WorkoutFolderInUpdate,
)
from app.service.workout_folder_service import (
    WorkoutFolderService,
    get_workout_folder_service,
)

workout_folder_router = APIRouter(prefix="/workout-folders", tags=["workout folders"])


@workout_folder_router.get("/")
def get_users_folders(
    workout_folder_service: Annotated[
        WorkoutFolderService, Depends(get_workout_folder_service)
    ],
    decoded_token: dict[str, str] = Depends(get_current_user),
):
    user_id = decoded_token["id"]
    return workout_folder_service.get_users_workout_folders(user_id)


@workout_folder_router.get("/{folder_id}")
def get_folder_by_id(
    folder_id: str,
    workout_folder_service: Annotated[
        WorkoutFolderService, Depends(get_workout_folder_service)
    ],
    decoded_token: dict = Depends(get_current_user),
):
    try:
        folder = workout_folder_service.get_folder_by_id(
            folder_id, decoded_token.get("id", "")
        )
    except UnauthorizedAccessException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_401_UNAUTHORIZED)
    if folder is None:
        raise HTTPException(
            detail="Folder with requested id does not exist",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return folder


@workout_folder_router.post("/", status_code=status.HTTP_201_CREATED)
def create_workout_folder(
    folder_to_create: WorkoutFolderInRequest,
    workout_folder_service: Annotated[
        WorkoutFolderService, Depends(get_workout_folder_service)
    ],
    decoded_token: dict[str, str] = Depends(get_current_user),
):
    return workout_folder_service.create_workout_folder(
        folder_to_create, decoded_token["id"]
    )


@workout_folder_router.put("/{folder_id}")
def update_workout_folder(
    folder_id: str,
    folder_to_update: WorkoutFolderInUpdate,
    workout_folder_service: Annotated[
        WorkoutFolderService, Depends(get_workout_folder_service)
    ],
    decoded_token: dict[str, str] = Depends(get_current_user),
):
    try:
        updated_folder = workout_folder_service.update_workout_folder(
            folder_id, folder_to_update, user_id=decoded_token["id"]
        )
    except ValueError as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except UnauthorizedAccessException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_401_UNAUTHORIZED)
    if updated_folder is None:
        raise HTTPException(
            detail="Folder with requested id does not exist",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return updated_folder


@workout_folder_router.delete("/{folder_id}", status_code=status.HTTP_200_OK)
def delete_workout_folder(
    folder_id: str,
    workout_folder_service: Annotated[
        WorkoutFolderService, Depends(get_workout_folder_service)
    ],
    decoded_token: dict[str, str] = Depends(get_current_user),
):
    try:
        is_success = workout_folder_service.delete_workout_folder(
            folder_id, decoded_token["id"]
        )
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UnauthorizedAccessException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return {"detail": is_success}
