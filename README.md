# XSSense v1.0.0
**The intelligent, context-aware companion for reflected XSS testing.**

A production-grade, context-aware reflected XSS assistant for penetration testers.

## Demo
![XSSense CLI in action](file:///C:/Users/manoj/.gemini/antigravity/brain/d0858168-dc02-4606-a2d5-73b9f1fbbfa1/xssense_cli_demo_1777970929982.png)

## 🎯 Core Purpose

A focused CLI tool that:
1. Detects if user input is reflected in an HTTP response.
2. Identifies the exact context of reflection (HTML, Attribute, JavaScript).
3. Generates and tests context-specific XSS payloads concurrently.
4. Provides clear, explainable CLI output or strict JSON for pipeline integration.

> This tool is **NOT** a full vulnerability scanner. It is a highly optimized assistant for reflected XSS testing only.

---

## ⚠️ Security & Ethics Disclaimer

This tool is for **educational purposes and authorized security testing only**.  
Use this tool **only on systems you own or have explicit written permission to test**.  
The authors are not responsible for any misuse or damage caused by this tool.

---

## Installation

```bash
git clone <repository_url>
cd XSSense/contextxss

# Option 1: Install via pip (editable, for development)
pip install -e .

# Option 2: Install globally via pipx (recommended for end users)
pipx install .
```

After installation, restart your terminal to ensure the `xssense` command is on your PATH.

---

## Usage Examples

```bash
# Basic deep scan (default — tests all payloads for the detected context)
xssense scan --url "https://example.com/search?q=test"

# Quick scan (tests 5–10 prioritised payloads per context)
xssense scan --url "https://example.com/search?q=test" --mode quick

# JSON output for pipeline / CI integration
xssense scan --url "https://example.com/?q=test" --json

# Suppress non-finding output (quiet mode)
xssense scan --url "https://example.com/?q=test" --quiet

# STDIN support — pipe a list of URLs
cat urls.txt | xssense scan --stdin --quiet

# Proxy support (e.g., route through Burp Suite)
xssense scan --url "https://example.com/?q=test" --proxy "http://127.0.0.1:8080"

# Set a custom timeout
xssense scan --url "https://example.com/?q=test" --timeout 5
```

---

## Output Examples

### Human-Readable (default)
```
[*] Testing GET https://example.com/search?q=test
[+] Reflection detected!
Snippet: ...<body>XSSCTX12345</body>...
[+] Context identified as: Html

╭─────────────── Scan Summary ───────────────╮
│ Target: https://example.com/search?q=test  │
│ Context: Html                              │
│ Payloads Tested: 38                        │
╰────────────────────────────────────────────╯

  Payload                   │ Status     │ Confidence │ Explanation
 ═══════════════════════════╪════════════╪════════════╪══════════════
  <script>alert(1)</script> │ VULNERABLE │ High       │ Input reflected inside HTML body without escaping.

[!] XSS vulnerability confirmed!
```

### JSON (--json flag)
```json
{
    "url": "https://example.com/search?q=test",
    "reflected": true,
    "context": "html",
    "payloads": [
        {
            "value": "<script>alert(1)</script>",
            "success": true,
            "reason": "Payload reflected unescaped and is active in context",
            "confidence": "high"
        }
    ],
    "summary": {
        "vulnerable": true,
        "notes": "XSS vulnerability confirmed"
    }
}
```

---

## Benchmark Results

Benchmarks were run against six mock targets covering all three contexts (HTML, Attribute, JavaScript) in both safe and vulnerable configurations.

| Mode  | True Positives | False Positives | Avg Time |
|-------|:--------------:|:---------------:|:--------:|
| QUICK | 3 / 3          | 0               | ~25s     |
| DEEP  | 3 / 3          | 0               | ~65s     |

> Times include full concurrent payload evaluation with network round-trips to a local mock server.  
> Run yourself: `python benchmarks/benchmark.py` (from the `contextxss/` directory)

---

## CLI Flags Reference

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--url` | `-u` | — | Target URL with query parameter |
| `--mode` | — | `deep` | Payload mode: `quick` or `deep` |
| `--json` | — | `false` | Output strict JSON schema |
| `--quiet` | `-q` | `false` | Only print confirmed findings |
| `--verbose` | `-v` | `false` | Extra scan detail |
| `--stdin` | — | `false` | Read URLs from STDIN |
| `--proxy` | — | — | HTTP proxy URL |
| `--timeout` | `-t` | `10` | Per-request timeout (seconds) |
| `--method` | `-m` | `GET` | HTTP method: `GET` or `POST` |
| `--data` | `-d` | — | POST body data |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | Scan completed successfully (even if no vulnerability found) |
| `1`  | Error occurred (connection failure, invalid arguments, etc.) |

---

## Limitations

- **Reflected XSS only**: This tool detects reflected XSS exclusively. It does **not** scan for Stored XSS, DOM-based XSS (without server-side reflection), SQL Injection, or any other vulnerability class.
- **No crawling / spidering**: URLs must be supplied manually via `--url` or `--stdin`. The tool does not discover endpoints automatically.
- **Single-parameter injection**: The tool injects payloads into all query parameters simultaneously. Complex multi-parameter forms may require manual testing per-parameter.
