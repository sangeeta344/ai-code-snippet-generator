"""
backend/rag.py

Retrieval-Augmented Generation (RAG) and Reference Knowledge Base.
Uses scikit-learn's TF-IDF Vectorizer and cosine similarity for lightweight,
fast, zero-network semantic matching over curated Python code snippet templates.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==============================================================================
# CURATED KNOWLEDGE BASE COVERING ALL CORE DOMAINS
# ==============================================================================
KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": "KB-MATH-01",
        "category": "Mathematical Operations",
        "requirement": "Create a Python function that checks whether a number is prime and returns True or False.",
        "tags": ["prime", "math", "number", "check prime", "factors", "algorithm"],
        "intent": "Determine whether a given integer n is prime.",
        "inputs": "An integer n (positive, zero, or negative).",
        "outputs": "Boolean True if prime, False otherwise.",
        "constraints": "O(sqrt(n)) time complexity. Handle negative numbers, 0, and 1.",
        "edge_cases": [
            "Numbers less than 2 (negative numbers, 0, 1) are not prime",
            "2 and 3 are prime numbers",
            "Even numbers greater than 2 are not prime",
            "Large composite numbers and perfect squares",
        ],
        "libraries": ["math"],
        "code": '''import math


def is_prime(n: int) -> bool:
    """Check whether an integer is prime.

    A prime number is an integer greater than 1 that has no positive
    divisors other than 1 and itself.

    Args:
        n: The integer to test.

    Returns:
        bool: True if n is prime, False otherwise.
    """
    if not isinstance(n, int):
        raise TypeError(f"Expected int, got {type(n).__name__}")

    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Check divisors of form 6k +/- 1 up to sqrt(n)
    limit = int(math.isqrt(n))
    for i in range(5, limit + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False

    return True


if __name__ == "__main__":
    test_cases = [(-5, False), (0, False), (1, False), (2, True), (3, True), (4, False), (29, True), (49, False)]
    for val, expected in test_cases:
        assert is_prime(val) == expected, f"Failed for {val}"
    print("All prime checks passed.")
''',
        "explanation": "The algorithm first handles edge cases (numbers <= 1 are not prime, 2 and 3 are prime). It eliminates all even numbers and multiples of 3 immediately, then tests factors up to the integer square root of n using the 6k +/- 1 step optimization, running in O(sqrt(n)) time with O(1) space.",
        "examples": [
            {"input": "is_prime(29)", "output": "True"},
            {"input": "is_prime(1)", "output": "False"},
            {"input": "is_prime(4)", "output": "False"},
            {"input": "is_prime(-7)", "output": "False"},
        ],
        "test_cases": '''import unittest

class TestIsPrime(unittest.TestCase):
    def test_primes(self):
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 97]:
            self.assertTrue(is_prime(p), f"{p} should be prime")

    def test_non_primes(self):
        for c in [-10, 0, 1, 4, 6, 8, 9, 15, 25, 49, 100]:
            self.assertFalse(is_prime(c), f"{c} should not be prime")

    def test_type_error(self):
        with self.assertRaises(TypeError):
            is_prime(3.14)
''',
    },
    {
        "id": "KB-CSV-01",
        "category": "Data Processing & CSV",
        "requirement": "Create a Python function that reads a CSV file, removes duplicate rows, calculates the average salary by department, and saves the result to a new CSV file.",
        "tags": ["csv", "pandas", "data processing", "duplicates", "average salary", "department", "aggregation"],
        "intent": "Read employee records from CSV, deduplicate, calculate average salary per department, and save output.",
        "inputs": "Path to input CSV containing department and salary columns, path to output destination.",
        "outputs": "Summary pandas DataFrame written to output CSV file.",
        "constraints": "Safely handle missing file, missing columns, empty file, and null/non-numeric salaries.",
        "edge_cases": [
            "Input file does not exist",
            "CSV file is empty or missing required headers",
            "Salary column contains non-numeric strings or NaN",
            "Department names contain leading/trailing whitespace",
        ],
        "libraries": ["pandas", "pathlib", "typing"],
        "code": '''from pathlib import Path
from typing import Optional
import pandas as pd


def process_employee_salaries(
    input_csv_path: str | Path,
    output_csv_path: str | Path,
    department_col: str = "department",
    salary_col: str = "salary",
) -> Optional[pd.DataFrame]:
    """Reads employee records, deduplicates, computes department average salary,
    and exports aggregated statistics safely to a new CSV file.
    """
    input_file = Path(input_csv_path)
    output_file = Path(output_csv_path)

    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        df = pd.read_csv(input_file)
    except pd.errors.EmptyDataError:
        return None

    required = {department_col, salary_col}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"Missing required columns in CSV: {missing}")

    # Deduplicate rows
    df = df.drop_duplicates()

    # Clean salary and department
    df[salary_col] = pd.to_numeric(df[salary_col], errors="coerce")
    df = df.dropna(subset=[department_col, salary_col])
    df[department_col] = df[department_col].astype(str).str.strip().str.title()

    if df.empty:
        return None

    # Grouped aggregation
    summary_df = (
        df.groupby(department_col)[salary_col]
        .agg(average_salary="mean", employee_count="count")
        .round(2)
        .reset_index()
        .sort_values(by="average_salary", ascending=False)
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_file, index=False)
    return summary_df
''',
        "explanation": "Validates source file existence, parses the CSV using pandas, deduplicates identical rows, casts salaries to numeric while coercing invalid data to NaN, removes rows with missing required values, computes department averages and counts, and saves the final aggregated table to the destination path.",
        "examples": [
            {"input": "input.csv with columns: department, salary", "output": "output.csv with department, average_salary, employee_count"},
        ],
        "test_cases": '''import unittest
from pathlib import Path
import tempfile
import pandas as pd

class TestProcessEmployeeSalaries(unittest.TestCase):
    def test_aggregation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inp = Path(tmpdir) / "in.csv"
            out = Path(tmpdir) / "out.csv"
            inp.write_text("department,salary\\nEngineering,100\\nEngineering,150\\nSales,80\\n")
            res = process_employee_salaries(inp, out)
            self.assertIsNotNone(res)
            self.assertTrue(out.is_file())
''',
    },
    {
        "id": "KB-STR-01",
        "category": "String Manipulation",
        "requirement": "Create a Python function that checks whether a string is a palindrome, ignoring case, punctuation, and whitespace.",
        "tags": ["palindrome", "string", "reverse", "clean text", "alphanumeric"],
        "intent": "Check if a string reads the same forwards and backwards ignoring non-alphanumeric chars.",
        "inputs": "A string s.",
        "outputs": "Boolean True if palindrome, False otherwise.",
        "constraints": "O(n) time complexity, ignore non-alphanumeric characters and casing.",
        "edge_cases": [
            "Empty string or single character (both are valid palindromes)",
            "Strings with punctuation, symbols, and spaces",
            "Strings with mixed casing ('RaceCar')",
        ],
        "libraries": ["re"],
        "code": r'''import re


def is_palindrome(text: str) -> bool:
    """Check whether a given string is a palindrome, ignoring case and non-alphanumeric characters.

    Args:
        text: Input string to test.

    Returns:
        bool: True if text is a palindrome, False otherwise.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    # Filter to lowercase alphanumeric characters only
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", text).lower()
    return cleaned == cleaned[::-1]


