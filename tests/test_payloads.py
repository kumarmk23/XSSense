import pytest
from contextxss.core.payload_engine import get_payloads

def test_get_payloads_html_deep():
    payloads = get_payloads("html", mode="deep")
    assert isinstance(payloads, list)
    assert len(payloads) > 0
    assert isinstance(payloads[0], dict)
    assert "payload" in payloads[0]
    assert "explanation" in payloads[0]

def test_get_payloads_html_quick():
    payloads = get_payloads("html", mode="quick")
    assert isinstance(payloads, list)
    assert len(payloads) > 0
    for p in payloads:
        assert p.get("tier") == "quick"

def test_get_payloads_unknown_context():
    # Should fallback to html
    payloads = get_payloads("unknown_context")
    assert isinstance(payloads, list)
    assert len(payloads) > 0
    assert isinstance(payloads[0], dict)
