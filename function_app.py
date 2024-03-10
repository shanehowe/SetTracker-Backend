import azure.functions as func

app = func.FunctionApp()

@app.route(route="auth/signin", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def sign_in(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()

    try:
        provider = body["provider"]
    except KeyError:
        return func.HttpResponse(
            "Please provide a provider",
            status_code=400
        )
    
    match provider:
        case "apple":
            return func.HttpResponse(
                "Apple Sign In",
                status_code=200
            )
        case _:
            return func.HttpResponse(
                "Unsupported provider",
                status_code=400
            )