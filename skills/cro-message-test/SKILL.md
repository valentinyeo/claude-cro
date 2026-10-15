---
name: cro-message-test
description: >
  Message and offer test on a simulated audience: a crowd of AI buyers built by
  MiroFish (run locally, Claude Haiku) discusses two or three versions of an
  offer, price format or headline, then a report says which they favour and
  what objections stop them. Use for /cro message-test, "test this offer",
  "which headline", "pricing reaction", or when a site is too small to A/B test.
argument-hint: "<brief.md or audit-folder> \"<question>\" [--rounds 12]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash
---

# Message test (MiroFish)

Small sites cannot A/B test (readiness NOT_TESTABLE or LIMITED). This gives an
early read on a message before it ships: which version a simulated crowd of the
client's buyers prefers, and the objections they raise in their own words.
It is simulated opinion. Label it so everywhere, put it next to real interviews,
and never present it as proof or a conversion forecast.

`M` = `"<CRO_SCRIPTS>/cro-py" message_test.py`.

## Setup (once per machine)

MiroFish is AGPL and lives outside this repo: `~/projects/mirofish`, a clone of
https://github.com/nikmcfly/MiroFish-Offline (English, Neo4j instead of Zep Cloud).
`~/projects/mirofish/start.sh` starts Neo4j and Ollama (embeddings) in Docker, a
local relay on 127.0.0.1:5011 that holds the Anthropic key and pins Claude Haiku,
and the app on 127.0.0.1:5001 (UI on :3000). Check with `M check`: it must print
`MIROFISH UP haiku`. If it cannot connect, run start.sh, then check again.

## 1. Write the brief

One Markdown file, about one page, in `W/message-test/brief.md`:

- **Who is selling**: what they do, proof they can show (numbers from the audit, not invented).
- **Who is buying**: roles, company size, budget power, what they must justify.
  Use the audit's personas and business type.
- **The versions**: 2-3 offers, price formats or headlines, word for word.
  Use the live site's text for "current". Mark any number we made up for the
  test (for example a monthly price the client has not set) in the brief and the result.
- **How people buy**: book a call, add to cart, sign up.

## 2. Run

```bash
M run "$W/message-test/brief.md" --name "<site> offer" --rounds 12 --platform reddit \
  --out "$W/message-test" --question "<which version makes <buyers> more willing to <action>, and what objections stop them?>"
```

12 rounds on one platform costs a few dollars with Haiku and takes 20-60
minutes; the report prints tokens and cost. Use `--platform parallel` and more
rounds only when the client asks for a bigger run. The run stops at
`--timeout` (default 90 minutes) with an error naming the step.

## 3. Read and report

Open `MESSAGE-TEST.md`. Before passing anything on:

- Check each claim it makes about the versions against the posts it cites.
  Drop conclusions with no agent quote behind them.
- Separate what the crowd preferred from why (objections, quotes).
- Write a short `MESSAGE-TEST-SUMMARY.md`: preferred version, top 3 objections with
  one quote each, what to change, and the caveat line. Keep invented test numbers labelled.
- In an audit deck, add it as one slide or appendix item: "Simulated buyer reaction
  (MiroFish): early signal, not proof".
