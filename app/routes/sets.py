from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.set_models import SetInCreate
from app.service.set_service import SetService, get_set_service

set_router = APIRouter(prefix="/sets", tags=["sets"])


@set_router.get("/{exercise_id}")
def get_users_sets_by_exercise_id(
    exercise_id: str,
    set_service: Annotated[SetService, Depends(get_set_service)],
    current_user: dict[str, str] = Depends(get_current_user),
):
    return set_service.get_users_sets_by_exercise_id(exercise_id, current_user["id"])


@set_router.post("/")
def create_set(
    set_to_create: SetInCreate,
    set_service: Annotated[SetService, Depends(get_set_service)],
    current_user: dict[str, str] = Depends(get_current_user),
):
    pass
