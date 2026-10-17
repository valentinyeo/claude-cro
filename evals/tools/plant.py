"""Plant five known conversion defects in a copy of each clean fixture and write its answer key.
Two tiers: the five obvious defects (<site>.planted.html) and five subtle ones (<site>.subtle.html).
The planting is deterministic, so CI can rebuild every planted page and compare it byte for byte.
Usage: plant.py [--check]   (--check: fail if a committed planted page or answer key is out of date)"""
import json
import re
import sys
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1]
FIX = EVALS / "fixtures"
KEYS = EVALS / "answer-keys"
SITES = ["hypertask.ai", "valentinyeo.com", "endlesstesting.ai"]

HEADLINE = "Welcome to our website"
URGENCY = ('<div class="planted-urgency" style="background:#b91c1c;color:#fff;text-align:center;padding:8px">'
           "Hurry! Only 3 spots left at this price. Offer ends in 00:14:59</div>")
CTA = '<p><a href="#" class="planted-cta" style="display:inline-block;padding:12px 24px;background:#111;color:#fff">Submit</a></p>'
PRICE_TOP = '<p class="planted-price">Pro plan: $49 per month</p>'
PRICE_BOTTOM = '<p class="planted-price">Pro plan: $79 per month, billed monthly</p>'
FIELDS = ["First name", "Last name", "Work email", "Phone number", "Company", "Job title",
          "Company size", "Country", "Date of birth"]
FORM = ('<section class="planted-form"><h2>Get started</h2><form action="#" method="post">'
        + "".join(f'<label>{f} *<input name="f{i}" required></label>' for i, f in enumerate(FIELDS, 1))
        + '<button type="submit">Send</button></form></section>')

# Each defect: where it was planted (snippet), and what counts as "found" when it appears in the agent's answer.
# `found` is a JavaScript-compatible regex, applied case-insensitively; the eval graders use the same pattern.
DEFECTS = [
    {"id": "vague-cta", "label": 'Vague CTA "Submit" linking to "#"', "snippet": CTA,
     "found": r"[\"'“‘]Submit[\"'”’]"},
    {"id": "meaningless-headline", "label": 'Headline "Welcome to our website"', "snippet": HEADLINE,
     "found": r"Welcome to our website"},
    {"id": "long-form", "label": "Form with 9 required fields", "snippet": FORM,
     "found": r"\b(9|nine)\b[^\n]{0,40}(fields?|inputs?|questions?)|(fields?|inputs?)[^\n]{0,40}\b(9|nine)\b|date of birth"},
    {"id": "fake-urgency", "label": 'Fake urgency banner "Only 3 spots left ... 00:14:59"', "snippet": URGENCY,
     "found": r"only 3 spots|spots left|00:14:59|offer ends in|fake urgency|false urgency|countdown"},
    {"id": "conflicting-prices", "label": "Pro plan priced $49 and $79 on the same page",
     "snippet": PRICE_TOP + " / " + PRICE_BOTTOM, "found": r"^(?=[\s\S]*\$49)(?=[\s\S]*\$79)"},
]


SUBTLE_CLAIM = '<p class="planted-claim">Trusted by 10,000+ teams worldwide. 30-day money-back guarantee.</p>'
SUBTLE_FORM = ('<section class="planted-signup"><h2>Get the weekly teardown</h2><form action="/subscribe" method="post">'
               '<input type="email" name="email" placeholder="Your work email">'
               '<input type="text" name="company" placeholder="Company website">'
               '<label><input type="checkbox" name="partners" checked> Yes, send me offers from our partners</label>'
               '<button type="submit">Get the weekly teardown</button></form></section>')
SUBTLE_SMALL = '<p class="planted-small" style="font-size:10px;color:#999">A $25 setup fee applies to every new account. All sales are final.</p>'

SUBTLE = [
    {"id": "placeholder-labels", "label": "Signup inputs have placeholders but no labels",
     "snippet": '<input type="email" name="email" placeholder="Your work email">',
     "found": r"placeholder[^\n]{0,120}label|label[^\n]{0,120}placeholder|unlabell?ed|no visible label"},
    {"id": "unsupported-claim", "label": '"Trusted by 10,000+ teams" with no names, logos or source', "snippet": "Trusted by 10,000+ teams worldwide.",
     "found": r"10,000\+? teams"},
    {"id": "prechecked-consent", "label": "Partner-offers checkbox is pre-checked",
     "snippet": '<input type="checkbox" name="partners" checked>',
     "found": r"pre-?(checked|ticked|selected)|checked by default|ticked by default|partner offers|offers from our partners"},
    {"id": "hidden-fee", "label": "$25 setup fee only in 10px grey small print", "snippet": "A $25 setup fee applies to every new account.",
     "found": r"\$25|setup fee"},
    {"id": "guarantee-conflict", "label": '"30-day money-back guarantee" contradicted by "All sales are final"',
     "snippet": "30-day money-back guarantee. / All sales are final.",
     "found": r"^(?=[\s\S]*(money-back|30-day))(?=[\s\S]*all sales are final)"},
]

TIERS = {"planted": DEFECTS, "subtle": SUBTLE}


def plant(html):
    html, n = re.subn(r"(<h1\b[^>]*>)[\s\S]*?(</h1>)", lambda m: m.group(1) + HEADLINE + m.group(2), html, count=1)
    assert n == 1, "no <h1>"
    html = re.sub(r"</h1>", lambda m: m.group(0) + CTA + PRICE_TOP, html, count=1)
    html, n = re.subn(r"(<body\b[^>]*>)", lambda m: m.group(1) + URGENCY, html, count=1)
    assert n == 1, "no <body>"
    html, n = re.subn(r"(<footer\b)", lambda m: FORM + PRICE_BOTTOM + m.group(1), html, count=1)
    assert n == 1, "no <footer>"
    return html


def plant_subtle(html):
    html, n = re.subn(r"</h1>", lambda m: m.group(0) + SUBTLE_CLAIM, html, count=1)
    assert n == 1, "no <h1>"
    html, n = re.subn(r"(<footer\b[^>]*>)", lambda m: SUBTLE_FORM + m.group(1) + SUBTLE_SMALL, html, count=1)
    assert n == 1, "no <footer>"
    return html


def build():
    out = {}
    for s in SITES:
        clean = (FIX / f"{s}.clean.html").read_text(encoding="utf-8")
        for tier, fn, suffix in (("planted", plant, ""), ("subtle", plant_subtle, ".subtle")):
            out[FIX / f"{s}.{tier}.html"] = fn(clean)
            key = {"fixture": f"fixtures/{s}.{tier}.html", "clean": f"fixtures/{s}.clean.html", "tier": tier,
                   "defects": [{k: d[k] for k in ("id", "label", "found")} | {"snippet": d["snippet"]} for d in TIERS[tier]]}
            out[KEYS / f"{s}{suffix}.json"] = json.dumps(key, indent=2, ensure_ascii=False) + "\n"
    return out


if __name__ == "__main__":
    stale = []
    for path, text in build().items():
        if "--check" in sys.argv:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(EVALS)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print("wrote", path.relative_to(EVALS))
    if stale:
        sys.exit("out of date (run evals/tools/plant.py): " + ", ".join(stale))
