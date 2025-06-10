import unittest
from unittest.mock import MagicMock, patch
from .database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor

    def test_execute_query_fetch_true(self):
        self.mock_cursor.fetchall.return_value = [{'id': 1}]
        query = "SELECT * FROM test"
        result = self.db_manager.execute_query(self.mock_conn, query, fetch=True)
        self.mock_cursor.execute.assert_called_with(query, None)
        self.mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, [{'id': 1}])

    def test_execute_query_fetch_false(self):
        self.mock_cursor.rowcount = 5
        query = "UPDATE test SET x=1"
        result = self.db_manager.execute_query(self.mock_conn, query, fetch=False)
        self.mock_cursor.execute.assert_called_with(query, None)
        self.mock_conn.commit.assert_called_once()
        self.assertEqual(result, 5)

    def test_execute_query_exception(self):
        self.mock_cursor.execute.side_effect = Exception("DB error")
        query = "SELECT * FROM test"
        with self.assertRaises(Exception):
            self.db_manager.execute_query(self.mock_conn, query)
        self.mock_conn.rollback.assert_called_once()

if __name__ == "__main__":
    unittest.main()