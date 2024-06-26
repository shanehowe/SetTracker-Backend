from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_current_user
from app.exceptions import EntityNotFoundException, UnauthorizedAccessException
from app.models.set_models import SetInCreate
from app.service.set_service import SetService, get_set_service

set_router = APIRouter(prefix="/sets", tags=["sets"])


@set_router.get("/{exercise_id}", response_model_by_alias=True)
def get_users_sets_by_exercise_id(
    exercise_id: str,
    set_service: Annotated[SetService, Depends(get_set_service)],
    current_user: dict[str, str] = Depends(get_current_user),
):
    return set_service.get_users_sets_by_exercise_id(exercise_id, current_user["id"])


@set_router.post("/", status_code=status.HTTP_201_CREATED, response_model_by_alias=True)
def create_set(
    set_to_create: SetInCreate,
    set_service: Annotated[SetService, Depends(get_set_service)],
    current_user: dict[str, str] = Depends(get_current_user),
):
    try:
        return set_service.create_set(set_to_create, current_user["id"])
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@set_router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(
    set_id: str,
    set_service: Annotated[SetService, Depends(get_set_service)],
    current_user: dict[str, str] = Depends(get_current_user),
):
    try:
        set_service.delete_set(set_id, current_user["id"])
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UnauthorizedAccessException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
