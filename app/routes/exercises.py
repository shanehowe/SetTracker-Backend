from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.exceptions import EntityAlreadyExistsException
from app.models.exercises_models import ExerciseInCreate
from app.service.exercise_service import ExerciseService, get_exercise_service

exercises_router = APIRouter(prefix="/exercises", tags=["exercises"])


@exercises_router.get("/")
def get_all_exercises(
    exercise_service: Annotated[ExerciseService, Depends(get_exercise_service)],
    decoded_token: dict = Depends(get_current_user),
):
    return exercise_service.get_system_and_user_exercises(decoded_token["id"])


@exercises_router.post("/", status_code=status.HTTP_201_CREATED)
def create_custom_exercise(
    exercise: ExerciseInCreate,
    exercise_service: Annotated[ExerciseService, Depends(get_exercise_service)],
    decoded_token: dict = Depends(get_current_user),
):
    try:
        return exercise_service.create_custom_exercise(exercise, decoded_token["id"])
    except EntityAlreadyExistsException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