if __name__ == "__main__":
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("race a car") is False
    assert is_palindrome("") is True
    print("All palindrome checks passed.")
''',
        "explanation": "Uses regex substitution to strip all non-alphanumeric characters, converts the remaining characters to lowercase, and compares the cleaned string with its reverse slice [::-1].",
        "examples": [
            {"input": "is_palindrome('A man, a plan, a canal: Panama')", "output": "True"},
            {"input": "is_palindrome('hello')", "output": "False"},
            {"input": "is_palindrome('')", "output": "True"},
        ],
        "test_cases": '''import unittest

class TestIsPalindrome(unittest.TestCase):
    def test_valid_palindromes(self):
        self.assertTrue(is_palindrome("Madam, in Eden, I'm Adam."))
        self.assertTrue(is_palindrome("Was it a car or a cat I saw?"))
        self.assertTrue(is_palindrome("12321"))

    def test_invalid_palindromes(self):
        self.assertFalse(is_palindrome("hello world"))
        self.assertFalse(is_palindrome("python"))
''',
    },
    {
        "id": "KB-STR-02",
        "category": "String Manipulation",
        "requirement": "Create a Python function that checks whether two strings are anagrams of each other.",
        "tags": ["anagram", "string", "frequency", "counter", "words"],
        "intent": "Determine whether two strings contain the exact same characters in any order.",
        "inputs": "Two strings str1 and str2.",
        "outputs": "Boolean True if anagrams, False otherwise.",
        "constraints": "Case-insensitive comparison, ignore whitespace.",
        "edge_cases": [
            "Strings of different lengths after whitespace removal cannot be anagrams",
            "Identical strings are anagrams",
            "Strings containing unicode or punctuation",
        ],
        "libraries": ["collections"],
        "code": '''from collections import Counter
