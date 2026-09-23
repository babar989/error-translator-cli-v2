"""
Traceback parsing module.
Responsible for extracting contextual information from traceback strings.
"""

import linecache
import os
import re

EXCEPTION_LINE = re.compile(
    r"^[\w.]*(?:Error|Exception|Warning|Exit|Interrupt|Iteration|NotImplemented)(?::|$)"
)


def extract_error_line(traceback_text: str) -> str:
    """
    Extract the actual error line from the traceback text,
    ignoring any trailing noise from frameworks or standard error.
    """
    lines = [line.strip() for line in traceback_text.strip().split("\n") if line.strip()]
    if not lines:
        return ""

    for line in reversed(lines):
        if EXCEPTION_LINE.match(line):
            return line

    return lines[-1]


def extract_location(traceback_text: str) -> tuple[str, str]:
    """
    Extract the file name and line number where the error occurred
    by parsing the standard Python traceback format.

    Args:
        traceback_text (str): The raw traceback text.

    Returns:
        tuple[str, str]: The file name and line number.
    """
    # Regex to capture "File <path>, line <number>"
    matches = re.findall(r'File\s+[\'"]?(.*?)[\'"]?,\s+line\s+(\d+)', traceback_text)
    if not matches:
        return "Unknown File", "Unknown Line"

    cwd = os.getcwd()
    # Try to find the last match that is in the current working directory
    for file_path, line_num in reversed(matches):
        abs_path = os.path.abspath(file_path)
        try:
            if os.path.commonpath([cwd, abs_path]) == cwd:
                return file_path, line_num
        except ValueError:
            pass

    # Fallback to the last match overall
    return matches[-1][0], matches[-1][1]


def extract_code_context(file_name: str, line_number: str) -> str:
    """
    Attempt to read the exact line of code that caused the error.

    Args:
        file_name (str): Path to the source file.
        line_number (str): Line number string.

    Returns:
        str: The extracted line of code, or empty string if not found.
    """
    if file_name != "Unknown File" and line_number != "Unknown Line":
        try:
            raw_line = linecache.getline(file_name, int(line_number))
            if raw_line:
                return raw_line.strip()
        except (OSError, ValueError):
            pass
    return ""
