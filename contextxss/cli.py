import typer
import sys
from typing import Optional
from contextxss.main import run_scan
from rich.console import Console

app = typer.Typer(help="XSSense: Context-aware reflected XSS assistant")
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


@app.command()
def scan(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Target URL with parameter to test"),
    stdin: bool = typer.Option(False, "--stdin", help="Read URLs from STDIN"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP Method (GET/POST)"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Data for POST requests"),
    mode: str = typer.Option("deep", "--mode", help="Payload mode: 'quick' or 'deep'"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="HTTP proxy (e.g., http://127.0.0.1:8080)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only show confirmed findings"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout for HTTP requests in seconds"),
):
    """
    Scan a URL for reflected XSS vulnerabilities contextually.
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
