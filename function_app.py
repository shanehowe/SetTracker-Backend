import azure.functions as func
import json
from pydantic import ValidationError

from app.service.user_service import UserService
from app.models.auth_models import AuthRequest

app = func.FunctionApp()

@app.route(route="auth/signin", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def sign_in(req: func.HttpRequest) -> func.HttpResponse:
    user_service = UserService()
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            body="Invalid request. Please provide json",
            status_code=400
        )

    try:
        auth_data = AuthRequest(**body)
    except ValidationError:
        return func.HttpResponse(
            body="Invalid request data. Please provide identity_token and oAuth provider"
        )
    
    authenticated_user = user_service.authenticate(auth_data)
    if authenticated_user is None:
        return func.HttpResponse(body="Failed to authenticate user.")
    
    return func.HttpResponse(
        body=json.dumps({"token": authenticated_user})
    )

