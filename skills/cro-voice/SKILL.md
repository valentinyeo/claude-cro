---
name: cro-voice
description: >
  Brand voice analysis and wording master document generation. Crawls multiple
  pages of a website to extract tone, vocabulary, sentence patterns, terminology,
  messaging themes, and CTA language patterns. Produces a reusable Brand Voice
  Master Document for consistent A/B test copywriting. Use when user says
  "brand voice", "wording analysis", "tone analysis", "voice guide", or
  "voice master".
argument-hint: "<url>"
allowed-tools: Read, Grep, Glob, Bash, WebFetch
---

# CRO Voice -- Brand Voice & Wording Master

Crawl a website, extract brand voice patterns across multiple pages, and produce
a reusable Brand Voice Master Document. This document becomes the reference for
other skills (`cro-testing`, `cro-copy`) when generating A/B test variants,
ensuring all suggested copy stays on-brand.

---

## Process

1. **Fetch the homepage** using `${CLAUDE_SKILL_DIR}/../cro/scripts/fetch_page.py`
   with the provided URL.

2. **Discover key pages** by extracting internal links from the homepage HTML.
   Identify up to 5 additional pages to analyze:
   - About / Our Story page
   - A product or service page
   - Pricing page (if present)
   - A blog post (if present)
   - Contact page

   Fetch each discovered page using `fetch_page.py`.

3. **Extract text content** from each page using
   `${CLAUDE_SKILL_DIR}/../cro/scripts/parse_cro.py`. This separates headlines,
   body copy, CTA text, testimonials, and micro-copy.

4. **Analyze across 8 dimensions** (see below). Look for patterns that are
   consistent across multiple pages -- these define the brand voice. Note any
   inconsistencies between pages as well.

5. **Generate the Brand Voice Master Document** following the output format
   below.

6. **Save to `reports/{domain}-voice.md`** (strip protocol and trailing slashes
   from the URL to derive the domain filename).

7. **Print a summary** with the voice personality description and path to the
   saved file.

---

## 8 Analysis Dimensions

### 1. Tone Profile

Rate the brand on each axis using a 1-5 scale. Provide evidence (specific
quotes or patterns) for each rating.

| Axis | 1 | 5 |
|------|---|---|
| Formal <-> Casual | Corporate, third-person, complex sentences | Conversational, contractions, short sentences |
| Serious <-> Playful | No humor, factual, clinical | Puns, jokes, lighthearted metaphors |
| Authoritative <-> Friendly | Expert-led, commanding, declarative | Peer-level, collaborative, inviting |
| Technical <-> Simple | Industry jargon, complex terms, assumed knowledge | Plain language, analogies, no jargon |

### 2. Vocabulary Level

| Metric | How to Assess |
|--------|---------------|
| Average word complexity | Count syllables per word across body copy samples |
| Jargon frequency | Count industry-specific terms per page |
| Reading grade level | Estimate Flesch-Kincaid grade from sentence and word length |
| Industry-specific terms | List all domain jargon used; note which terms are explained vs assumed |

### 3. Key Terminology (Sacred Words)

Identify words and phrases used repeatedly across multiple pages. These are
brand-defining terms that should NEVER be changed in A/B test variants.

**How to identify:**
- Words/phrases appearing on 3+ pages
- Terms used in headlines, CTAs, and value propositions
- Trademarked or proprietary terms
- Emotionally charged words that carry brand meaning

**Output:** List each sacred term with usage count and page locations.

### 4. Messaging Themes

Core themes communicated consistently across pages. These represent the brand's
values and positioning.

**How to identify:**
- Recurring concepts across headlines and body copy
- Consistent value propositions
- Repeated benefit categories
- Common objection-handling patterns

### 5. Sentence Patterns

| Metric | How to Measure |
|--------|----------------|
| Average sentence length | Word count per sentence across all pages |
| Active vs passive voice | Percentage of sentences in active voice |
| Question usage | Frequency of questions in copy (rhetorical or direct) |
| Exclamation frequency | How often exclamation marks appear |
| Fragment usage | Short, punchy fragments vs complete sentences |
| List vs paragraph | How content is structured -- bullets/lists vs flowing prose |

### 6. Person & Voice

| Pattern | How to Measure |
|---------|----------------|
| First person (we/our) | Count across all pages, note context of usage |
| Second person (you/your) | Count across all pages, note context of usage |
| Third person (they/the company) | Count across all pages |
| Direct address style | How does the brand speak TO the reader? Commands, invitations, questions? |
| You:We ratio | Calculate the ratio; higher = more customer-centric |

### 7. Emotional Register

