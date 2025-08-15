import json
from typing import List, Dict

def clean_json_string(raw: str) -> str:
    """Extract JSON objects from an arbitrary string and return a JSON array string.

    The input may contain descriptive text and multiple JSON objects separated by whitespace.
    This function locates balanced curly-brace blocks and joins them into a JSON array
    so that ``json.loads`` can parse the result.
    """
    objects = []
    depth = 0
    buffer = []

    for char in raw:
        if char == '{':
            if depth == 0:
                buffer = []
            depth += 1
        if depth > 0:
            buffer.append(char)
        if char == '}':
            depth -= 1
            if depth == 0 and buffer:
                objects.append(''.join(buffer))
                buffer = []

    return '[' + ','.join(objects) + ']'


def parse_test_cases(raw: str) -> List[Dict]:
    """Parse a raw test case string into a list of dictionaries."""
    cleaned = clean_json_string(raw)
    if cleaned == '[]':
        return []
    return json.loads(cleaned)


if __name__ == '__main__':
    import sys
    input_text = sys.stdin.read()
    cases = parse_test_cases(input_text)
    print(json.dumps(cases, indent=2))
