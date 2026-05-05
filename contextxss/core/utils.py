from urllib.parse import parse_qsl, urlencode

def inject_payload_into_query(query: str, payload: str) -> str:
    """Helper to inject payload into all query parameters."""
    query_params = parse_qsl(query, keep_blank_values=True)
    injected_params = [(k, payload) for k, v in query_params]
    return urlencode(injected_params)

def inject_payload_into_data(data: str, payload: str) -> str:
    """Helper to inject payload into form data string."""
    if not data:
        return data
    params = parse_qsl(data, keep_blank_values=True)
    injected_params = [(k, payload) for k, v in params]
    return urlencode(injected_params)
