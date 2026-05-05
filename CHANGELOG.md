# Changelog

All notable changes to this project will be documented in this file.

---

## [1.0.0] - 2026-05-05

### Added
- **Context-Aware XSS Detection**: Identifies the reflection context (HTML body,
  HTML attribute, JavaScript string) using BeautifulSoup4 DOM parsing with regex fallbacks.
- **97 Curated Payloads**: A hand-curated set of payloads covering standard tags,
  attribute breakout, event handlers, JS string breakout, framework injections
  (AngularJS, Vue), and mutation-based (mXSS) vectors.
- **Tiered Payload Modes**: `quick` mode (5–10 prioritised payloads) and `deep` mode
  (full payload set) controlled via `--mode`.
- **Concurrent Evaluation**: Up to 5 workers in parallel for speed, with early-exit
  on first High-confidence confirmed finding.
- **Strict JSON Schema**: `--json` flag outputs a fully structured, machine-readable
  JSON schema suitable for CI/CD pipeline integration.
- **Heuristic False-Positive Filter**: Context-aware checks verify that reflected
  payloads are genuinely active (contain breakout characters matching the enclosing
  quote or tag context) before flagging as vulnerable.
- **CLI Contract**: All flags (`--mode`, `--json`, `--quiet`, `--verbose`, `--stdin`,
  `--proxy`, `--timeout`) work consistently. Exit code `0` = success, `1` = error.
- **STDIN Support**: Pipe a list of URLs via `--stdin` for batch scanning.
- **Proxy Support**: Route traffic through any HTTP proxy (e.g., Burp Suite) via `--proxy`.
- **Benchmark Suite**: `benchmarks/benchmark.py` tests all six mock targets (HTML/Attribute/JS
  × safe/vulnerable). Results saved to `benchmarks/results.json`.
- **GitHub Actions CI**: Linting (`flake8`) and unit tests (`pytest`) run on every push.
- **13 Unit Tests**: Cover context analysis, reflection detection, payload selection, and
  strict JSON output schema compliance.

### Changed
- Package name set to `xssense` for clean `pip install` / `pipx install` installation.
- `evaluator.py` upgraded with heuristic accuracy checks to eliminate false positives
  on safe-but-reflected payloads.
- `mock_targets.py` fixed so `js_safe` endpoint correctly escapes `<` and `>` as
  `\x3c`/`\x3e`, making it a genuinely safe target.
- `formatter.py` table updated with `max_width=40` and `overflow="fold"` to prevent
  long payloads from breaking terminal table layout.
- All source files cleaned to pass `flake8` lint (E9/F63/F7/F82 critical rules).

### Benchmark Results (v1.0.0)

| Mode  | True Positives | False Positives | Avg Time |
|-------|:--------------:|:---------------:|:--------:|
| QUICK | 3 / 3          | 0               | ~25s     |
| DEEP  | 3 / 3          | 0               | ~65s     |

### Limitations
- Reflects XSS testing strictly. No stored XSS, DOM-based XSS (without server reflection),
  SQLi, or other vulnerability classes.
- No crawling or spidering. URLs must be supplied manually via `--url` or `--stdin`.
- Single-parameter injection mode; complex multi-parameter forms may need per-parameter testing.
