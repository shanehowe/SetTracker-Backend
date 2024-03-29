from fastapi import FastAPI
from app.routes.authentication import auth_router
from app.routes.workout_folders import workout_folder_router


fast_app = FastAPI()
fast_app.include_router(auth_router)
fast_app.include_router(workout_folder_router)
