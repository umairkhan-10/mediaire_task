import pytest
from testcontainers.mongodb import MongoDbContainer

from common.db_manager import DBManager


@pytest.fixture(scope="session")
def mongodb_container():
    with MongoDbContainer("mongo:latest") as mongo:
        yield mongo


@pytest.fixture(scope="function")
def db_manager(mongodb_container):
    test_uri = mongodb_container.get_connection_url()
    return DBManager(mongo_uri=test_uri)


@pytest.fixture(scope="function")
def mongodb(mongodb_container):
    db = mongodb_container.get_connection_client()["test_neuroData"]
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
    return db

# Should write more test cases as well
