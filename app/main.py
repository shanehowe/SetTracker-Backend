from fastapi import FastAPI

from app.routes.authentication import auth_router
from app.routes.exercises import exercises_router
from app.routes.workout_folders import workout_folder_router
from app.routes.sets import set_router

fast_app = FastAPI()
fast_app.include_router(auth_router)
fast_app.include_router(workout_folder_router)
fast_app.include_router(exercises_router)
fast_app.include_router(set_router)
