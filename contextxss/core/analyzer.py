from bs4 import BeautifulSoup
import re


def analyze_context(response_text: str, marker: str, positions: list[int]) -> str:
    """
    Determines the context of the reflection (HTML, Attribute, JavaScript).
    Uses BeautifulSoup4 for DOM parsing and regex fallbacks.
    """
    soup = BeautifulSoup(response_text, 'html.parser')

    # Check for JavaScript context
    script_tags = soup.find_all('script')
    for script in script_tags:
        if script.string and marker in script.string:
            return "javascript"

    # Check for inline JS attributes (onclick, onmouseover, etc.) and general attrs
    for tag in soup.find_all(True):
        for attr, value in tag.attrs.items():
            if isinstance(value, str) and marker in value:
                if attr.startswith('on'):
                    return "javascript"  # Reflected inside an event handler
                return "attribute"
            elif isinstance(value, list):  # Some attributes like class are lists
                for v in value:
                    if marker in v:
                        return "attribute"

    # If not in script and not in attribute, check text content
    for text_node in soup.find_all(string=True):
        if marker in text_node:
            if text_node.parent.name == "script":
                return "javascript"
            return "html"

    # Fallback regex if bs4 fails to build a proper tree around the marker
    script_pattern = re.compile(
        r'<script[^>]*>.*?' + re.escape(marker) + r'.*?</script>',
        re.IGNORECASE | re.DOTALL
    )
    if script_pattern.search(response_text):
        return "javascript"

    attr_pattern = re.compile(
        r'<[^>]*?[\s]+[a-zA-Z\-]+=["\'][^"\']*?' + re.escape(marker) + r'[^"\']*?["\'][^>]*?>',
        re.IGNORECASE
    )
    if attr_pattern.search(response_text):
        return "attribute"

    # Default to HTML
    return "html"
