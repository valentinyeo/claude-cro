# Claude CRO — Conversion Rate Optimization for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-blueviolet.svg)](https://claude.ai)

A comprehensive CRO skill package for Claude Code that audits websites for conversion optimization opportunities, generates A/B test hypotheses, and builds prioritized optimization roadmaps.

## Features

- **12 specialized sub-skills** covering every aspect of CRO
- **6 parallel subagents** for full-site audits (UX, copy, tracking, visual, performance, trust)
- **CRO Health Score (0-100)** with weighted category scoring
- **Industry detection** for SaaS, E-commerce, Lead Gen, Subscription, Local Service, and Agency sites
- **ICE-scored A/B test hypotheses** with structured hypothesis templates
- **SSRF-protected scripts** for safe web page fetching and analysis
- **Funnel analysis** across multi-page conversion flows
- **Competitor benchmarking** with side-by-side comparison

## Quick Start

```bash
git clone https://github.com/valentinyeo/claude-cro.git
cd claude-cro
./install.sh
```

Then open Claude Code and run:

```
/cro audit https://example.com
```

## Commands

| Command | Description |
|---------|-------------|
| `/cro audit <url>` | Full website conversion audit with parallel agents |
| `/cro page <url>` | Single page conversion deep-dive |
| `/cro funnel <url1> <url2> ...` | Multi-step funnel mapping and drop-off analysis |
| `/cro test <url>` | A/B test hypothesis generation (ICE framework) |
| `/cro copy <url>` | Conversion copywriting analysis |
| `/cro ux <url>` | UX heuristic evaluation (Nielsen's 10 heuristics) |
| `/cro forms <url>` | Form optimization analysis |
| `/cro ecommerce <url>` | E-commerce CRO (PDP, cart, checkout) |
| `/cro trust <url>` | Trust signals and social proof audit |
| `/cro tracking <url>` | Analytics and tracking setup validation |
| `/cro benchmark <url> <competitor>` | Competitor conversion comparison |
| `/cro plan <url>` | CRO strategy and 90-day roadmap |

## CRO Health Score

Every audit produces a CRO Health Score from 0 to 100, calculated from weighted category scores:

| Category | Weight |
|----------|--------|
| UX | 25% |
| Copy | 20% |
| Trust | 15% |
| Visual Hierarchy | 15% |
| Forms | 10% |
| Performance | 10% |
| Tracking | 5% |

### Score Ratings

| Score | Rating | Interpretation |
|-------|--------|----------------|
| 90-100 | Exceptional | Best-in-class conversion optimization |
| 70-89 | Strong | Solid foundation with clear opportunities |
| 50-69 | Moderate | Significant gaps impacting conversion |
| 30-49 | Weak | Major conversion barriers present |
| 0-29 | Critical | Fundamental issues blocking conversions |

## Architecture

Claude CRO uses a three-layer architecture:

```
Orchestrator (cro/SKILL.md)
    |
    +-- Routes /cro <subcommand> to the right sub-skill
    |
    +-- For /cro audit: spawns 6 parallel subagents
    |       |-- cro-ux         (UX heuristics)
    |       |-- cro-copy       (conversion copywriting)
    |       |-- cro-tracking   (analytics validation)
    |       |-- cro-visual     (visual hierarchy)
    |       |-- cro-performance (page speed)
    |       +-- cro-trust      (trust signals)
    |
    +-- Collects results, calculates weighted score, generates report
```

Sub-skills and agents load reference files on-demand:

- `conversion-benchmarks.md` — Industry conversion rate data
- `psychology-principles.md` — Cialdini's principles, cognitive biases, Fogg model
- `testing-framework.md` — ICE scoring, sample size guidance, hypothesis templates
- `ux-heuristics.md` — Nielsen's heuristics with conversion focus
- `quality-gates.md` — Minimum requirements and pass/fail criteria

## Industry Detection

The orchestrator automatically detects the website's business type to apply industry-specific benchmarks and evaluation criteria:

| Business Type | Detection Signals |
|---------------|-------------------|
| SaaS | /pricing, /features, "free trial", "sign up", "book a demo" |
| E-commerce | /products, /cart, "add to cart", Product schema, price elements |
| Lead Gen | Contact form, "get a quote", "book a call", phone number |
| Subscription | /plans, "subscribe", recurring pricing, membership tiers |
| Local Service | Street address, phone number, Google Maps embed, LocalBusiness schema |
| Agency/B2B | /case-studies, /portfolio, client logos, team section |

## Python Scripts

Four utility scripts support the analysis skills:

| Script | Purpose |
|--------|---------|
| `fetch_page.py` | Fetch web pages with SSRF prevention, redirect following, timeout |
| `parse_cro.py` | Extract CTAs, forms, trust signals, tracking, headlines, schema from HTML |
| `capture_screenshot.py` | Take desktop and mobile screenshots via Playwright (headless) |
| `analyze_funnel.py` | Analyze multi-page funnels for transitions, leaks, and friction |

All scripts include SSRF protection that blocks requests to private/internal IP ranges.

## Requirements

- **Python 3.9+**
- **Claude Code** (the CLI)
- **Playwright** (optional, for screenshot capture)

Python packages (installed automatically by `install.sh`):

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
playwright>=1.40.0
```

## Directory Structure

```
claude-cro/
|-- cro/
|   |-- SKILL.md                  # Main orchestrator
|   +-- references/
|       |-- conversion-benchmarks.md
|       |-- psychology-principles.md
|       |-- testing-framework.md
|       |-- ux-heuristics.md
|       +-- quality-gates.md
|-- skills/
|   |-- cro-audit/
|   |-- cro-page/
|   |-- cro-funnel/
|   |-- cro-copy/
|   |-- cro-ux/
|   |-- cro-forms/
|   |-- cro-ecommerce/
|   |-- cro-trust/
|   |-- cro-tracking/
|   |-- cro-testing/
|   |-- cro-benchmark/
|   +-- cro-plan/
|-- agents/
|   |-- cro-ux.md
|   |-- cro-copy.md
|   |-- cro-tracking.md
|   |-- cro-visual.md
|   |-- cro-performance.md
|   +-- cro-trust.md
|-- scripts/
|   |-- fetch_page.py
|   |-- parse_cro.py
|   |-- capture_screenshot.py
|   +-- analyze_funnel.py
|-- hooks/
|   +-- validate-cro-report.sh
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- COMMANDS.md
|   |-- INSTALLATION.md
|   +-- TROUBLESHOOTING.md
|-- install.sh
|-- install.ps1
|-- uninstall.sh
|-- requirements.txt
|-- LICENSE
|-- CHANGELOG.md
+-- README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Make your changes and test them
4. Commit: `git commit -m "Add my improvement"`
5. Push: `git push origin feature/my-improvement`
6. Open a pull request

When contributing new sub-skills or agents, follow the existing SKILL.md format and include:
- Frontmatter with name, description, and trigger keywords
- Structured analysis sections with evaluation criteria
- Scoring methodology with weights
- Output format template
- Cross-references to related skills and reference files

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

**Valentin Yeo** — [GitHub](https://github.com/valentinyeo)

---

Built for [Claude Code](https://claude.ai) by Anthropic.
