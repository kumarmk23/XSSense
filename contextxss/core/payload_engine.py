import json
import os

PAYLOADS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "payloads.json")

def get_payloads(context: str, mode: str = "deep") -> list[dict]:
    """
    Returns a list of payload dictionaries based on the specific context and mode.
    Mode can be 'quick' or 'deep'.
    """
    try:
        with open(PAYLOADS_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
        
    context_payloads = data.get(context, data.get("html", []))
    
    if mode == "quick":
        return [p for p in context_payloads if p.get("tier") == "quick"]
        
    return context_payloads
