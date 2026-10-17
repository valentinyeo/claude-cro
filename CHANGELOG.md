# Changelog

All notable changes to Claude CRO will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-10-17

### Added
- Works in Claude Code cloud sessions (proxy-aware fetching, preinstalled Chromium fallback)
- Free teardown line at the end of every audit report and results page
- Evals: scores the pack against plain Claude on planted defects and held-out test winners

### Changed
- Plugin renamed to `cro` in marketplace `valentinyeo-cro`
- The cro skill triggers on page reviews; cro-page and cro-forms check more defects

## [1.0.0] - 2026-03-01

### Added
- Initial release of Claude CRO skill package
- Main orchestrator (`cro/SKILL.md`) with routing for 12 sub-commands
- 12 sub-skills: audit, page, funnel, test, copy, ux, forms, ecommerce, trust, tracking, benchmark, plan
- 6 parallel subagents for full site audits: cro-ux, cro-copy, cro-tracking, cro-visual, cro-performance, cro-trust
- CRO Health Score (0-100) with weighted category scoring
- Industry detection for SaaS, E-commerce, Lead Gen, Subscription, Local Service, and Agency sites
- 5 reference files: conversion benchmarks, psychology principles, testing framework, UX heuristics, quality gates
- 4 Python utility scripts:
  - `fetch_page.py` — URL fetcher with SSRF prevention
  - `parse_cro.py` — HTML CRO element extractor
  - `capture_screenshot.py` — Playwright-based screenshot capture
  - `analyze_funnel.py` — Multi-page funnel analyzer
- Install/uninstall scripts for Linux, macOS, and Windows
- Report validation hook (`validate-cro-report.sh`)
- Comprehensive documentation: architecture, commands, installation, troubleshooting
