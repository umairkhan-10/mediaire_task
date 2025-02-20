import unittest
from unittest.mock import patch

from pymongo.errors import PyMongoError

from common.db_manager import DBManager


class TestDBManager(unittest.TestCase):
    def test_singleton_instance(self):
        """Test that only one instance of DBManager is created."""
        db_manager_1 = DBManager()
        db_manager_2 = DBManager()
        self.assertIs(db_manager_1, db_manager_2)

    def test_insert_success(self):
        """Test id cocument is successfully inserted."""
        with patch("pymongo.collection.Collection.insert_one") as mock_insert:
            mock_insert.return_value.inserted_id = "12345"
            db_manager = DBManager()
            inserted_id = db_manager.insert("test_coll", {"key": "value"})
            self.assertEqual(inserted_id, "12345")
            mock_insert.assert_called_once_with({"key": "value"})

    def test_insert_failure(self):
        """Test insert method handles exceptions."""
        with patch("pymongo.collection.Collection.insert_one", side_effect=PyMongoError("Insertion Error")):
            db_manager = DBManager()
            inserted_id = db_manager.insert("test_coll", {"key": "value"})
            self.assertIsNone(inserted_id)

    # TODO:
    def test_fetch_one_failure(self):
        pass

    def test_fetch_one_and_update_success(self):
        pass

    def test_fetch_one_and_update_failure(self):
        pass

    def test_fetch_all_success(self):
        pass

    def test_update_success(self):
        pass


if __name__ == '__main__':
    unittest.main()
