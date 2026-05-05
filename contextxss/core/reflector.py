import re


def detect_reflection(response_text: str, marker: str) -> tuple[bool, list[int]]:
    """
    Checks if the marker appears in the response text.
    Returns (is_reflected, reflection_positions).
    """
    if not response_text:
        return False, []

    valid_positions = []
    for m in re.finditer(re.escape(marker), response_text):
        pos = m.start()
        # If the marker starts with a quote, verify it's not escaped
        if marker[0] in ['"', "'"] and pos > 0 and response_text[pos - 1] == '\\':
            continue
        valid_positions.append(pos)

    if valid_positions:
        return True, valid_positions

    return False, []
