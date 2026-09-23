import re

EXCEPTION_LINE = re.compile(
    r"^[\w.]*(?:Error|Exception|Warning|Exit|Interrupt|Iteration|NotImplemented)(?::|$)"
)


def extract_error_line(traceback_text: str) -> str:
    lines = [line.strip() for line in traceback_text.strip().split("\n") if line.strip()]
    if not lines:
        return ""
    for line in reversed(lines):
        if EXCEPTION_LINE.match(line):
            return line
    return lines[-1]


print(
    extract_error_line(
        "Traceback...\nZeroDivisionError: division by zero\nSomeFramework: session torn down"
    )
)
print(extract_error_line("KeyError: 'x'"))
print(extract_error_line("Plain sentence."))
print(
    extract_error_line(
        "Traceback1...\nDuring handling of the above exception, another exception occurred:\nTraceback2...\nKeyError: 'foo'"
    )
)
print(extract_error_line("Traceback...\nKeyboardInterrupt"))
print(
    extract_error_line(
        "Traceback...\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)"
    )
)
print(extract_error_line("SomeError: first part of message\ncontinuation line\nanother line"))
