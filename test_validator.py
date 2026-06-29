import unittest
from validator import validate_fix

class TestValidator(unittest.TestCase):
    def test_invalid_syntax(self):
        original = "def foo():\n    return 42"
        fix = "def foo(:\n    return 42"
        result = validate_fix(original, fix)
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["score"], 0.0)
        self.assertIn("--- original", result["diff"])
        self.assertIn("+++ fix", result["diff"])
        self.assertEqual(result["lines_changed"], 0)

    def test_valid_syntax_more_lines(self):
        original = "def foo():\n    return 42"
        fix = "def foo():\n    x = 1\n    return 42"
        result = validate_fix(original, fix)
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["score"], 0.5)
        self.assertEqual(result["lines_changed"], 1)

    def test_valid_syntax_fewer_or_equal_lines(self):
        original = "def foo():\n    x = 1\n    return 42"
        fix = "def foo():\n    x = 2\n    return 42" # Same chars count, same lines count
        result = validate_fix(original, fix)
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["score"], 0.8)
        self.assertEqual(result["lines_changed"], 0)

    def test_valid_syntax_fewer_lines_shorter_chars(self):
        original = "def foo():\n    x = 1\n    return 42"
        fix = "def foo():\n    return 42" # fewer lines (2 vs 3), shorter chars (30 vs 40)
        result = validate_fix(original, fix)
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["lines_changed"], 1)

    def test_error_handling(self):
        # Passing None to trigger exception in splitlines()
        result = validate_fix(None, None)
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["lines_changed"], 0)
        self.assertEqual(result["diff"], "")

if __name__ == "__main__":
    unittest.main()
