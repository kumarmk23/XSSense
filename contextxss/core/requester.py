import requests
import urllib3
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from contextxss.core.utils import inject_payload_into_data

# Suppress insecure request warnings for targets with bad SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_session():
    """Create a robust requests session."""
    session = requests.Session()
    session.trust_env = False
    
    # Standard browser headers to avoid being blocked by simple WAFs/CDNs
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    # Configure retry strategy for transient network errors
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def send_request(
    url: str,
    method: str = "GET",
    data: str = None,
    payload: str = "",
    timeout: int = 15,
    proxies: dict = None
):
    """
    Sends an HTTP request with the injected payload in the parameters.
    Handles GET and POST requests.
    Returns (status_code, headers, response_text, request_url, request_data).
    """
    try:
        session = get_session()
        
        if method == "GET":
            parsed_url = urlparse(url)
            query_params = parse_qsl(parsed_url.query, keep_blank_values=True)

            injected_params = [(k, payload) for k, v in query_params]
            new_query = urlencode(injected_params)

            request_url = urlunparse((
                parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                parsed_url.params, new_query, parsed_url.fragment
            ))

            response = session.get(request_url, timeout=timeout, proxies=proxies, verify=False, allow_redirects=True)
            return response.status_code, response.headers, response.text, request_url, None

        elif method == "POST":
            request_data = inject_payload_into_data(data, payload)

            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            response = session.post(
                url, data=request_data, headers=headers,
                timeout=timeout, proxies=proxies, verify=False, allow_redirects=True
            )
            return response.status_code, response.headers, response.text, url, request_data

        else:
            return None, None, None, url, data

    except requests.exceptions.RequestException as e:
        return None, None, str(e), url, data
