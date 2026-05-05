from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import json

console = Console()


def print_results(
    url: str, context: str, payloads: list[dict], results: list[dict],
    snippet: str = "", as_json: bool = False,
    quiet: bool = False, is_reflected: bool = True
):
    """
    Prints the final results using rich formatting or JSON.
    """
    if as_json:
        vuln_found = any(r.get("success", False) for r in results)

        json_payloads = []
        for res in results:
            if quiet and not res["success"]:
                continue
            json_payloads.append({
                "value": res["payload"],
                "success": res["success"],
                "reason": res["reason"],
                "confidence": res["confidence"].lower()
            })

        json_out = {
            "url": url,
            "reflected": is_reflected,
            "context": context if context else "null",
            "payloads": json_payloads,
            "summary": {
                "vulnerable": vuln_found,
                "notes": (
                    "XSS vulnerability confirmed" if vuln_found
                    else "No definitive XSS vulnerabilities triggered"
                )
            }
        }
        print(json.dumps(json_out, indent=4))
        return

    if not quiet:
        console.print("\n")
        summary_text = (
            f"[bold white]Target:[/bold white] {url}\n"
            f"[bold white]Context:[/bold white] [bold cyan]{context.capitalize()}[/bold cyan]\n"
            f"[bold white]Payloads Tested:[/bold white] {len(payloads)}"
        )
        console.print(Panel(
            summary_text,
            title="[bold green]Scan Summary[/bold green]",
            box=box.ROUNDED
        ))

    table = Table(
        title="Payload Evaluation Results",
        box=box.MINIMAL_DOUBLE_HEAD,
        show_lines=True
    )
    table.add_column("Payload", style="cyan", overflow="fold", max_width=40)
    table.add_column("Status", style="bold", justify="center", width=12)
    table.add_column("Confidence", style="magenta", width=12)
    table.add_column("Explanation", style="white", overflow="fold")

    vuln_found = False

    for res in results:
        if quiet and not res["success"]:
            continue

        payload_str = res["payload"]
        if res["success"]:
            status_str = "[green]VULNERABLE[/green]"
            vuln_found = True
        else:
            status_str = "[red]FAILED[/red]"

        conf_color = (
            'red' if res['confidence'].lower() == 'high'
            else 'yellow' if res['confidence'].lower() == 'medium'
            else 'white'
        )
        conf = f"[{conf_color}]{res['confidence']}[/]"

        explanation = res["explanation"]
        table.add_row(payload_str, status_str, conf, explanation)

    if not quiet or vuln_found:
        console.print(table)

    if not quiet:
        if vuln_found:
            console.print("[bold green][!] XSS vulnerability confirmed![/bold green]")
        else:
            console.print(
                "[bold yellow][*] No definitive XSS vulnerabilities were "
                "successfully triggered with the tested payloads.[/bold yellow]"
            )
