import multiprocessing
import os
from typing import Dict, Optional, List

from pymongo import MongoClient

from common.config import MONGO_DB_URI
from common.logger import logger


class DBManager:
    _instance = None
    lock = multiprocessing.Lock()

    def __new__(cls, mongo_uri: Optional[str] = None, *args, **kwargs):
        """Ensures only one instance of DBManager is created."""
        with cls.lock:
            if cls._instance is None:
                cls._instance = super(DBManager, cls).__new__(cls, *args, **kwargs)
                # URI should be secured in some env or AWS Secrets Manager
                if not mongo_uri:
                    mongo_uri = os.getenv("MONGO_URI", MONGO_DB_URI)
                cls._instance.initialize_db(mongo_uri)
        return cls._instance

    # to initialize the database connection
    def initialize_db(self, mongo_uri) -> None:
        self.client = None
        self.db = None
        try:
            # as it's local, so not providing any authentication
            self.client = MongoClient(mongo_uri)
            self.db = self.client.get_database("neuroData")
        except Exception as e:
            # Handling exceptions and printing an error message if connection fails
            logger.error(f"Error in creating DB or collections {e}")
            if self.client is not None:
                self.client.close()
                logger.info("DB Connection closed.")

    def insert(self, collection_name: str, data: Dict) -> Optional[str]:
        """Insert document into DB."""
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting document into {collection_name}: {e}")
            return None

    def fetch_one(self, collection_name: str, query: Dict) -> Optional[Dict]:
        """Fetches a single document from DB."""
        try:
            collection = self.db[collection_name]
            return collection.find_one(query)
        except Exception as e:
            logger.error(f"Error fetching document from {collection_name}: {e}")
            return None

    def fetch_one_and_update(self, collection_name: str, query: Dict, update: Dict) -> Optional[Dict]:
        """Fetches and updates a document"""
        try:
            collection = self.db[collection_name]
            return collection.find_one_and_update(query, {"$set": update}, return_document=True)
        except Exception as e:
            logger.error(
                f"Error in fetch_one_and_update of DB Manager {collection_name}: {e}"
            )
            return None

    def fetch_all(self, collection_name: str, query: Dict) -> Optional[List]:
        """Fetches all documents based of query"""
        try:
            collection = self.db[collection_name]
            return list(collection.find(query))
        except Exception as e:
            logger.error(
                f"Error in fetch_all of DB Manager {collection_name}: {e}"
            )
            return None

    def update(self, collection_name: str, query: Dict, update_data: Dict) -> Optional[int]:
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, {"$set": update_data})
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating document in {collection_name}: {e}")
            return None
