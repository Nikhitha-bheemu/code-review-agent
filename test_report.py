import unittest
import os
from report import generate_report

class TestReport(unittest.TestCase):
    def setUp(self):
        # Remove any existing pdf file before each test
        if os.path.exists("code_review_report.pdf"):
            os.remove("code_review_report.pdf")

    def tearDown(self):
        # Clean up after tests
        if os.path.exists("code_review_report.pdf"):
            os.remove("code_review_report.pdf")

    def test_generate_report_high_severity(self):
        code = "def divide(x, y):\n    return x / y"
        bugs = [
            {
                "line_number": 2,
                "bug_type": "Division by Zero",
                "severity": "high",
                "description": "Division by y without checking if y is 0"
            }
        ]
        fixes = [
            "def divide(x, y):\n    return x / y if y != 0 else 0"
        ]
        
        md_report = generate_report(code, bugs, fixes)
        
        # Verify markdown contents
        self.assertIn("# Code Review Report", md_report)
        self.assertIn("## Generated:", md_report)
        self.assertIn("- Total bugs found: 1", md_report)
        self.assertIn("- Total fixes generated: 1", md_report)
        self.assertIn("Line | Type | Severity | Description", md_report)
        self.assertIn("### Bug 1: Division by y without checking if y is 0", md_report)
        self.assertIn("## Recommendation: 🔴 CRITICAL - Immediate fix required", md_report)
        
        # Verify PDF file creation
        self.assertTrue(os.path.exists("code_review_report.pdf"))

    def test_generate_report_medium_severity(self):
        code = "def save():\n    f = open('test.txt', 'w')"
        bugs = [
            {
                "line_number": 2,
                "bug_type": "Resource Leak",
                "severity": "medium",
                "description": "File descriptor not closed properly"
            }
        ]
        fixes = [
            "def save():\n    with open('test.txt', 'w') as f:\n        pass"
        ]
        
        md_report = generate_report(code, bugs, fixes)
        self.assertIn("## Recommendation: 🟡 NEEDS FIX", md_report)
        self.assertTrue(os.path.exists("code_review_report.pdf"))

    def test_generate_report_low_severity(self):
        code = "def hello():\n    print('hi')"
        bugs = [
            {
                "line_number": 1,
                "bug_type": "Style",
                "severity": "low",
                "description": "Missing docstring"
            }
        ]
        fixes = [
            "def hello():\n    '''Hello function'''\n    print('hi')"
        ]
        
        md_report = generate_report(code, bugs, fixes)
        self.assertIn("## Recommendation: 🟢 PASS", md_report)
        self.assertTrue(os.path.exists("code_review_report.pdf"))

if __name__ == "__main__":
    unittest.main()
