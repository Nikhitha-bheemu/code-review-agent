import unittest
from unittest.mock import MagicMock, patch
from ga_engine import score_fix, crossover, mutate, evolve_fix

class TestGAEngine(unittest.TestCase):
    def test_score_fix_invalid_syntax(self):
        # Invalid python code syntax should yield 0.0
        self.assertEqual(score_fix("def original(): pass", "def invalid(: pass"), 0.0)

    def test_score_fix_valid_base(self):
        # Valid code, same lines and characters -> score 1.0
        self.assertEqual(score_fix("def original(): pass", "def original(): pass"), 1.0)

    def test_score_fix_fewer_lines(self):
        # Valid code, fewer lines but longer in characters -> score 1.3
        original = "x=1\ny=2"
        fix = "x = 1 + 2 + 3 + 4"
        self.assertEqual(score_fix(original, fix), 1.3)

    def test_score_fix_shorter_chars(self):
        # Valid code, shorter characters but more lines -> score 1.2
        original = "x = 1234567890"
        fix = "x=1\ny"
        self.assertEqual(score_fix(original, fix), 1.2)

    def test_score_fix_max_limit(self):
        # Valid code, fewer lines and shorter characters -> score 1.5
        original = "x = 1\ny = 2\n"
        fix = "x = 1"  # fewer lines (1 vs 2) and shorter (5 chars vs 12 chars)
        self.assertEqual(score_fix(original, fix), 1.5)

    def test_crossover(self):
        fix1 = "line1_1\nline1_2\nline1_3\nline1_4"
        fix2 = "line2_1\nline2_2\nline2_3\nline2_4"
        # half1 = 2 lines, half2 = 2 lines
        result = crossover(fix1, fix2)
        expected = "line1_1\nline1_2\nline2_3\nline2_4"
        self.assertEqual(result, expected)

    @patch('anthropic.Anthropic')
    def test_mutate_success(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='```python\ndef fixed(): pass\n```')]
        mock_client.messages.create.return_value = mock_response
        
        result = mutate("def buggy(): pass", "dummy_key")
        self.assertEqual(result, "def fixed(): pass")
        
        # Verify call parameters
        mock_client.messages.create.assert_called_once()
        kwargs = mock_client.messages.create.call_args[1]
        self.assertEqual(kwargs["model"], "claude-sonnet-4-6")
        self.assertEqual(kwargs["max_tokens"], 1024)
        self.assertEqual(kwargs["system"], "You are a Python code optimizer.")

    @patch('anthropic.Anthropic')
    def test_mutate_failure_fallback(self, mock_anthropic):
        mock_anthropic.side_effect = Exception("API error")
        result = mutate("def buggy(): pass", "dummy_key")
        self.assertEqual(result, "def buggy(): pass")

    @patch('anthropic.Anthropic')
    def test_evolve_fix_success(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        # Mock responses for initial population (4 fixes)
        # And mutation calls (since generations=1, pop_size=4, elites=2, we need 2 mutation calls)
        mock_responses = []
        for i in range(4):
            res = MagicMock()
            res.content = [MagicMock(text=f"def fixed{i}(): pass")]
            mock_responses.append(res)
            
        # 2 mutation responses for the 2 children in generation 1
        for i in range(2):
            res = MagicMock()
            res.content = [MagicMock(text=f"def mutated{i}(): pass")]
            mock_responses.append(res)
            
        mock_client.messages.create.side_effect = mock_responses
        
        bug = {"description": "Fix division by zero"}
        original_code = "def calc(a, b): return a / b"
        
        result = evolve_fix(
            bug=bug,
            original_code=original_code,
            api_key="dummy_key",
            generations=1,
            population_size=4
        )
        
        # Result should be one of the syntactically valid candidates
        self.assertTrue(result.startswith("def "))
        # The prompt parameters for initial population should be verified
        first_call_kwargs = mock_client.messages.create.call_args_list[0][1]
        self.assertEqual(first_call_kwargs["system"], "You are a Python bug fixer. Return only fixed code.")
        self.assertEqual(first_call_kwargs["model"], "claude-sonnet-4-6")
        self.assertEqual(first_call_kwargs["max_tokens"], 1024)

    @patch('anthropic.Anthropic')
    def test_evolve_fix_failure_fallback(self, mock_anthropic):
        mock_anthropic.side_effect = Exception("API failure")
        bug = {"description": "Fix bug"}
        original_code = "def original(): pass"
        
        result = evolve_fix(
            bug=bug,
            original_code=original_code,
            api_key="dummy_key",
            generations=3,
            population_size=4
        )
        # Should fallback to original code
        self.assertEqual(result, original_code)

if __name__ == '__main__':
    unittest.main()
