import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from contextxss.output.formatter import print_results
from io import StringIO

def test_json_schema_vulnerable(capsys):
    url = "http://example.com/?q=test"
    context = "html"
    payloads = [{"payload": "<script>alert(1)</script>", "tier": "quick", "confidence": "High", "explanation": "Basic XSS"}]
    results = [{"payload": "<script>alert(1)</script>", "success": True, "reason": "Reflected", "confidence": "High", "explanation": "Basic XSS"}]
    
    print_results(url, context, payloads, results, as_json=True, is_reflected=True)
    
    captured = capsys.readouterr()
    output = captured.out
    
    data = json.loads(output)
    
    assert data["url"] == url
    assert data["reflected"] is True
    assert data["context"] == "html"
    assert isinstance(data["payloads"], list)
    assert len(data["payloads"]) == 1
    assert data["payloads"][0]["value"] == "<script>alert(1)</script>"
    assert data["payloads"][0]["success"] is True
    assert data["payloads"][0]["reason"] == "Reflected"
    assert data["payloads"][0]["confidence"] == "high"
    
    assert isinstance(data["summary"], dict)
    assert data["summary"]["vulnerable"] is True

def test_json_schema_no_reflection(capsys):
    url = "http://example.com/?q=test"
    
    print_results(url, context=None, payloads=[], results=[], as_json=True, is_reflected=False)
    
    captured = capsys.readouterr()
    output = captured.out
    
    data = json.loads(output)
    
    assert data["url"] == url
    assert data["reflected"] is False
    assert data["context"] == "null"
    assert isinstance(data["payloads"], list)
    assert len(data["payloads"]) == 0
    
    assert isinstance(data["summary"], dict)
    assert data["summary"]["vulnerable"] is False
