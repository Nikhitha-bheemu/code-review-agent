import unittest
from unittest.mock import MagicMock, patch
from detector import detect_bugs

class TestDetector(unittest.TestCase):
    @patch('anthropic.Anthropic')
    def test_detect_bugs_success_list(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='[{"line_number": 2, "bug_type": "ZeroDivision", "description": "Dividing by zero", "severity": "high"}]')]
        mock_client.messages.create.return_value = mock_response
        
        result = detect_bugs("def divide(x, y): return x / y", "dummy_key")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["bug_type"], "ZeroDivision")
        
        # Verify prompt and parameters
        mock_anthropic.assert_called_once_with(api_key="dummy_key")
        mock_client.messages.create.assert_called_once()
        kwargs = mock_client.messages.create.call_args[1]
        self.assertEqual(kwargs["model"], "claude-sonnet-4-6")
        self.assertEqual(kwargs["max_tokens"], 1024)
        self.assertIn("You are a strict Python bug detector.", kwargs["system"])

    @patch('anthropic.Anthropic')
    def test_detect_bugs_success_dict_bugs(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"bugs": [{"line_number": 3, "bug_type": "TypeError", "description": "Type mismatch", "severity": "medium"}]}')]
        mock_client.messages.create.return_value = mock_response
        
        result = detect_bugs("x = 'str' + 1", "dummy_key")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["bug_type"], "TypeError")

    @patch('anthropic.Anthropic')
    def test_detect_bugs_success_dict_issues(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"issues": [{"line_number": 4, "bug_type": "IndexError", "description": "Index out of range", "severity": "low"}]}')]
        mock_client.messages.create.return_value = mock_response
        
        result = detect_bugs("x = list[10]", "dummy_key")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["bug_type"], "IndexError")

    @patch('anthropic.Anthropic')
    def test_detect_bugs_regex_fallback(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        # Simulating text enclosing the json array
        malformed_text = 'Here is the bug array:\n[{"line_number": 5, "bug_type": "NameError", "description": "Undefined var", "severity": "high"}]\nHope this helps!'
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=malformed_text)]
        mock_client.messages.create.return_value = mock_response
        
        result = detect_bugs("print(undefined_var)", "dummy_key")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["bug_type"], "NameError")

    @patch('anthropic.Anthropic')
    def test_detect_bugs_markdown_strip(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='```json\n[{"line_number": 1, "bug_type": "ResourceWarning", "description": "Unclosed file", "severity": "medium"}]\n```')]
        mock_client.messages.create.return_value = mock_response
        
        result = detect_bugs("f = open('file')", "dummy_key")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["bug_type"], "ResourceWarning")

    @patch('anthropic.Anthropic')
    def test_detect_bugs_invalid_all_fail(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='no json array at all here')]
        mock_client.messages.create.return_value = mock_response
        
        result = detect_bugs("def dummy(): pass", "dummy_key")
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
