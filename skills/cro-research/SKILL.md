---
name: cro-research
description: >
  Research published A/B tests and maintain the source-backed CRO evidence
  database. Use for /cro research, "find evidence for this finding", "CRO case
  studies", "research conversion tests", "add test evidence", "update evidence
  database", or a scheduled weekly CRO research run.
argument-hint: "[topic | weekly | find <finding>] [--page-type TYPE --element ELEMENT --principle TAG]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash, WebFetch, WebSearch
---

# CRO Research

Build evidence, not a list of impressive percentages. No `source_url` means no
record. External experiments can support a hypothesis; they do not prove a
finding about a client's page or promise the same lift. Work in this session;
do not start helper agents.

Resolve `CRO_SCRIPTS` once with
`cd "${CLAUDE_SKILL_DIR}/../cro/scripts" && pwd`.
Write the absolute path literally in every command. Run scripts through
`"<CRO_SCRIPTS>/cro-py" evidence.py ...`.
The database is `${CLAUDE_SKILL_DIR}/../cro/evidence`.

Read `../cro/evidence/SCHEMA.md`, `references/sources.md`, and
`../cro/references/business-types.md` before adding anything. The last file is
the only business-type vocabulary. Do not duplicate it in this skill.

## Choose the mode

- **Find:** An audit, report or slide needs evidence for a specific finding.
  Follow Find evidence below. This mode does not need database writes.
- **Research:** A topic or missing match needs new published experiments.
  Follow the research workflow and ask permission before shared repository writes
  if the user asked only for citations.
- **Weekly:** Refresh sources and grow the database using the weekly checklist.
  Keep a dated run log in the user's output workspace, not in the skill pack.

## Find evidence for this finding

1. Keep the client's own evidence first: quote, selector, screenshot or measured
   number. State the observed problem separately from the proposed explanation.
2. Identify `page_type`, `element` and principle. Search the local database:

   ```bash
   "<CRO_SCRIPTS>/cro-py" evidence.py search --page-type product --element reviews --principle social-proof --min-strength B
   "<CRO_SCRIPTS>/cro-py" evidence.py search --page-type product --json
   ```

3. Filters are ANDed. If no match, remove element, then principle; try a related
   page type or business type. Never silently describe a broad match as exact.
4. Read complete JSON records, including notes and verification details. Prefer
   the same business model, conversion step, device, intervention and metric.
   Consider relevant losses and flat results, not just supporting wins.
5. Use 1-3 relevant sources. Name the company, tested change, exact metric,
   reported result, strength, verification status and important limits. Cite both
   the stable database ID and a clickable original source link.
6. Report form:

   ```text
   Site evidence: [quote / element / screenshot / measured number].
   External evidence: [Company] reported [result on exact metric] after
   [control vs variant] ([linked source], record [id], strength [A/B/C],
   [verified/unverified]). [Context difference or design limitation].
   Implication: This supports investigating [hypothesis], not a promised lift.
   ```

   On slides, keep company, metric and result in the body, add `[id]` and a
   clickable source in the footnote, and put grade, verification and caveats in
   speaker notes. Do not truncate the metric to just a percent or hide a loss.
7. No credible match: say "No matching published test found". Cite relevant
   qualitative research as such, or recommend obtaining user evidence. Do not
   retrofit an unrelated win. Never cite legacy idea lists as verified tests.
8. Evidence does not override test readiness. Audits and plans must follow
   `../cro/references/test-readiness.md`; NOT_TESTABLE sites get usability research
   and measured fixes, not an A/B backlog based on outside percentages.

## Research workflow

### 1. Define the gap and search

Write the target business, page, element, principle and metric. Run `search` and
`stats` first. Read `references/sources.md` for source quality and query patterns.
Search at least one primary source and explicitly search for losses, null
results and conflicting evidence. Use available web search or fetch publisher
indexes and sitemaps if search is unavailable. Log unavailable search tools.

### 2. Read the source, not the snippet

Fetch the full source and keep its HTML and metadata in the output workspace:

```bash
"<CRO_SCRIPTS>/cro-py" fetch_page.py <source-url> --output <workspace>/source.html --json
```

A bot wall, 404 or JavaScript shell is not a loaded case study. Do not bypass
private-address protections or invent a working URL. If necessary inspect a
browser screenshot and explain why the HTTP verifier cannot confirm it. Skip an
unreachable source for new seed additions; log it as a research lead instead.

### 3. Extract structured JSON

