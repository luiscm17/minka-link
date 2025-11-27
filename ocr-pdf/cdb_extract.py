import os
from azure.cosmos import CosmosClient
import uuid
from dotenv import load_dotenv

load_dotenv()
endpoint = os.getenv("cdb_endpoint")
key = os.getenv("cdb_key")


DATABASE_NAME = "pdfdb"
CONTAINER_NAME = "pdfdata"

def save_to_cosmos(data):
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    data["id"] = str(uuid.uuid4())
    container.create_item(body=data)
    return data["id"]