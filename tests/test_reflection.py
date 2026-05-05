import pytest
from contextxss.core.reflector import detect_reflection

def test_detect_reflection_success():
    response = "<html><body>Hello XSSCTX12345!</body></html>"
    is_reflected, positions = detect_reflection(response, "XSSCTX12345")
    assert is_reflected is True
    assert len(positions) == 1
    assert positions[0] == 18

def test_detect_reflection_failure():
    response = "<html><body>Hello World!</body></html>"
    is_reflected, positions = detect_reflection(response, "XSSCTX12345")
    assert is_reflected is False
    assert len(positions) == 0

def test_detect_reflection_empty():
    is_reflected, positions = detect_reflection("", "XSSCTX12345")
    assert is_reflected is False
