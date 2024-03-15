from azure.cosmos import CosmosClient


class CosmosDBClientSingleton:
    _instance = None
    client = None

    def __new__(cls, db_host, db_key):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = CosmosClient(db_host, db_key)
        return cls._instance
