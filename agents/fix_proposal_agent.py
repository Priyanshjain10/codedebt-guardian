"""
Fix Proposal Agent - Agent 3 of 3
Generates concrete, actionable code fixes for detected technical debt using Gemini 2.0.

For each debt item, produces:
- Explanation of the problem
- Concrete code fix (before/after)
- Step-by-step remediation guide
- Testing recommendations
- Estimated time to implement
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False

from tools.memory_bank import MemoryBank
from tools.observability import ObservabilityLayer

logger = logging.getLogger(__name__)

if _GENAI_AVAILABLE:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

FIX_SYSTEM_PROMPT = """You are a senior software engineer generating code fixes for technical debt.
For each issue, provide a clear, actionable fix that:
1. Is minimal and focused (don't over-engineer)
2. Follows Python best practices and PEP 8
3. Includes proper error handling
4. Has clear before/after examples

Respond ONLY with valid JSON with these exact fields:
- issue_type: the type of debt being fixed
- severity: CRITICAL/HIGH/MEDIUM/LOW
- problem_summary: 1 sentence explaining the issue
- fix_summary: 1 sentence explaining the fix
- before_code: problematic code snippet (if applicable)
- after_code: fixed code snippet
- steps: list of strings, step-by-step fix instructions
- testing_tip: how to verify the fix worked
- estimated_time: realistic time to implement
- references: list of relevant docs/PEP links"""


class FixProposalAgent:
    """
    Agent 3: Fix Proposal Generator

    Uses Gemini 2.0 with specialized context for each debt type.
    Generates production-ready code fixes with before/after examples.
    """

    def __init__(self, memory: Optional[MemoryBank] = None):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=FIX_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        ) if _GENAI_AVAILABLE else None
        self.memory = memory or MemoryBank()
        self.obs = ObservabilityLayer(service_name="fix_proposal_agent")

        # Pre-built fix templates for common issues (fast path, no API call needed)
        self._fix_templates = self._build_fix_templates()

    def propose(self, issues: List[Dict]) -> List[Dict[str, Any]]:
        """
        Generate fix proposals for a list of ranked issues.

        Args:
            issues: Top-priority issues from the ranking agent

        Returns:
            List of fix proposals with code examples and instructions
        """
        with self.obs.trace("propose") as span:
            span.set_attribute("input_issues", len(issues))
            proposals = []

            for issue in issues:
                proposal = self._generate_fix(issue)
                if proposal:
                    proposals.append(proposal)

            span.set_attribute("proposals_generated", len(proposals))
            logger.info(f"Generated {len(proposals)} fix proposals")
            return proposals

    def _generate_fix(self, issue: Dict) -> Optional[Dict]:
        """Generate a fix for a single issue. Uses template if available, else AI."""
        issue_type = issue.get("type", "")
        cache_key = f"fix_{issue_type}_{issue.get('location', '')}"

        # Check memory cache
        cached = self.memory.get(cache_key)
        if cached:
            return cached

        # Use template for common issues (faster + free)
        if issue_type in self._fix_templates:
            proposal = self._apply_template(issue, self._fix_templates[issue_type])
        else:
            # Fall back to Gemini AI for complex/custom issues
            proposal = self._ai_generate_fix(issue)

        if proposal:
            self.memory.set(cache_key, proposal, ttl_seconds=86400)  # Cache for 24h

        return proposal

    def _ai_generate_fix(self, issue: Dict) -> Optional[Dict]:
        """Use Gemini to generate a fix for a complex or custom issue."""
        prompt = f"""Generate a fix for this technical debt issue:

Type: {issue.get('type')}
Severity: {issue.get('severity')}
Description: {issue.get('description')}
Location: {issue.get('location')}
Impact: {issue.get('impact')}
Effort to Fix: {issue.get('effort_to_fix')}
Business Justification: {issue.get('business_justification', 'N/A')}

Provide a complete, production-ready fix."""

        if not self.model:
            return self._fallback_fix(issue)

        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            fix = json.loads(raw)
            fix["issue_id"] = issue.get("_rank_id")
            fix["source"] = "gemini_ai"
            fix["original_issue"] = {
                "type": issue.get("type"),
                "severity": issue.get("severity"),
                "location": issue.get("location"),
                "score": issue.get("score"),
                "priority": issue.get("priority"),
            }
            return fix

        except Exception as e:
            logger.warning(f"AI fix generation failed for {issue.get('type')}: {e}")
            return self._fallback_fix(issue)

    def _apply_template(self, issue: Dict, template: Dict) -> Dict:
        """Apply a pre-built fix template to an issue."""
        proposal = dict(template)
        proposal["issue_id"] = issue.get("_rank_id")
        proposal["source"] = "template"
        proposal["original_issue"] = {
            "type": issue.get("type"),
            "severity": issue.get("severity"),
            "location": issue.get("location"),
            "score": issue.get("score"),
            "priority": issue.get("priority"),
        }
        return proposal

    def _fallback_fix(self, issue: Dict) -> Dict:
        """Fallback fix when AI is unavailable."""
        return {
            "issue_id": issue.get("_rank_id"),
            "issue_type": issue.get("type"),
            "severity": issue.get("severity"),
            "problem_summary": issue.get("description", "Technical debt detected"),
            "fix_summary": "Manual review and refactoring required",
            "before_code": "# See issue location for problematic code",
            "after_code": "# Refactor following the steps below",
            "steps": [
                f"Navigate to {issue.get('location', 'the affected file')}",
                "Review the code in context",
                "Apply the fix based on the issue type",
                "Run tests to verify the fix",
            ],
            "testing_tip": "Run your test suite and verify no regressions",
            "estimated_time": issue.get("effort_to_fix", "HOURS"),
            "references": ["https://peps.python.org/pep-0008/"],
            "source": "fallback",
            "original_issue": {
                "type": issue.get("type"),
                "severity": issue.get("severity"),
                "location": issue.get("location"),
            },
        }

    def _build_fix_templates(self) -> Dict[str, Dict]:
        """Pre-built fix templates for the most common debt types."""
        return {
            "bare_except": {
                "issue_type": "bare_except",
                "severity": "MEDIUM",
                "problem_summary": "Bare `except:` clauses catch all exceptions including SystemExit, hiding bugs.",
                "fix_summary": "Specify the exact exception types you expect to catch.",
                "before_code": """try:
    result = risky_operation()
except:
    pass  # silently ignores everything""",
                "after_code": """try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except ConnectionError as e:
    logger.warning(f"Connection failed, retrying: {e}")
    return None""",
                "steps": [
                    "Identify what exceptions `risky_operation()` can raise",
                    "Replace bare `except:` with specific exception types",
                    "Add appropriate logging inside the except block",
                    "Decide: should the exception propagate or be handled?",
                    "Never use `pass` silently — always log or re-raise",
                ],
                "testing_tip": "Write a test that triggers the exception and verify the specific exception type is caught correctly",
                "estimated_time": "15-30 minutes",
                "references": ["https://docs.python.org/3/tutorial/errors.html", "https://peps.python.org/pep-0008/#programming-recommendations"],
            },
            "missing_docstring": {
                "issue_type": "missing_docstring",
                "severity": "LOW",
                "problem_summary": "Function lacks a docstring, reducing discoverability and maintainability.",
                "fix_summary": "Add a Google-style or NumPy-style docstring describing purpose, args, and return value.",
                "before_code": """def calculate_discount(price, percentage, max_discount):
    if percentage > 100:
        raise ValueError("Percentage cannot exceed 100")
    discount = price * (percentage / 100)
    return min(discount, max_discount)""",
                "after_code": """def calculate_discount(price: float, percentage: float, max_discount: float) -> float:
    \"\"\"Calculate a capped discount amount for a given price.

    Args:
        price: Original price in the base currency.
        percentage: Discount percentage (0-100).
        max_discount: Maximum discount cap.

    Returns:
        The calculated discount, capped at max_discount.

    Raises:
        ValueError: If percentage exceeds 100.

    Example:
        >>> calculate_discount(100.0, 20.0, 15.0)
        15.0
    \"\"\"
    if percentage > 100:
        raise ValueError("Percentage cannot exceed 100")
    discount = price * (percentage / 100)
    return min(discount, max_discount)""",
                "steps": [
                    "Add a one-line summary as the first line of the docstring",
                    "Document all parameters with their types",
                    "Document the return type and value",
                    "Document any exceptions that can be raised",
                    "Add a usage example if the function is complex",
                    "Consider using a tool like `interrogate` to enforce docstring coverage",
                ],
                "testing_tip": "Run `python -m pydoc your_module.function_name` to verify docstring renders correctly",
                "estimated_time": "5-15 minutes per function",
                "references": ["https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings"],
            },
            "hardcoded_password": {
                "issue_type": "hardcoded_password",
                "severity": "CRITICAL",
                "problem_summary": "Password is hardcoded in source code, exposing credentials in version control.",
                "fix_summary": "Move credentials to environment variables and use python-dotenv for local development.",
                "before_code": """# NEVER DO THIS
DB_PASSWORD = "my_super_secret_password123"
connection = connect(host="localhost", password=DB_PASSWORD)""",
                "after_code": """import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env file in dev

DB_PASSWORD = os.environ.get("DB_PASSWORD")
if not DB_PASSWORD:
    raise EnvironmentError("DB_PASSWORD environment variable is not set")

connection = connect(host="localhost", password=DB_PASSWORD)""",
                "steps": [
                    "IMMEDIATELY rotate the exposed credential — assume it is compromised",
                    "Create a `.env` file (add to .gitignore if not already)",
                    "Move the credential to the `.env` file: `DB_PASSWORD=your_password`",
                    "Install python-dotenv: `pip install python-dotenv`",
                    "Load env vars with `load_dotenv()` at app startup",
                    "Replace hardcoded value with `os.environ.get('DB_PASSWORD')`",
                    "Add startup validation to fail fast if required env vars are missing",
                    "For production, use a secrets manager (AWS Secrets Manager, Vault, etc.)",
                ],
                "testing_tip": "Run `git log -p | grep -i password` to check if credential was ever committed to history",
                "estimated_time": "30-60 minutes (includes credential rotation)",
                "references": [
                    "https://12factor.net/config",
                    "https://pypi.org/project/python-dotenv/",
                    "https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password",
                ],
            },
            "long_method": {
                "issue_type": "long_method",
                "severity": "MEDIUM",
                "problem_summary": "Function is too long, making it hard to understand, test, and maintain.",
                "fix_summary": "Extract logical sections into smaller, well-named helper functions.",
                "before_code": """def process_order(order_data):
    # validate
    if not order_data.get('user_id'):
        raise ValueError("Missing user_id")
    if not order_data.get('items'):
        raise ValueError("No items in order")
    # ... 80 more lines of mixed concerns
    """,
                "after_code": """def process_order(order_data: dict) -> Order:
    \"\"\"Process a new order end-to-end.\"\"\"
    _validate_order(order_data)
    priced_items = _calculate_prices(order_data['items'])
    order = _create_order_record(order_data['user_id'], priced_items)
    _send_confirmation_email(order)
    return order

def _validate_order(order_data: dict) -> None:
    \"\"\"Validate required order fields.\"\"\"
    if not order_data.get('user_id'):
        raise ValueError("Missing user_id")
    if not order_data.get('items'):
        raise ValueError("No items in order")

def _calculate_prices(items: list) -> list:
    \"\"\"Apply pricing rules to each item.\"\"\"
    # focused, testable logic here
    ...""",
                "steps": [
                    "Identify logical sections in the long function (validation, processing, output)",
                    "Extract each section into a private helper function (prefix with `_`)",
                    "Give each helper a clear, verb-based name describing what it does",
                    "Pass only what each helper needs — avoid global state",
                    "Write unit tests for each extracted helper independently",
                    "Verify the refactored version passes all existing tests",
                ],
                "testing_tip": "Each extracted function should be independently testable — write at least one test per helper",
                "estimated_time": "1-4 hours depending on complexity",
                "references": ["https://refactoring.guru/refactoring/techniques/composing-methods/extract-method"],
            },
            "missing_requirements": {
                "issue_type": "missing_requirements",
                "severity": "HIGH",
                "problem_summary": "No requirements file found, making the project impossible to reliably install.",
                "fix_summary": "Generate a requirements.txt or move to pyproject.toml with pinned dependencies.",
                "before_code": "# No requirements.txt exists",
                "after_code": """# requirements.txt
google-generativeai==0.8.3
requests==2.32.3
streamlit==1.41.1
python-dotenv==1.0.1
rich==13.9.4

# requirements-dev.txt (for development only)
pytest==8.3.4
pytest-cov==6.0.0
black==24.10.0
ruff==0.8.4""",
                "steps": [
                    "Run `pip freeze > requirements.txt` to generate from current environment",
                    "Review and clean up — remove packages you don't actually use",
                    "Pin exact versions with `==` for reproducibility",
                    "Separate dev dependencies into `requirements-dev.txt`",
                    "Test by creating a fresh venv and running `pip install -r requirements.txt`",
                    "Consider migrating to `pyproject.toml` for modern Python packaging",
                ],
                "testing_tip": "Create a fresh virtual environment and run `pip install -r requirements.txt` to verify it works cleanly",
                "estimated_time": "30-60 minutes",
                "references": ["https://pip.pypa.io/en/stable/user_guide/#requirements-files", "https://python-poetry.org/"],
            },
            "no_tests": {
                "issue_type": "no_tests",
                "severity": "HIGH",
                "problem_summary": "No test files found — cannot verify correctness or catch regressions.",
                "fix_summary": "Add pytest-based unit tests for core functionality, starting with the most critical paths.",
                "before_code": "# No tests directory exists",
                "after_code": """# tests/test_core.py
import pytest
from your_module import YourClass

class TestYourClass:
    \"\"\"Tests for YourClass core functionality.\"\"\"

    def test_basic_functionality(self):
        \"\"\"Test the happy path.\"\"\"
        obj = YourClass()
        result = obj.do_something("input")
        assert result == "expected_output"

    def test_invalid_input_raises(self):
        \"\"\"Test that invalid input raises the right exception.\"\"\"
        obj = YourClass()
        with pytest.raises(ValueError, match="Invalid input"):
            obj.do_something(None)

    def test_edge_case_empty_string(self):
        \"\"\"Test edge case: empty string input.\"\"\"
        obj = YourClass()
        result = obj.do_something("")
        assert result == ""  # or whatever is correct""",
                "steps": [
                    "Install pytest: `pip install pytest pytest-cov`",
                    "Create a `tests/` directory at the project root",
                    "Start with tests for the most critical/complex functions",
                    "Write at least: one happy path, one error case, one edge case per function",
                    "Run tests with: `pytest tests/ -v --cov=your_module`",
                    "Add a `pytest.ini` or `pyproject.toml` section for test configuration",
                    "Set up GitHub Actions to run tests on every push",
                ],
                "testing_tip": "Aim for 70%+ coverage on business-critical code. Use `pytest --cov --cov-report=html` to see a visual coverage report",
                "estimated_time": "1-3 days for initial test suite",
                "references": ["https://docs.pytest.org/en/stable/", "https://coverage.readthedocs.io/"],
            },
        }
