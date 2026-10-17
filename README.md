# Claude CRO: find out why visitors don't buy, and fix it

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/valentinyeo/claude-cro/actions/workflows/ci.yml/badge.svg)](https://github.com/valentinyeo/claude-cro/actions/workflows/ci.yml)

A free, complete conversion rate optimization (CRO) method for Claude Code. Point it at your website and it shows you, with screenshots and quotes from your own pages, what stops visitors from buying, booking or signing up, which fix to try first, and how to tell whether the fix worked.

Nothing is held back. This is the same method used on paid client work.

## Start here: improve your own site in one afternoon

**1. Install** (Claude Code 2.1.275 or later):

```
/plugin install cro --marketplace valentinyeo/claude-cro
```

Older Claude Code: `/plugin marketplace add valentinyeo/claude-cro`, then `/plugin install cro@valentinyeo-cro`. Or clone the repo and run `./install.sh` (Windows: `install.ps1`).

**2. Check the setup:** `/cro doctor`. The first run sets up its own Python env and a headless browser, which takes about a minute.

**3. Audit your site:**

```
/cro audit https://your-site.com
```

About 20 minutes. Specialist agents review UX, copy, trust, visuals, speed and tracking. AI visitors then try to buy or book in a real browser, and a skeptic agent throws out every finding it can disprove from the screenshots.

**4. Read the results:** `/cro results <audit-folder>` builds one page: a score out of 10 per area, what stands between each score and 10/10, and the experiments to run next, each with its hypothesis.

See a real one first: the maintainer's own site, audited with this pack: https://valentinyeo.github.io/claude-cro/examples/valentinyeo.com/

**5. Fix one thing and measure it.** Start with the top Critical finding. The audit says whether your traffic is big enough for an A/B test. If not, use the before-and-after checks on the results page instead.

## How the method works

- **Traffic decides the method.** A/B tests need roughly 100+ conversions per variant to mean anything. The Test Readiness Gate checks your numbers first. Small sites get research and before-and-after checks instead of a test backlog they can't finish.
- **Evidence or it's cut.** Every finding quotes your page, names the element, or cites a measured number. A skeptic agent tries to disprove each one before you see it.
- **Real visitors beat opinions.** Browser personas and synthetic visitors modelled on your analytics show where people actually stop, not just what breaks a rule.
- **Industry numbers are estimates.** Benchmarks and "proven test" lifts come from published case studies. The pack labels them that way and never promises a lift.

The reasoning behind each step lives in [`skills/cro/references/`](skills/cro/references/): test readiness, scoring, UX heuristics, persuasion principles, proven tests and conversion benchmarks.

## Commands

**Find the problems**

| Command | What you get |
|---------|--------------|
| `/cro audit <url>` | Full audit: specialist agents, browser personas, skeptic review, scored findings |
| `/cro page <url>` | Quick review of one page, no agents |
| `/cro funnel <url1> <url2> ...` | Where visitors drop between steps |
| `/cro copy` `ux` `forms` `trust` `tracking` `ecommerce <url>` | One area in depth |
| `/cro benchmark <url> <competitor>` | Side-by-side with a competitor |
| `/cro synthetic <url> [--traffic export.csv]` | 100-200 AI visitors modelled on your analytics try to convert and report friction |
| `/cro message-test <brief> "<question>"` | Simulated buyers compare offers, prices or headlines (needs MiroFish, installed separately) |

**Decide and fix**

| Command | What you get |
|---------|--------------|
| `/cro results <audit-folder>` | One page with every result, scores out of 10 and next experiments |
| `/cro readiness` | Is your traffic big enough to A/B test? |
| `/cro test <url>` | Test ideas with hypotheses, sized to your traffic |
| `/cro wireframe <url or audit-folder>` | Before and after designs of the fixes, phone and desktop |
| `/cro build-test <url> "<hypothesis>"` | Test variant code with a browser preview |
| `/cro plan <url>` | 90-day roadmap |
| `/cro research [topic]` | Search a database of published A/B test results |

**For consultants and agencies**

| Command | What you get |
|---------|--------------|
| `/cro audit <url> --prospect` then `/cro slides <folder> --pitch` | A pitch deck built on a prospect's own site |
| `/cro program <init\|plan\|launch\|result\|report>` | Run a client's monthly experiment program |

Full reference: [docs/COMMANDS.md](docs/COMMANDS.md).

## Want it done for you?

The method is free. Running it well takes time: building the variants, running the tests, reading the results honestly. If you'd rather have an expert run the program on your site, book a free 20-minute teardown of your site with Valentin Yeo, who maintains this pack: https://cal.com/valentinyeo/teardown (more at https://valentinyeo.com)

## What's inside

- **20 skills:** the `/cro` router plus one skill per command, in [`skills/`](skills/)
- **8 agents:** UX, copy, tracking, visual, performance and trust specialists, a browser persona and a skeptic, in [`agents/`](agents/)
- **Python scripts:** page fetching with private-address blocking, screenshots, crawling, speed, tracking checks, scoring and reports, in [`skills/cro/scripts/`](skills/cro/scripts/)
- **Tests:** run on Linux, macOS and Windows in CI, including a check that no client names ever ship in the pack

Requirements: Claude Code, Python 3.9+. Playwright and its browser install themselves on first run.

## Contributing

Fork, branch, change, run `python tests/lint_skills.py` and `python -m unittest discover -s tests -p "test_*.py"`, then open a pull request. New skills follow the existing `SKILL.md` format: frontmatter, evaluation criteria, scoring, output template.

## License

MIT. See [LICENSE](LICENSE).
