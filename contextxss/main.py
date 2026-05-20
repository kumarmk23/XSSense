from rich.console import Console
from urllib.parse import urlparse
from contextxss.core.requester import send_request
from contextxss.core.reflector import detect_reflection
from contextxss.core.analyzer import analyze_context
from contextxss.core.payload_engine import get_payloads
from contextxss.core.evaluator import evaluate_payloads
from contextxss.output.formatter import print_results

console = Console(stderr=True)
MARKER = "XSSCTX12345"


def validate_url_params(url: str, method: str, data: str, quiet: bool) -> bool:
    if method == "GET":
        parsed = urlparse(url)
        if not parsed.query:
            if not quiet:
                console.print(
                    f"[bold yellow][!] Warning: No parameters found in {url}. "
                    "A parameter is required.[/bold yellow]"
                )
            return False
    elif method == "POST":
        if not data:
            if not quiet:
                console.print(
                    f"[bold yellow][!] Warning: No data provided for {url} "
                    "POST request.[/bold yellow]"
                )
            return False
    return True


def run_scan(
    url: str, method: str = "GET", data: str = None,
    verbose: bool = False, timeout: int = 10, mode: str = "deep",
    proxy: str = None, quiet: bool = False, as_json: bool = False
) -> bool:
    if not validate_url_params(url, method, data, quiet):
        return False

    if not quiet and not as_json:
        console.print(f"[*] Testing {method} {url}")

    proxies = {"http": proxy, "https": proxy} if proxy else None

    # Step 1 & 2: Send initial request with marker
    status, headers, response_text, request_url, request_data = send_request(
        url, method, data, payload=MARKER, timeout=timeout, proxies=proxies
    )

    if status is None:
        if not quiet and not as_json:
            console.print(f"[bold red][-] Failed to connect to the target: {url}[/bold red]")
            console.print(f"[dim red][!] Error details: {response_text}[/dim red]")
        return False

    # Step 3: Detect Reflection
    is_reflected, positions = detect_reflection(response_text, MARKER)

    if not is_reflected:
        if not quiet and not as_json:
            console.print("[bold yellow][-] No reflection detected. Exiting.[/bold yellow]")
        if as_json:
            print_results(
                url, context=None, payloads=[], results=[],
                snippet="", as_json=True, quiet=quiet, is_reflected=False
            )
        return True

    # Extract snippet around reflection point
    pos = positions[0]
    start = max(0, pos - 30)
    end = min(len(response_text), pos + len(MARKER) + 30)
    snippet = response_text[start:end].replace('\n', ' ').strip()
    snippet = f"...{snippet}..."

    if not quiet and not as_json:
        console.print("[bold green][+] Reflection detected![/bold green]")
        console.print(f"[bold white]Snippet:[/bold white] [cyan]{snippet}[/cyan]")

    # Step 5a: Identify context
    context_type = analyze_context(response_text, MARKER, positions)

    if not quiet and not as_json:
        console.print(
            f"[bold green][+] Context identified as:[/bold green] "
            f"{context_type.capitalize()}"
        )

    # Step 5b: Generate payloads
    payloads = get_payloads(context_type, mode)
    if not quiet and not as_json and verbose:
        console.print(
            f"[*] Testing {len(payloads)} payloads for "
            f"{context_type} context in {mode} mode."
        )

    # Step 5c & 5d: Inject and evaluate
    results = evaluate_payloads(url, method, data, payloads, context_type, timeout, proxies)

    # Step 6: Print structured output
    print_results(
        url, context_type, payloads, results,
        snippet=snippet, as_json=as_json, quiet=quiet, is_reflected=True
    )
    return True