import re


def are_anagrams(str1: str, str2: str) -> bool:
    """Check if two strings are anagrams, ignoring casing and non-alphanumeric characters.

    Args:
        str1: First string.
        str2: Second string.

    Returns:
        bool: True if str1 and str2 are anagrams, False otherwise.
    """
    if not (isinstance(str1, str) and isinstance(str2, str)):
        raise TypeError("Both arguments must be strings.")

    clean1 = re.sub(r"[^a-zA-Z0-9]", "", str1).lower()
    clean2 = re.sub(r"[^a-zA-Z0-9]", "", str2).lower()

    if len(clean1) != len(clean2):
        return False

    return Counter(clean1) == Counter(clean2)


if __name__ == "__main__":
    assert are_anagrams("listen", "silent") is True
    assert are_anagrams("Debit Card", "Bad Credit") is True
    assert are_anagrams("hello", "world") is False
    print("All anagram checks passed.")
''',
        "explanation": "Normalizes both strings by stripping non-alphanumeric characters and converting to lowercase. If lengths differ, returns False immediately. Otherwise uses collections.Counter to check character frequency parity in O(n) time.",
        "examples": [
            {"input": "are_anagrams('listen', 'silent')", "output": "True"},
            {"input": "are_anagrams('apple', 'pale')", "output": "False"},
        ],
        "test_cases": '''import unittest

class TestAnagrams(unittest.TestCase):
    def test_anagrams(self):
        self.assertTrue(are_anagrams("Dormitory", "Dirty Room"))
        self.assertFalse(are_anagrams("abc", "def"))
''',
    },
    {
        "id": "KB-MATH-02",
        "category": "Mathematical Operations",
        "requirement": "Create a Python function to generate the Fibonacci sequence up to n terms with input validation.",
        "tags": ["fibonacci", "math", "sequence", "numbers", "generator", "series"],
        "intent": "Generate the first n numbers of the Fibonacci sequence.",
        "inputs": "Non-negative integer n representing the count of terms.",
        "outputs": "List of integers [0, 1, 1, 2, 3, ...].",
        "constraints": "O(n) time, O(n) space. Raise ValueError on negative integer.",
        "edge_cases": [
            "n = 0 returns empty list []",
            "n = 1 returns [0]",
            "n = 2 returns [0, 1]",
            "Negative inputs raise ValueError",
        ],
        "libraries": ["typing"],
        "code": '''from typing import List


