# pstack model configuration for claude-cro. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Agent `model`). Alias entries in a panel list still count toward its fan-out.
# Values are `<model> <effort>` for the Agent tool, e.g. `opus medium` = model "opus", effort "medium".
# budget: custom (house rules 2026-10-25: code sonnet high, judgment/hardest opus medium, lookups haiku)
# Token ladder wins: before each spawn run `pstack-role <role>`. If it says hax/codex, use that, not these lines.
# Claude workers run alone; never spawn Codex or Grok helpers from a Claude worker. No fast models.
feature, refactoring: sonnet high
bug-fix: sonnet high
perf-issue: sonnet high
hillclimb: sonnet high
judgment and prose: opus medium
hardest tasks: opus medium
how explorer: haiku medium
how explainer: opus medium
why investigators: sonnet high
why synthesizer: opus medium
reflect tooling: sonnet high
reflect judgment, divergent, synthesizer: opus medium
arena runners: opus medium, sonnet high
arena cross-judge pool: opus medium, sonnet high
swarm workers: sonnet high
architect runners: opus medium, sonnet high
interrogate reviewers: opus medium, sonnet high
