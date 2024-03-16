from azure.cosmos import CosmosClient
import os


DB_HOST = os.environ["DB_HOST"]
DB_KEY = os.environ["DB_KEY"]


class CosmosDBClientSingleton:
    _instance = None
    client: CosmosClient

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = CosmosClient(url=DB_HOST, credential=DB_KEY)
        return cls._instance
