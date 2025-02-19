# DB connection can be separated out in a more centralized place.
# URI should be fetched from more secure place like env or some Secrets Manager
import os

from pymongo import MongoClient

from common.const import NeuroDataCollections
from common.logger import logger


class DBManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensures only one instance of DBManager is created."""
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls, *args, **kwargs)
            # URI should be secured in some env or AWS Secrets Manager
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            cls._instance.initialize_db(mongo_uri)
        return cls._instance

    # to initialize the database connection
    def initialize_db(self, mongo_uri):
        self.client = None
        self.db = None
        try:
            # as it's local, so not providing any authentication
            self.client = MongoClient(mongo_uri)
            self.db = self.client.get_database("neuroData")
            # Creating collections if it doesn't exist already
            if NeuroDataCollections.brain_scans not in self.db.list_collection_names():
                self.db.create_collection("brain_scans")

            if (
                    NeuroDataCollections.brain_reports
                    not in self.db.list_collection_names()
            ):
                self.db.create_collection("brain_reports")
        except Exception as e:
            # Handling exceptions and printing an error message if connection fails
            logger.error(f"Error in creating DB or collections {e}")
            if self.client is not None:
                self.client.close()
                logger.info("DB Connection closed.")

    def insert(self, collection_name: str, data: dict):
        """Insert document into DB."""
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting document into {collection_name}: {e}")
            return None

    def fetch_one(self, collection_name: str, query: dict):
        """Fetches a single document from DB."""
        try:
            collection = self.db[collection_name]
            return collection.find_one(query)
        except Exception as e:
            logger.error(f"Error fetching document from {collection_name}: {e}")
            return None

    def fetch_one_and_update(self, collection_name: str, query: dict, update: dict):
        """Fetches and updates a document"""
        try:
            collection = self.db[collection_name]
            return collection.find_one_and_update(query, update, return_document=True)
        except Exception as e:
            logger.error(
                f"Error in fetch_one_and_update of DB Manager {collection_name}: {e}"
            )
            return None

    def update(self, collection_name: str, query: dict, update_data: dict):
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, {"$set": update_data})
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating document in {collection_name}: {e}")
            return None
