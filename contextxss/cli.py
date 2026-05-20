import typer
import sys
from typing import Optional
from contextxss.main import run_scan
from rich.console import Console

app = typer.Typer(
    help="XSSense: Context-aware reflected XSS assistant",
    rich_markup_mode="rich",
)
console = Console(stderr=True)


BANNER = """
[bold cyan]
  ██╗  ██╗███████╗███████╗███████╗███╗   ██╗███████╗███████╗
  ╚██╗██╔╝██╔════╝██╔════╝██╔════╝████╗  ██║██╔════╝██╔════╝
   ╚███╔╝ ███████╗███████╗█████╗  ██╔██╗ ██║███████╗█████╗  
   ██╔██╗ ╚════██║╚════██║██╔══╝  ██║╚██╗██║╚════██║██╔══╝  
  ██╔╝ ██╗███████║███████║███████╗██║ ╚████║███████║███████╗
  ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝
[/bold cyan]
[dim white]────────────────────────────────────────────────────────────[/dim white]
[bold white]  v1.0.0 | Intelligent Context-Aware Reflected XSS Assistant[/bold white]
[dim white]────────────────────────────────────────────────────────────[/dim white]
"""


def print_banner():
    console.print(BANNER)


@app.callback()
def callback():
    """
    XSSense: Context-aware reflected XSS assistant
    """
    pass


@app.command(
    epilog="""
[bold cyan]------------------  SCAN MODES  ------------------[/bold cyan]

  [bold yellow]quick[/bold yellow]   Fast triage - runs only high-confidence, low-noise payloads.
          Best for rapid reconnaissance across many URLs.
          Payload count: ~10 per context.

  [bold yellow]deep[/bold yellow]    Full audit - runs the complete payload library including
          WAF-bypass variants, edge-case encodings, and multi-context
          probes. Best for thorough testing of a single target.
          Payload count: up to 38 per context.  [bold green](default)[/bold green]

[bold cyan]-------------  XSS CONTEXT TYPES DETECTED  -------------[/bold cyan]

  XSSense automatically identifies the reflection context and selects
  matching payloads. Supported contexts:

  [bold magenta]html[/bold magenta]          Reflection lands in raw HTML body.
                Payloads use <script>, <svg/onload>, <img onerror>, etc.

  [bold magenta]attribute[/bold magenta]     Reflection is inside an HTML tag attribute.
                Payloads break out of quote context (" onmouseover=, etc.)

  [bold magenta]javascript[/bold magenta]    Reflection is inside a JS string or block.
                Payloads escape the string (';alert(1)//, etc.)

[bold cyan]---------------  OUTPUT FORMATS  ----------------[/bold cyan]

  [bold green]default[/bold green]     Rich formatted tables printed to the terminal.

  [bold green]--json[/bold green]      Machine-readable JSON printed to stdout.
              Pipe to a file:  xssense scan --url <URL> --json > out.json

  [bold green]--quiet[/bold green]     Suppresses all output except confirmed XSS findings.
              Ideal for silent scripting and CI pipelines.

[bold cyan]-----------------  EXAMPLES  -----------------[/bold cyan]

  # Quick scan
  xssense scan --url "https://example.com/search?q=test" --mode quick

  # Deep scan with verbose output
  xssense scan --url "https://example.com/search?q=test" --mode deep --verbose

  # POST request scan
  xssense scan --url "https://example.com/submit" --method POST --data "input=test"

  # JSON output piped to file
  xssense scan --url "https://example.com/search?q=test" --json > results.json

  # Scan multiple URLs from a file
  cat urls.txt | xssense scan --stdin

  # Route through Burp Suite proxy
  xssense scan --url "https://example.com/search?q=test" --proxy http://127.0.0.1:8080
"""
)
def scan(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Target URL with at least one query parameter to test"),
    stdin: bool = typer.Option(False, "--stdin", help="Read target URLs line-by-line from STDIN"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method to use: GET (default) or POST"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="POST body data (e.g. 'user=test&pass=x')"),
    mode: str = typer.Option(
        "deep",
        "--mode",
        help=(
            "Payload scan mode:\n\n"
            "  quick — high-confidence payloads only (~10 per context), fast triage\n\n"
            "  deep  — full payload library (up to 38 per context), thorough audit [default]"
        ),
    ),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="HTTP/S proxy URL (e.g. http://127.0.0.1:8080 for Burp Suite)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print payload count, context details, and per-request info"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all output except confirmed XSS findings"),
    json: bool = typer.Option(False, "--json", help="Output results as machine-readable JSON (to stdout)"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Per-request HTTP timeout in seconds (default: 10)"),
):
    """
    Scan a URL for context-aware reflected XSS vulnerabilities.

    XSSense injects a marker into every parameter, detects where it
    is reflected in the response, identifies the XSS context
    (html / attribute / javascript), and fires matching payloads.
    """
    urls_to_scan = []

    if url:
        urls_to_scan.append(url)

    if stdin:
        if not sys.stdin.isatty():
            for line in sys.stdin:
                line = line.strip()
                if line:
                    urls_to_scan.append(line)

    if not urls_to_scan:
        console.print("[bold red]Error: No URLs provided. Use --url or --stdin.[/bold red]")
        raise typer.Exit(code=1)

    if not quiet and not json:
        print_banner()

    try:
        for target in urls_to_scan:
            if verbose and not quiet and not json:
                console.print(f"[bold cyan]Starting XSSense scan on:[/bold cyan] {target}")

            success = run_scan(
                url=target,
                method=method.upper(),
                data=data,
                verbose=verbose,
                timeout=timeout,
                mode=mode.lower(),
                proxy=proxy,
                quiet=quiet,
                as_json=json
            )
            if not success:
                raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