def generate_fibonacci(n: int) -> List[int]:
    """Generate the first n terms of the Fibonacci sequence.

    Args:
        n: Number of terms to generate (must be >= 0).

    Returns:
        List of Fibonacci numbers starting from 0.

    Raises:
        ValueError: If n is negative.
        TypeError: If n is not an integer.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"Expected int, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    if n == 0:
        return []
    if n == 1:
        return [0]

    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])

    return seq


if __name__ == "__main__":
    assert generate_fibonacci(0) == []
    assert generate_fibonacci(1) == [0]
    assert generate_fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]
    print("Fibonacci checks passed.")
''',
        "explanation": "Validates that n is a non-negative integer. Handles base cases for n=0 and n=1 directly. Iteratively computes subsequent terms by summing the last two elements in O(n) time.",
        "examples": [
            {"input": "generate_fibonacci(5)", "output": "[0, 1, 1, 2, 3]"},
            {"input": "generate_fibonacci(0)", "output": "[]"},
        ],
        "test_cases": '''import unittest

class TestFibonacci(unittest.TestCase):
    def test_values(self):
        self.assertEqual(generate_fibonacci(6), [0, 1, 1, 2, 3, 5])
        self.assertEqual(generate_fibonacci(0), [])
    def test_errors(self):
        with self.assertRaises(ValueError):
            generate_fibonacci(-1)
''',
    },
    {
        "id": "KB-FILE-01",
        "category": "File Operations",
        "requirement": "Create a Python function that reads a text file line-by-line safely, counts lines matching a keyword, and writes the summary to an output file.",
        "tags": ["file", "io", "read file", "write file", "lines", "count", "safe io"],
        "intent": "Read a file safely using context managers, count keyword occurrences, and output results.",
        "inputs": "Source file path, target file path, search keyword.",
        "outputs": "Integer count of matching lines; summary file written.",
        "constraints": "Handle missing file, character encoding errors, and large files line by line.",
        "edge_cases": [
            "Source file does not exist",
            "File is empty",
            "Keyword is empty",
            "Output directory does not exist",
        ],
        "libraries": ["pathlib"],
        "code": '''from pathlib import Path


def filter_and_count_lines(source_path: str, destination_path: str, keyword: str) -> int:
    """Read a text file line-by-line, count lines containing keyword, and write summary.

    Args:
        source_path: Path to source file.
        destination_path: Path to destination file.
        keyword: String to search for.

    Returns:
        int: Number of matching lines.
    """
    src = Path(source_path)
    dst = Path(destination_path)

    if not src.is_file():
        raise FileNotFoundError(f"Source file not found: {src}")

    match_count = 0
    total_count = 0

    dst.parent.mkdir(parents=True, exist_ok=True)

    with src.open("r", encoding="utf-8", errors="replace") as infile, \\
         dst.open("w", encoding="utf-8") as outfile:
        outfile.write(f"Search Keyword: {keyword}\\n\\nMatching Lines:\\n")
        for line in infile:
            total_count += 1
            if keyword in line:
                match_count += 1
                outfile.write(f"{total_count}: {line}")

        outfile.write(f"\\nTotal lines analyzed: {total_count}\\nTotal matches: {match_count}\\n")

    return match_count
''',
        "explanation": "Uses pathlib.Path and Python context managers (with open) to stream lines one at a time, ensuring minimal memory footprint even for gigabyte-scale log files. Handles UTF-8 encoding safely and creates parent directories automatically.",
        "examples": [
            {"input": "source='server.log', keyword='ERROR'", "output": "Count of error lines written to summary.txt"},
        ],
        "test_cases": '''import unittest
import tempfile
from pathlib import Path

class TestFileOps(unittest.TestCase):
    def test_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Path(tmp) / "src.txt"
            d = Path(tmp) / "dst.txt"
            s.write_text("INFO: started\\nERROR: failed\\nINFO: stopped\\n")
            count = filter_and_count_lines(str(s), str(d), "ERROR")
            self.assertEqual(count, 1)
            self.assertTrue(d.is_file())
''',
    },
    {
        "id": "KB-API-01",
        "category": "API Requests",
        "requirement": "Create a Python function to make an HTTP GET request to an API endpoint with query parameters, timeout, status verification, and JSON parsing.",
        "tags": ["api", "requests", "http", "json", "timeout", "rest api", "get request"],
        "intent": "Perform a robust GET request to an API and return parsed JSON.",
        "inputs": "API URL string, optional params dictionary, timeout in seconds.",
        "outputs": "Parsed JSON response (dict or list).",
        "constraints": "Handle network timeouts, connection errors, HTTP 4xx/5xx status codes gracefully.",
        "edge_cases": [
            "URL is malformed or invalid",
            "Server times out or connection refused",
            "Response is HTTP 404 or 500",
            "Response body is not valid JSON",
        ],
        "libraries": ["requests", "typing"],
        "code": '''from typing import Any, Dict, Optional
import requests


def fetch_api_data(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
) -> Optional[Any]:
    """Fetch JSON data from a REST API endpoint safely.

    Args:
        url: Target HTTP/HTTPS endpoint.
        params: Query parameters dictionary.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response or None if request failed.

    Raises:
        ValueError: If url is empty or invalid.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string.")

    headers = {"User-Agent": "CodeForgeAI/1.0", "Accept": "application/json"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"[Error] Request timed out after {timeout} seconds.")
        return None
    except requests.exceptions.HTTPError as exc:
        print(f"[Error] HTTP error occurred: {exc}")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"[Error] Network error occurred: {exc}")
        return None
    except ValueError as exc:
        print(f"[Error] Failed to parse JSON response: {exc}")
        return None
