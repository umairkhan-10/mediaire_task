import pytest
from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer


@pytest.fixture(scope="session")
def mongodb_container():
    with MongoDbContainer("mongo:latest") as mongo:
        mongo_client = MongoClient(mongo.get_connection_url())
        yield mongo_client
        mongo_client.close()


@pytest.fixture(scope="function")
def mongodb(mongodb_client):
    db = mongodb_client["test_neuroData"]
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
    return db

# Should write more test cases as well