Identify the primary emotions the brand consistently evokes:

- **Confidence** -- "trusted", "proven", "reliable"
- **Warmth** -- "caring", "together", "family"
- **Excitement** -- "amazing", "revolutionary", "game-changing"
- **Urgency** -- "now", "don't miss", "limited"
- **Calm** -- "peace of mind", "easy", "simple"
- **Empowerment** -- "take control", "your journey", "unlock"

Classify as Primary (dominant across pages), Secondary (present but not dominant),
and Avoided (emotions the brand never uses).

### 8. CTA Language Patterns

Analyze every CTA across all crawled pages:

| Attribute | What to Record |
|-----------|----------------|
| Verb choice | What action verbs does the brand prefer? (Get, Start, Discover, Shop, Try, etc.) |
| Commitment level | Soft (explore, learn, discover) vs Hard (buy, subscribe, sign up) |
| First vs second person | "Start My Trial" vs "Start Your Trial" vs "Start Free Trial" |
| Risk reducers | "Free", "No credit card", "Cancel anytime" -- which are used? |
| Urgency in CTAs | "Now", "Today", "Instantly" -- presence and frequency |
| CTA length | Average word count of CTA buttons |

---

## Output Format

Save this as `reports/{domain}-voice.md`:

```markdown
# Brand Voice Master: {domain}
**Generated:** {date}
**Pages analyzed:** {list of URLs}

## Voice Profile Summary
[2-3 sentence personality description that captures the brand's voice as if
describing a person. E.g., "inne.io speaks like a knowledgeable friend -- warm
but evidence-based, casual but never sloppy. The brand avoids corporate jargon
in favor of relatable, empowering language around women's health."]

## Tone Spectrum

| Axis | Rating (1-5) | Evidence |
|------|-------------|----------|
| Formal <-> Casual | X | [Specific quotes/patterns] |
| Serious <-> Playful | X | [Specific quotes/patterns] |
| Authoritative <-> Friendly | X | [Specific quotes/patterns] |
| Technical <-> Simple | X | [Specific quotes/patterns] |

## Sacred Terminology
Words/phrases that define the brand -- NEVER replace in A/B tests:
- "{term 1}" -- used X times across Y pages
- "{term 2}" -- used X times across Y pages
- ...

## Messaging Themes
1. **{Theme}** -- Evidence: [quotes from site]
2. **{Theme}** -- Evidence: [quotes from site]
3. ...

## Vocabulary & Readability
- Reading grade level: X
- Avg sentence length: X words
- Active voice: X%
- Jargon density: X terms per page
- Industry terms used: [list]

## Person & Voice Patterns
- You/your usage: X%
- We/our usage: X%
- You:We ratio: X:1
- Direct address style: [description]

## Emotional Register
- **Primary:** [emotion(s)]
- **Secondary:** [emotion(s)]
- **Avoided:** [emotions the brand never uses]

## CTA Language Patterns

| Location | CTA Text | Verb Type | Commitment Level |
|----------|----------|-----------|-----------------|
| Homepage hero | "..." | Soft/Hard | Low/Medium/High |
| Product page | "..." | Soft/Hard | Low/Medium/High |
| ... | ... | ... | ... |

**Preferred CTA verbs:** [list]
**Avg CTA length:** X words
**Risk reducers used:** [list or "none"]

## A/B Test Copywriting Guidelines
Based on this analysis, when writing test variants for {domain}:

### DO:
1. [Specific guideline derived from analysis]
2. [Specific guideline derived from analysis]
3. [Specific guideline derived from analysis]
4. [Specific guideline derived from analysis]
5. [Specific guideline derived from analysis]

### DON'T:
1. [What to avoid, derived from analysis]
2. [What to avoid, derived from analysis]
3. [What to avoid, derived from analysis]
4. [What to avoid, derived from analysis]
5. [What to avoid, derived from analysis]
```

---

## Cross-References

- **Copy analysis:** Use the `cro-copy` sub-skill for detailed copy scoring. The voice document provides context for the copy skill's rewrite suggestions.
- **A/B testing:** Use the `cro-testing` sub-skill to generate test hypotheses. It will load the voice document to ensure variant copy stays on-brand.
- **Full page analysis:** Use the `cro-page` sub-skill for a broader conversion audit.
- **Psychology:** Read `${CLAUDE_SKILL_DIR}/../cro/references/psychology-principles.md` for persuasion principles to map against the brand's emotional register.
- **Quality gates:** Read `${CLAUDE_SKILL_DIR}/../cro/references/quality-gates.md` for minimum copy standards by business type.