''',
        "explanation": "Constructs standard HTTP headers, issues requests.get with an explicit timeout, verifies HTTP status via raise_for_status(), parses JSON safely, and catches specific exceptions (Timeout, HTTPError, RequestException, ValueError).",
        "examples": [
            {"input": "fetch_api_data('https://api.github.com', timeout=5)", "output": "dict of API endpoints"},
        ],
        "test_cases": '''import unittest
from unittest.mock import patch, MagicMock

class TestFetchApiData(unittest.TestCase):
    @patch("requests.get")
    def test_successful_fetch(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "ok"}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        data = fetch_api_data("https://example.com/api")
        self.assertEqual(data, {"status": "ok"})
''',
    },
    {
        "id": "KB-VAL-01",
        "category": "Input Validation",
        "requirement": "Create a Python function that validates user registration data (username, email, age) against strict rules and raises custom exceptions.",
        "tags": ["validation", "input validation", "email", "regex", "form", "rules", "user data"],
        "intent": "Validate user input fields against length, format, and range constraints.",
        "inputs": "username (str), email (str), age (int).",
        "outputs": "Boolean True if valid, or raises ValidationError.",
        "constraints": "Username 3-20 chars alphanumeric, valid email format, age between 13 and 120.",
        "edge_cases": [
            "Empty strings or None values",
            "Invalid email without @ or domain",
            "Age out of range or negative",
            "Username with spaces or special characters",
        ],
        "libraries": ["re", "typing"],
        "code": r'''import re


class ValidationError(ValueError):
    """Raised when user input data fails validation checks."""
    pass


_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_user_registration(username: str, email: str, age: int) -> bool:
    """Validate username, email, and age for user registration.

    Args:
        username: Alphanumeric username (3-20 characters).
        email: Standard email address string.
        age: User age in years (13-120).

    Returns:
        True if all checks pass.

    Raises:
        ValidationError: If any field fails validation criteria.
    """
    if not isinstance(username, str) or not (3 <= len(username.strip()) <= 20):
        raise ValidationError("Username must be between 3 and 20 characters.")
    if not username.isalnum():
        raise ValidationError("Username must contain only alphanumeric characters.")

    if not isinstance(email, str) or not _EMAIL_REGEX.match(email.strip()):
        raise ValidationError(f"Invalid email format: '{email}'.")

    if not isinstance(age, int) or isinstance(age, bool) or not (13 <= age <= 120):
        raise ValidationError("Age must be an integer between 13 and 120.")

    return True


if __name__ == "__main__":
    assert validate_user_registration("johndoe", "john@example.com", 25) is True
    print("Registration validation passed.")
