import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from contextxss.core.utils import inject_payload_into_data


def send_request(
    url: str,
    method: str = "GET",
    data: str = None,
    payload: str = "",
    timeout: int = 10,
    proxies: dict = None
):
    """
    Sends an HTTP request with the injected payload in the parameters.
    Handles GET and POST requests.
    Returns (status_code, headers, response_text, request_url, request_data).
    """
    try:
        if method == "GET":
            parsed_url = urlparse(url)
            query_params = parse_qsl(parsed_url.query, keep_blank_values=True)

            injected_params = [(k, payload) for k, v in query_params]
            new_query = urlencode(injected_params)

            request_url = urlunparse((
                parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                parsed_url.params, new_query, parsed_url.fragment
            ))

            response = requests.get(request_url, timeout=timeout, proxies=proxies)
            return response.status_code, response.headers, response.text, request_url, None

        elif method == "POST":
            request_data = inject_payload_into_data(data, payload)

            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(
                url, data=request_data, headers=headers,
                timeout=timeout, proxies=proxies
            )
            return response.status_code, response.headers, response.text, url, request_data

        else:
            return None, None, None, url, data

    except requests.exceptions.RequestException as e:
        return None, None, str(e), url, data
