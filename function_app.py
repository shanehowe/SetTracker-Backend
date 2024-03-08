import azure.functions as func

app = func.FunctionApp()

@app.route(route="signin", auth_level=func.AuthLevel.ANONYMOUS)
def sign_in(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello, World! This is a sign in page")