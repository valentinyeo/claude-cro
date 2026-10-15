---
name: cro-program
description: >
  Run a signed client's ongoing CRO program: baseline and test readiness,
  research, experiment backlog, building and QA of tests, monitoring, honest
  result calls, learnings, and regression checks after site releases. Use for
  /cro program, "start the client program", "log this test result", "what's
  running for <client>", "monthly CRO report".
argument-hint: "<init|plan|launch|result|board|report|check> [client] [...]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash, WebFetch, Agent
---

# Client CRO Program

One private folder per client, `cro-program-<client>/`, holds the program.
**It contains client data: never put it inside the public skill repo or in a
public evidence record.** Learnings may go to a private evidence store only,
anonymised, if the client contract allows it.

`CRO_SCRIPTS` = absolute path from `cd "${CLAUDE_SKILL_DIR}/../cro/scripts" && pwd`.
All program state changes go through `"<CRO_SCRIPTS>/cro-py" program.py --dir <folder> ...`
so the numbers and history stay consistent. Never compute results by hand.

## init: onboarding a new client

1. Get real numbers from the client (analytics or store admin), not estimates:
   monthly conversions on the main goal, conversion rate or visitors, average
   order value, main traffic sources, the testing tool they have (or will buy).
2. `program.py init <client> <site> --conversions N --cvr X` records the
   baseline and readiness verdict.
3. Run `/cro audit <site> --depth deep --conversions N --cvr X` into the
   program folder (`audit/`).
4. `capture.py` each key page into `baselines/<page>/` and
   `program.py snapshot <page> baselines/<page>/elements.json` for each, so
   later releases can be checked against them.
5. Write `PROGRAM.md`: goals, the readiness verdict in plain words, method
   (A/B program, big swings + research, or research + fixes), cadence, and who
   approves launches.

## plan: build the backlog (monthly)

- Sources, in order of trust: persona friction and usability findings, client
  analytics (drop-off pages), customer voice (polls, reviews, support tickets),
  the audit, then published tests from the evidence database.
- READY: ICE-rank ideas; `program.py add <id> "<title>" --page P --mde <expected lift>`
  for the next 3-5. The script prints the needed sample and weeks; drop or
  enlarge any test that needs more than 8 weeks.
- LIMITED: at most one or two big-swing tests at a time, sized for 20-30%.
  Everything else ships as a research-backed fix.
- NOT_TESTABLE: no tests. Log fixes with `add` + `status shipped`, and measure
  them against the baseline (before/after, 4 weeks each, note campaigns).

## launch: per experiment

1. `status <id> building`; build with `/cro build-test` (variant code + preview).
2. `status <id> qa`: check control and variant screenshots on mobile and
   desktop, every targeted selector found, no JS errors, goals fire in the
   testing tool's preview.
3. Get the client's go in writing, then `status <id> running --note "<tool link>"`.
4. Monitoring rule: during the run, only check for a broken split (SRM), errors
   and revenue-threatening drops. **Do not stop early on a good-looking number.**

## result: calling a test

Only when the planned sample is reached (or the test is broken):
`program.py result <id> --cv <control visitors> --cc <control conversions> --vv <variant visitors> --vc <variant conversions>`.

- `NOT FINISHED` → keep running. `INVALID` (sample ratio mismatch) → fix the
  targeting, rerun from zero. `WIN` → ship, then confirm with the baseline.
  `LOSS` or `FLAT` → record what it teaches; flat results are information.
- Write `experiments/<id>/RESULT.md`: hypothesis, screenshots, numbers from the
  script, verdict, what we learned, next test it suggests.
- Then `status <id> shipped` or `rejected`.

## check: after a site release

`capture.py` the key pages again and `program.py diff <page> <new elements.json>`.
A changed CTA, form field count, trust element or tracking tag is reported to
the client the same day, with before/after screenshots.

## report: monthly client update

`program.py board`, then write `reports/<YYYY-MM>.md` (and `/cro slides` in
CLIENT mode for a call): what shipped, what ran, results with confidence ranges
in plain words, learnings, next month's plan, any readiness change (re-run
`test_readiness.py` with the latest month's numbers). Never claim revenue from a
test beyond what its confidence range supports.