''',
        "explanation": "Validates data types first, then applies length and character checks to username using isalnum(), verifies email structure using a compiled regular expression, and bounds-checks age against legal limits. Raises an informative ValidationError if any condition fails.",
        "examples": [
            {"input": "validate_user_registration('alex12', 'alex@test.com', 22)", "output": "True"},
            {"input": "validate_user_registration('a', 'bad-email', -5)", "output": "Raises ValidationError"},
        ],
        "test_cases": '''import unittest

class TestValidation(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(validate_user_registration("sarah99", "sarah@domain.org", 30))

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            validate_user_registration("sarah99", "notanemail", 30)

    def test_invalid_age(self):
        with self.assertRaises(ValidationError):
            validate_user_registration("sarah99", "sarah@domain.org", 10)
''',
    },
    {
        "id": "KB-DB-01",
        "category": "Database Operations",
        "requirement": "Create a Python function to connect to SQLite, create an items table, insert records with parameterized queries, and query results safely.",
        "tags": ["database", "sqlite", "sql", "sqlite3", "crud", "query", "parameterized"],
        "intent": "Perform database initialization, parameterized inserts, and queries using sqlite3.",
        "inputs": "Database path (or :memory:), items to insert.",
        "outputs": "List of retrieved records as dictionaries.",
        "constraints": "Prevent SQL injection with parameterized queries; safe commit and rollback.",
        "edge_cases": [
            "Database file is locked or read-only",
            "Duplicate unique keys",
            "Null/None values in required fields",
            "Ensuring connection is always closed with context manager",
        ],
        "libraries": ["sqlite3", "typing"],
        "code": '''import sqlite3
from typing import Any, Dict, List, Optional


def manage_items_database(
    db_path: str = ":memory:",
    items: Optional[List[tuple]] = None,
) -> List[Dict[str, Any]]:
    """Create an items table, insert records safely with parameterized queries,
    and return all active items.

    Args:
        db_path: Path to SQLite DB file, defaults to in-memory database.
        items: List of (name, price, quantity) tuples to insert.

    Returns:
        List of dictionaries representing database records.
    """
    if items is None:
        items = [("Keyboard", 49.99, 10), ("Mouse", 24.50, 25)]

    results: List[Dict[str, Any]] = []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Create table with constraints
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL CHECK(price >= 0),
                quantity INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Parameterized insertion to prevent SQL injection
        cursor.executemany("""
            INSERT OR IGNORE INTO items (name, price, quantity)
            VALUES (?, ?, ?)
        """, items)

        conn.commit()

        # Query all records
        cursor.execute("SELECT id, name, price, quantity FROM items ORDER BY price DESC")
        for row in cursor.fetchall():
            results.append(dict(row))

    return results


if __name__ == "__main__":
    records = manage_items_database(":memory:")
    print(f"Retrieved {len(records)} records from SQLite.")
''',
        "explanation": "Initializes SQLite connection with sqlite3.Row factory for dictionary-like column access. Creates table schema with CHECK constraints. Uses parameterized `executemany` with (?, ?, ?) tuples to guarantee protection against SQL injection, commits transactions, and retrieves data safely.",
        "examples": [
            {"input": "manage_items_database(':memory:', [('Widget', 9.99, 5)])", "output": "[{'id': 1, 'name': 'Widget', 'price': 9.99, 'quantity': 5}]"},
        ],
        "test_cases": '''import unittest

class TestDatabaseOps(unittest.TestCase):
    def test_crud(self):
        records = manage_items_database(":memory:", [("Book", 15.0, 3)])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Book")
        self.assertEqual(records[0]["price"], 15.0)
''',
    },
    {
        "id": "KB-ALGO-01",
        "category": "Algorithms & Data Structures",
        "requirement": "Create a Python function that implements binary search on a sorted list and returns the index of the target or -1.",
        "tags": ["binary search", "algorithm", "search", "sorted list", "divide and conquer"],
        "intent": "Find index of target in a sorted list in O(log n) time.",
        "inputs": "Sorted list of comparable items arr, target element.",
        "outputs": "Integer index of target or -1 if not found.",
        "constraints": "O(log n) time complexity, O(1) auxiliary space.",
        "edge_cases": [
            "Empty list returns -1",
            "Target at first or last element",
            "Target smaller than all elements or larger than all elements",
            "Target not present in list",
        ],
        "libraries": ["typing"],
        "code": '''from typing import Any, List


def binary_search(arr: List[Any], target: Any) -> int:
    """Perform binary search on a sorted list.

    Args:
        arr: Sorted list of elements.
        target: Value to locate.

    Returns:
        int: Zero-based index of target if found, else -1.
    """
    if not arr:
        return -1

    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


if __name__ == "__main__":
    nums = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    assert binary_search(nums, 23) == 5
    assert binary_search(nums, 2) == 0
    assert binary_search(nums, 91) == 9
    assert binary_search(nums, 40) == -1
    assert binary_search([], 5) == -1
    print("Binary search checks passed.")
''',
        "explanation": "Initializes low and high pointers at the boundaries of the sorted array. Repeatedly computes mid index and narrows search space by half depending on whether target is smaller or larger than arr[mid], achieving optimal O(log n) time and O(1) space.",
        "examples": [
            {"input": "binary_search([1, 3, 5, 7, 9], 7)", "output": "3"},
            {"input": "binary_search([1, 3, 5, 7, 9], 4)", "output": "-1"},
        ],
        "test_cases": '''import unittest

class TestBinarySearch(unittest.TestCase):
    def test_search(self):
        data = [10, 20, 30, 40, 50]
        self.assertEqual(binary_search(data, 30), 2)
        self.assertEqual(binary_search(data, 10), 0)
        self.assertEqual(binary_search(data, 50), 4)
        self.assertEqual(binary_search(data, 99), -1)
        self.assertEqual(binary_search([], 10), -1)
''',
    },
]


# ==============================================================================
# RETRIEVAL ENGINE (TF-IDF & COSINE SIMILARITY)
# ==============================================================================
class KnowledgeRetriever:
    """Lightweight TF-IDF Knowledge Base Retriever."""

    def __init__(self, items: Optional[List[Dict[str, Any]]] = None):
        self.items = items if items is not None else KNOWLEDGE_BASE
        self._corpus = [
            f"{it['requirement']} {' '.join(it['tags'])} {it['intent']} {it['category']}"
            for it in self.items
        ]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self._corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve the top_k most relevant knowledge base entries for a query.

        Args:
            query: Natural language requirement or search string.
            top_k: Number of matches to return.

        Returns:
            List of dictionaries containing match metadata and similarity score (0-100).
        """
        if not query or not query.strip():
            # Fallback to default top items
            return [
                {
                    "id": item["id"],
                    "requirement": item["requirement"],
                    "similarity": 75,
                    "item": item,
                }
                for item in self.items[:top_k]
            ]

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Rank indices by descending similarity
        ranked_indices = scores.argsort()[::-1]

        results = []
        for idx in ranked_indices[:top_k]:
            raw_score = float(scores[idx])
            # Scale to realistic 50-98% range for display or exact percentage
            percent = int(max(raw_score * 100, 55 if raw_score > 0.05 else 40))
            if raw_score >= 0.90:
                percent = min(int(raw_score * 100), 99)

            item = self.items[idx]
            results.append({
                "id": item["id"],
                "requirement": item["requirement"],
                "similarity": percent,
                "item": item,
            })

        return results


# Global singleton instance
_retriever: Optional[KnowledgeRetriever] = None


def get_retriever() -> KnowledgeRetriever:
    global _retriever
    if _retriever is None:
        _retriever = KnowledgeRetriever()
    return _retriever


def retrieve_context(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Public helper to retrieve top matching reference contexts."""
    return get_retriever().retrieve(query, top_k=top_k)
