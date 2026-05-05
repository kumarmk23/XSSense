import pytest
from contextxss.core.analyzer import analyze_context

def test_analyze_html_context():
    html = "<div>User input: XSSCTX12345</div>"
    context = analyze_context(html, "XSSCTX12345", [])
    assert context == "html"

def test_analyze_attribute_context():
    html = "<input type='text' name='q' value='XSSCTX12345'>"
    context = analyze_context(html, "XSSCTX12345", [])
    assert context == "attribute"
    
def test_analyze_attribute_context_double_quotes():
    html = '<input type="text" name="q" value="XSSCTX12345">'
    context = analyze_context(html, "XSSCTX12345", [])
    assert context == "attribute"

def test_analyze_javascript_context_inline():
    html = "<button onclick='show(\"XSSCTX12345\")'>Click</button>"
    context = analyze_context(html, "XSSCTX12345", [])
    assert context == "javascript"

def test_analyze_javascript_context_script_tag():
    html = "<script>var a = 'XSSCTX12345';</script>"
    context = analyze_context(html, "XSSCTX12345", [])
    assert context == "javascript"
