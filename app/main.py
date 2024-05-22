from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.authentication import auth_router
from app.routes.exercises import exercises_router
from app.routes.sets import set_router
from app.routes.users import user_router
from app.routes.workout_folders import workout_folder_router

fast_app = FastAPI()
fast_app.include_router(auth_router)
fast_app.include_router(workout_folder_router)
fast_app.include_router(exercises_router)
fast_app.include_router(set_router)
fast_app.include_router(user_router)


@fast_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    parsed_errors = []
    for error in exc.errors():
        if "msg" not in error or "loc" not in error:
            continue
        elif len(error["loc"]) < 2:
            continue
        location = error["loc"][1]
        # Remove the first word from the message. It will be replaced with the location.
        msg = " ".join(error["msg"].split()[1:]).replace(": ", " ")
        friendly_message = f"{location}: {msg}"
        parsed_errors.append(friendly_message)
    if not parsed_errors:
        parsed_errors = exc.errors()
    return JSONResponse(status_code=422, content={"detail": parsed_errors})
