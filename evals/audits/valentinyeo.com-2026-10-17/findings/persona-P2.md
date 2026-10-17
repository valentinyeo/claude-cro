Status: complete
# Persona: P2, busy DTC founder, mobile, wants the free 20 minute teardown
**Outcome:** reached the booking calendar (cal.com) in about 1 tap. Did not book.
**Steps taken:** 5 (goto, 3 scrolls, goto cal.com) · **Time a real visitor would spend:** about 30 to 60 seconds
Note: the harness click on the CTA hung for over 2 minutes. The CTA is target=_blank to cal.com, so this is probably a new-tab artefact. I went to the cal.com URL directly.

## Friction log
| Step | What I tried | What happened | Severity | Evidence |
|------|--------------|---------------|----------|----------|
| 1 | Land from Google and scan | Headline "More A/B tests, shipped faster." and a dark full-width "Get your free 20 minute teardown" button are visible without scrolling. Clear. | None (positive) | step-01.png |
| 1 | Understand the offer | The paragraph says "100 tests for inne" and "took Eduki from 5 to 120+". I do not know who inne or Eduki are, or whether they are DTC. Nothing says "for ecommerce/DTC brands". | Medium | step-01.png |
| 1 | Look for proof | "See the results" is a small text link under the button, easy to miss. The 100+ stat sits below the fold with only a label. | Low | step-01.png |
| 1 | Understand the CTA | "Teardown" is jargon. Nothing says what I get (a video? a call?) or that I need to bring my site. | Medium | step-01.png |
| 3 | Scroll the page | A blank band about 200px tall appears under the header, probably a reveal-on-scroll animation. Content looks missing. The sticky header also eats space. | Low | step-03.png |
| 3 | Look for pricing | Services (Done-For-You, Audit, and a third) give no prices or starting point. I cannot judge whether I can afford him. | Medium | step-03.png |
| 4 | Reach the bottom | The closing CTA repeats. "Email" and "WhatsApp" are small underlined text links with little tap padding, and the address shows only as plain text. | Low | step-04.png |
| 4 | Trust check | The footer has a real address, phone and sole trader name, which helps. The address is a shared-office style and the gmail address looks less like a business. | Low | step-04.png |
| 5 | Tap the CTA | It opens cal.com in a new tab (target=_blank). The page is clear: "Free, no-obligation", 20m, Google Meet, and a calendar. The first slot is Monday 19th. A teardown call with no booking form is quick. | Low | step-05.png |
| 5 | Pick a time | The timezone field says "Select..." and is empty. I have to set it before the times make sense, and the calendar pushes the slots below the fold on mobile. | Medium | step-05.png |
| 5 | What happens next | "Bring your site" is the only prep instruction. It does not say whether I need analytics access or who joins. | Low | step-05.png |

## Moments of doubt
- Is this for DTC or ecommerce brands, or only for large sites like trivago?
- What does it cost afterwards, and what is the catch with a "free" teardown?
- Who are inne and Eduki? No logos or one-line results shown near the top.
- What do I need to bring or prepare, and will it be a sales pitch?
- Is he available soon? The earliest slot was 2 days out, which is fine but is not stated on the site.

## Top 3 fixes from this visitor's view
1. Add a line under the hero, "For ecommerce and DTC teams", plus 2 or 3 client logos or one quantified result right under the CTA, and expand "inne" and "Eduki" in plain words. Evidence: step-01.png
2. Make the CTA say what happens ("Book a free 20-minute site review, no pitch") and add "what you get / what to bring" microcopy. Show starting prices or engagement ranges in Services. Evidence: step-01.png, step-03.png
3. Make "See the results", Email and WhatsApp full-size tap targets, fix the blank band on scroll, and open cal.com in the same tab or prefill timezone. Evidence: step-03.png, step-04.png, step-05.png
