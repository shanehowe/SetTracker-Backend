import os
import sys
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import PartitionKey

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------

try:
    DB_HOST = os.environ["DB_HOST"]
    DB_KEY = os.environ["DB_KEY"]
except KeyError:
    sys.exit("Cosmos DB credentials not set")

DATABASE_ID = "set-tracker-db"

try:
    client = cosmos_client.CosmosClient(DB_HOST, credential=DB_KEY)

    db = client.get_database_client(DATABASE_ID)

    containers_to_create = [
        "users",
        "exercise-sets",
        "exercises",
        "workout-folders",
    ]

    for container_id in containers_to_create:
        db.create_container(id=container_id, partition_key=PartitionKey(path="/id"))

    # Seed the database with a user
    user = {
        "email": "doestnotmatter@email.com",
        "provider": "apple",
        "id": "f4ed09fc-ee99-43e0-8b19-123424f988ac",
        "preferences": {"theme": "system"},
    }
    container_client = db.get_container_client("users")
    container_client.create_item(body=user)

    # Seed the database with some exercises, When I set it up I scrope exercises from the web
    # but this is more than enough to let you see the funcitonality of the app
    exercises = [
        {
            "name": "Bench Press",
            "body_parts": ["Chest", "Triceps", "Shoulders"],
            "creator": "system",
        },
        {
            "name": "Squat",
            "body_parts": ["Quads", "Glutes", "Hamstrings"],
            "creator": "system",
        },
        {
            "name": "Deadlift",
            "body_parts": ["Back", "Glutes", "Hamstrings"],
            "creator": "system",
        },
        {
            "name": "Overhead Press",
            "body_parts": ["Shoulders", "Triceps"],
            "creator": "system",
        },
        {
            "name": "Pull Up",
            "body_parts": ["Back", "Biceps"],
            "creator": "system",
        },
        {
            "name": "Dumbbell Curl",
            "body_parts": ["Biceps", "Forearms"],
            "creator": "system",
        },
        {
            "name": "Tricep Extension",
            "body_parts": ["Triceps"],
            "creator": "system",
        },
        {
            "name": "Leg Press",
            "body_parts": ["Quads", "Glutes", "Hamstrings"],
            "creator": "system",
        },
    ]
    container_client = db.get_container_client("exercises")
    for exercise in exercises:
        exercise["id"] = str(uuid.uuid4())
        container_client.create_item(body=exercise)
except exceptions.CosmosHttpResponseError as e:
    sys.exit(f"Setting up database failed\n{str(e.message)}")
