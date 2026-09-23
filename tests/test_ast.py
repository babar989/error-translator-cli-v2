import os
import tempfile

import pytest

from error_translator.ast.ast_engine import get_ast_suggestions

# Use distinctly different variable names so difflib doesn't accidentally match them!
MOCK_CODE = """
global_var = 100

def func_a():
    apple_qty = 1
    # Crash happens here (line 6)
    print(appl_qty)

def func_b():
    banana_num = 2
    # Crash happens here (line 11)
    print(banan_num)
"""


@pytest.fixture
def mock_file():
    fd, path = tempfile.mkstemp(suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(MOCK_CODE)
    yield path
    os.remove(path)


def test_ast_scoping_func_a(mock_file):
    # Simulate a NameError crash on line 6 (inside func_a) looking for 'appl_qty'
    suggestion = get_ast_suggestions(mock_file, "6", "appl_qty", "NameError")
    assert suggestion == "apple_qty"

    # Try to access func_b's variable from func_a
    suggestion_bad = get_ast_suggestions(mock_file, "6", "banan_num", "NameError")
    assert suggestion_bad is None  # Should be completely blocked


def test_ast_scoping_func_b(mock_file):
    # Simulate a NameError crash on line 11 (inside func_b)
    suggestion = get_ast_suggestions(mock_file, "11", "banan_num", "NameError")
    assert suggestion == "banana_num"


MOCK_ASYNC_CODE = """
async def fetch_data():
    user_count = 10
    # line 4
    print(usr_count)
    return user_count

# line 8
print(usr_count)

# line 11
print(fetch_dta)
"""


@pytest.fixture
def mock_async_file():
    fd, path = tempfile.mkstemp(suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(MOCK_ASYNC_CODE)
    yield path
    os.remove(path)


def test_ast_scoping_async_leak(mock_async_file):
    # Leak regression: inside an async function 'user_count' is defined.
    # At module level (line 8), a crash for 'usr_count' should NOT suggest 'user_count'.
    suggestion = get_ast_suggestions(mock_async_file, "8", "usr_count", "NameError")
    assert suggestion is None


def test_ast_scoping_async_inside(mock_async_file):
    # Inside-async suggestion: inside async function, 'usr_count' should suggest 'user_count'.
    suggestion = get_ast_suggestions(mock_async_file, "4", "usr_count", "NameError")
    assert suggestion == "user_count"


def test_ast_scoping_async_name(mock_async_file):
    # Async function name in enclosing scope: module-level typo 'fetch_dta' -> 'fetch_data'
    suggestion = get_ast_suggestions(mock_async_file, "11", "fetch_dta", "NameError")
    assert suggestion == "fetch_data"