- Follow SCHEMA.md. Write one record per tested comparison, not per metric.
- Describe control and variant from the actual article and screenshots. Record
  all bundled changes; do not attribute a redesign result to one button.
- Use the tested company's name, not the agency. Classify the primary business
  from its conversion action and note ambiguous or secondary models.
- Copy the exact metric, signed relative lift and a short supporting quote.
  Distinguish percentage points, relative percentages, projected revenue,
  segment results, signup-page visits and completed sales.
- Capture published samples, conversions, significance, duration and publication
  date. Use null when not published; do not infer exact arm counts or fabricate
  dates from a crawl timestamp. Preserve rounded numbers with notes.
- Grade A only when sample and significance are published; B for a numeric lift
  with incomplete stats; C for qualitative outcomes. Grade is completeness, not
  proof of a well-designed experiment. Explain short tests, peeking and ambiguity.
- Mark `research_type: "research"` for non-A/B studies such as Baymard. Never
  manufacture a control, winner, lift or randomization that the source lacks.
- No numeric result: leave `relative_lift_pct` null. Flat/inconclusive is not 0%
  and not proof of equivalence. Losses are useful records, not extraction errors.

### 4. Dedupe, add and verify

Search by company, page and element; inspect records from the same source.
Check syndicated articles and redirected URLs for the same experiment. The CLI
catches matching URL+change text, not paraphrases of an existing experiment.

```bash
"<CRO_SCRIPTS>/cro-py" evidence.py validate
"<CRO_SCRIPTS>/cro-py" evidence.py add <workspace>/candidate.json
"<CRO_SCRIPTS>/cro-py" evidence.py verify <id>
```

`add` refuses duplicate IDs/comparisons and resets verification to unverified.
`verify` uses the shared safe HTTP fetch logic, then checks company, percent and
supporting quote in visible text. Read `verification_details`, not only the exit
code. Unpublished numbers must stay unverified even if the qualitative quote is
confirmed. Never manually upgrade verification because an outcome seems plausible.
For a mismatched quote or formatting error, correct the record against the source
and verify again. Do not alter the result just to make the verifier pass.

### 5. Render and self-review

```bash
"<CRO_SCRIPTS>/cro-py" evidence.py validate
"<CRO_SCRIPTS>/cro-py" evidence.py export-md
"<CRO_SCRIPTS>/cro-py" evidence.py stats
```

Open CATALOG.md and inspect the new records. Good evidence means a reader can
follow the source link, identify exactly what changed, find the recorded outcome
in context, understand what is missing, and see why the case is relevant without
being promised the same result. The script renders deterministic Markdown; do
not hand-edit the catalog.

## Weekly run checklist

- [ ] Record run date, owner, target gaps and initial `stats` in a workspace log.
- [ ] Validate the existing database before editing. Stop on corruption.
- [ ] Reverify existing records with `verify all`; log unreachable or changed
  sources and downgrade stale claims honestly. Never silently delete failures.
- [ ] Search source indexes and primary blogs for new experiments since the last
  run, plus targeted loss/null queries. Log queries and screened candidates.
- [ ] Extract only source-backed comparisons, manually dedupe, add and verify.
  No addition quota is worth inventing a number. Zero credible additions is valid.
- [ ] Regenerate catalog, validate again and measure counts by strength,
  verification and outcome. Distinguish records from independent studies.
- [ ] Review every new metric, quote, control/variant, business type and grade.
- [ ] Record added IDs, updated IDs, rejected leads with reasons, commands,
  counts, fetch failures, publication bias and next gaps in the workspace log.
- [ ] If authorized, hand changes to the repository owner's normal review flow.
  No automatic commit, push, deployment or scheduler installation.

This checklist is ready for a later scheduler; it does not install one. Schedule
one writer at a time and give it a workspace, source access and explicit write
permission. A source outage is a failed refresh to report, not an excuse to mark
records verified from cache.

## Final self-review

- Does every record have a reachable source, exact supporting quote and honest
  verification? Did failed rechecks clear a previous verified state?
- Are company, comparison, population and metric faithful to the publication?
- Are unknown statistics null, lower bounds labeled, and rounded 100% qualified?
- Have I included conflicting, loss and inconclusive evidence in the search?
- Are new records independent comparisons rather than duplicate metrics?
- Is the catalog regenerated and are reported counts freshly measured?
- Does each client finding retain its own site evidence and linked citations?
- Have I avoided jargon, unsupported causal explanations and promised lifts?
