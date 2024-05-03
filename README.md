# SetTracker Backend

## Introduction
This repository contains the backend service for the SetTracker application, an Azure Function app wrapping a FastAPI API. It is designed to handle all server-side logic, authentication, and data persistence for the strength training tracking app.

## Technologies Used
- **Azure Functions**: Serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure.
- **FastAPI**: Modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.
- **CosmosDB**: Azure's fully managed NoSQL database for modern app development.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Pytest**: Framework makes it easy to write small tests, yet scales to support complex functional testing.
- **JWT (JSON Web Tokens)**: Method for securely transmitting information between parties as a JSON object, used here for authentication.
- **Apple Auth**: Authentication method supported, enabling secure login from the frontend app without traditional passwords.

## Architecture
- **Routers**: Define the endpoints and handle the routing of API requests.
- **Service Layer**: Contains the business logic of the application.
- **Data Access Layer**: Manages the interaction with the database, in this case, CosmosDB, for CRUD operations.
- **Models**: Uses Pydantic for data validation and schema definition.

## Getting Started

**Prerequisites**
- Python 3.11+
- Azure account with an active subscription
- Azure CLI installed and configured

## Azure Cosmos DB
An account needs to be set up. Heres what you need to do.
- In Azure portal navigate to CosmosDB and select **create**
- On the next screen choose **Azure Cosmos DB for NoSQL**
- Complete the following forms
- Name the database **set-tracker-db**
- We will create the containers in the next step

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/shanehowe/SetTracker-Backend.git
   cd SetTracker-backend
2. **(Optional) Create a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
3. **Install the requirements**
```bash
pip install -r requirements.txt
```
4. **Create the containers in CosmosDB** Navigate to the file ```setup_cosmos_db.py``` and run the script. This will create the containers needed for the application. Make sure you have the environment variables set up.
```bash
python3 setup_cosmos_db.py
```
5. **Create a script to run the backend**
- Call a file call it ```start.sh``` in roote of project
```bash
export DB_HOST="The URI of your CosmosDB" # Can be found in 'Keys'
export DB_KEY="You Master Key"
export JWT_SECRET="GenerateRandomSecret"

# Start the function app
func start
```
6. **Run the script you just created**
```bash
chmod u+x start.sh
./start.sh
```

## Making Requests
To make requests you will need to send a token in the header with your requests and said token needs to be linked to a user. Heres what you need to do.

- In your code editor, open a python interactive shell and run the following. This will generate a token for you to use. The user has been created if you have ran ```setup_cosmos_db.py```.

```python
import jwt 

payload = {"email" : "doesnotmatter@email.com", "id": "f4ed09fc-ee99-43e0-8b19-123424f988ac"}

jwt.encode(payload, "GenerateRandomSecret", algorithm="HS256")
```
Now you have your bearer token to make requests to the backend.

- In your web browser navigate to ```http://localhost:7071/docs```. Here you will find the routes and HTTP methods for making requests.

## Cleaning Up
Once finished make sure to go to your Azure portal and remove the resources you created to avoid any charges.
