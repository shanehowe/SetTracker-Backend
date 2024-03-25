from fastapi import FastAPI
from app.routes.authentication import auth_router


fast_app = FastAPI()
fast_app.include_router(auth_router)
