import unittest
import os
import json
from unittest.mock import patch
from memory import save_fix, recall_similar_fix, STORAGE_FILE

class TestMemory(unittest.TestCase):
    def setUp(self):
        # Remove any existing storage file before each test
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)

    def tearDown(self):
        # Clean up after tests
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)

    def test_save_and_recall_exact(self):
        bug_desc = "division by zero error in calculate"
        fix_code = "return total / count if count != 0 else 0"
        
        save_fix(bug_desc, fix_code)
        
        # Check file content structure
        self.assertTrue(os.path.exists(STORAGE_FILE))
        with open(STORAGE_FILE, "r") as f:
            data = json.load(f)
            self.assertIn(bug_desc, data)
            self.assertEqual(data[bug_desc]["fix"], fix_code)
            self.assertIn("timestamp", data[bug_desc])

        # Recall exact match
        recalled = recall_similar_fix(bug_desc)
        self.assertEqual(recalled, fix_code)

    def test_recall_similar_matches(self):
        bug_desc = "division by zero error in calculate"
        fix_code = "return total / count if count != 0 else 0"
        save_fix(bug_desc, fix_code)

        # Test similar match with >= 2 matching words (e.g. "division" and "zero")
        recalled = recall_similar_fix("division zero problem")
        self.assertEqual(recalled, fix_code)

        # Test match with 1 word (e.g. only "division") -> should return None
        recalled_one = recall_similar_fix("division problem")
        self.assertIsNone(recalled_one)

    def test_recall_no_file(self):
        recalled = recall_similar_fix("some bug")
        self.assertIsNone(recalled)

    @patch('json.dump')
    def test_save_exception_handling(self, mock_dump):
        mock_dump.side_effect = Exception("Write error")
        # Should not raise exception
        save_fix("division by zero", "fix_code")

if __name__ == "__main__":
    unittest.main()
