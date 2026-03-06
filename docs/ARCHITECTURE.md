# Architecture

Claude CRO is designed as a three-layer skill architecture optimized for parallel
execution, lazy resource loading, and modular extensibility.

## Three-Layer Design

```
Layer 1: Orchestrator
    skills/cro/SKILL.md
    |
    |-- Parses /cro <subcommand> and routes to the correct sub-skill
    |-- Manages full audit workflow (fetch, detect, delegate, collect, score, report)
    |-- Owns the CRO Health Score calculation
    |-- Loads reference files on-demand
    |
Layer 2: Sub-Skills (12)
    skills/cro-*/SKILL.md
    |
    |-- Each handles a specific CRO domain (copy, UX, forms, etc.)
    |-- Contains its own evaluation criteria, scoring, and output format
    |-- Can be invoked independently or as part of a full audit
    |-- References Python scripts for data extraction
    |
Layer 3: Agents (6)
    agents/cro-*.md
    |
    |-- Lightweight evaluation agents spawned during /cro audit
    |-- Run in parallel for speed
    |-- Each receives page HTML + business type context
    |-- Returns: category score, findings, recommendations, test hypothesis
```

## Routing Logic

When a user types `/cro <subcommand> <url>`, the orchestrator:

1. Parses the subcommand from the user input
2. Maps it to the corresponding sub-skill directory:

```
/cro audit     -> Full audit workflow (Layer 1 orchestration)
/cro page      -> skills/cro-page/SKILL.md
/cro funnel    -> skills/cro-funnel/SKILL.md
/cro test      -> skills/cro-testing/SKILL.md
/cro copy      -> skills/cro-copy/SKILL.md
/cro ux        -> skills/cro-ux/SKILL.md
/cro forms     -> skills/cro-forms/SKILL.md
/cro ecommerce -> skills/cro-ecommerce/SKILL.md
/cro trust     -> skills/cro-trust/SKILL.md
/cro tracking  -> skills/cro-tracking/SKILL.md
/cro benchmark -> skills/cro-benchmark/SKILL.md
/cro plan      -> skills/cro-plan/SKILL.md
```

3. Loads the sub-skill's SKILL.md instructions
4. Executes the analysis process defined in the sub-skill

## Parallel Agent Delegation (`/cro audit`)

The full audit command is the most complex workflow. It spawns 6 subagents
that run in parallel to minimize total analysis time.

### Workflow

```
1. Fetch page HTML
   |
2. Detect business type (SaaS, E-commerce, Lead Gen, etc.)
   |
3. Spawn 6 subagents in parallel
   |   Each receives:
   |   - Full page HTML
   |   - Detected business type
   |   - Evaluation brief from its agent definition
   |
   +-- cro-ux agent         -> UX score + findings
   +-- cro-copy agent       -> Copy score + findings
   +-- cro-tracking agent   -> Tracking score + findings
   +-- cro-visual agent     -> Visual score + findings
   +-- cro-performance agent -> Performance score + findings
   +-- cro-trust agent      -> Trust score + findings
   |
4. Collect all 6 results
   |
5. Calculate CRO Health Score (weighted composite)
   |
6. Merge findings, sort by priority
   |
7. Generate unified report
```

### Why Parallel?

Each subagent evaluates an independent domain. There are no dependencies
between them — the UX analysis does not need copy results, and vice versa.
Running them in parallel means a full audit completes in roughly the time of
the slowest single agent, rather than the sum of all six.

### Agent Communication

Agents communicate through a simple protocol:

**Input:** Raw HTML string + business type string + evaluation instructions
**Output:** Structured result with:
- `score` (0-100)
- `findings` (list of {description, priority, section, recommendation})
- `top_3_recommendations` (prioritized action items)
- `test_hypothesis` (optional A/B test suggestion)

## Reference File Lazy Loading

Reference files are NOT loaded at startup. They are loaded on-demand by
the sub-skill or agent that needs them.

```
Reference File                     Loaded By
----------------------------------  ----------------------------------
conversion-benchmarks.md           cro-performance agent, cro-funnel
psychology-principles.md           cro-copy agent, cro-trust agent
testing-framework.md               cro-testing sub-skill
ux-heuristics.md                   cro-ux agent
quality-gates.md                   cro-tracking agent, cro-visual agent
```

### Why Lazy Loading?

1. **Token efficiency** — reference files are large (1,000-3,000 tokens each).
   Loading all 5 for every command wastes context window.
2. **Relevance** — a `/cro copy` analysis does not need UX heuristics.
3. **Scalability** — as more references are added, startup cost does not grow.

## Scoring Methodology

### CRO Health Score (Full Audit)

The composite score uses a weighted average across categories:

```
Score = (UX * 0.25) + (Copy * 0.20) + (Trust * 0.15) + (Visual * 0.15)
      + (Forms * 0.10) + (Performance * 0.10) + (Tracking * 0.05)
```

### Weight Justification

| Category | Weight | Rationale |
|----------|--------|-----------|
| UX | 25% | Navigation, layout, and interaction quality have the broadest impact on all conversions |
| Copy | 20% | Persuasion, clarity, and value proposition directly drive conversion decisions |
| Trust | 15% | Trust is a prerequisite for conversion — without it, nothing else matters |
| Visual | 15% | Visual hierarchy guides attention to conversion elements (CTAs, forms) |
| Forms | 10% | Critical but only relevant when forms exist; narrower scope |
| Performance | 10% | Speed impacts conversion but is a technical factor, not a persuasion factor |
| Tracking | 5% | Does not directly affect conversion, but is essential for measurement |

### Sub-Skill Scores

Each sub-skill (page, copy, funnel, etc.) has its own scoring methodology
with different section weights. These are documented within each sub-skill's
SKILL.md file.

## Industry Detection Algorithm

The orchestrator analyzes the fetched page content to classify the business type:

```
1. Extract all links, text content, and schema markup
2. Count signal matches for each business type
3. Score each type based on signal frequency and strength
4. Select the type with the highest score as primary
5. If a second type has >50% of the primary's score, note it as secondary
```

Signal matching is weighted:

- **Strong signals** (2 points): schema markup (Product, LocalBusiness), pricing
  page links, cart/checkout elements
- **Medium signals** (1 point): CTA text patterns, page structure, section types
- **Weak signals** (0.5 points): generic terms that appear across types

## Script Support

Python scripts handle data extraction tasks that are better suited to
programmatic processing than natural language analysis.

### Data Flow

```
URL input
    |
    v
fetch_page.py  -----> Raw HTML + metadata
    |                      |
    v                      v
parse_cro.py  ------> Structured CRO elements (CTAs, forms, trust, etc.)
    |                      |
    v                      v
Sub-skill/Agent -----> Analysis + scoring + recommendations
    |
    v
capture_screenshot.py (optional) -> Visual analysis input
    |
    v
analyze_funnel.py (for /cro funnel) -> Multi-page transition analysis
```

### SSRF Prevention

All scripts that make outbound HTTP requests include SSRF (Server-Side
Request Forgery) protection:

1. Parse the hostname from the URL
2. Resolve DNS to get the IP address
3. Check the IP against a blocklist of private/reserved ranges
4. Block the request if the IP is private (10.x, 172.16-31.x, 192.168.x, 127.x, etc.)
5. After following redirects, re-check the final URL's resolved IP

This prevents the scripts from being used to probe internal networks.
