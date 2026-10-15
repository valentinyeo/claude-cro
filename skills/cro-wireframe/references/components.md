# Low-fidelity component snippets

Copy only the sections needed. Link `assets/wireframe.css` from a local copy.
Always include `<meta name="viewport" content="width=device-width, initial-scale=1">`.
Use real site words in before. The examples below are illustrative copy, not
facts about a client. Replace every product, price, logo, review, policy, and
claim with evidence from that business, or omit it. Use proposed copy in after
and record its supporting evidence. Never copy example claims into a client page.

Keep all surfaces grayscale. Only the primary CTA uses blue. Red is reserved
for numbered review annotations, not customer-facing urgency or a second CTA.
Render just one primary action per viewport. Secondary paths are neutral links.
A sticky CTA replaces an in-view primary action, rather than competing with it.
This kit is static: menu buttons, gallery choices, cart buttons and forms show
layout, not working flows. Native FAQ details work without JavaScript.

## Header / nav

```html
<header class="wf-header">
  <button class="wf-button wf-menu" aria-label="Open menu">Menu</button>
  <a class="wf-brand wf-link" href="#home">Allbirds</a>
  <nav class="wf-nav" aria-label="Main navigation">
    <a class="wf-link" href="#new">New arrivals</a>
    <a class="wf-link" href="#men">Men</a>
    <a class="wf-link" href="#women">Women</a>
  </nav>
  <a class="wf-link" href="#cart">Bag</a>
</header>
```

## Hero: headline, subhead, primary CTA

A mobile value proposition and its primary action should fit within the
390 x 844 viewport including the real header. Keep crop/layout in before even
when it is poor. In after, put useful copy before a tall image when appropriate.

```html
<section class="wf-hero" id="home">
  <div class="wf-copy">
    <p class="wf-eyebrow">Everyday shoes</p>
    <h1>Comfort for your everyday.</h1>
    <p>Explore shoes for daily routines, weekend plans, and travel.</p>
    <a class="wf-cta" href="#shoes">Shop shoes</a>
  </div>
  <div class="wf-placeholder" role="img" aria-label="Lifestyle photograph showing shoes in use">
    Lifestyle image: shoes in use
  </div>
</section>
```

## Trust bar / logos

Only name real customers, certifications or publications with verified rights
and relevance. Do not turn an unverified press mention into an endorsement.

```html
<section class="wf-trust" aria-label="Featured in">
  <span>Featured in</span>
  <span class="wf-logo">Verified publication name</span>
</section>
```

## Reviews / stars

Numbers and quotes must refer to the right product, date and review source.

```html
<blockquote class="wf-reviews">
  <p class="wf-stars" aria-label="4.7 out of 5 stars">★★★★☆</p>
  <p>4.7 out of 5, from 218 verified product reviews</p>
  <p>“Comfortable on my daily walk.”</p>
  <cite>Verified buyer, source and date in evidence notes</cite>
</blockquote>
```

## Product gallery

Use labeled boxes, not downloaded remote images. Represent the original crop
and relative size in before. No need to draw a shoe realistically.

```html
<div class="wf-gallery" aria-label="Product images">
  <div class="wf-placeholder" role="img" aria-label="Shoe side view">Side view</div>
  <div class="wf-placeholder" role="img" aria-label="Sole detail">Sole detail</div>
  <div class="wf-placeholder" role="img" aria-label="Shoe on foot">On foot</div>
  <div class="wf-placeholder" role="img" aria-label="Upper detail">Upper detail</div>
</div>
```

## Price block

Never invent a discount, total, shipping threshold, availability, or currency.

```html
<section aria-label="Price">
  <h2>Everyday walking shoes</h2>
  <p class="wf-price">$110</p>
  <p class="wf-note">Shipping and taxes calculated at checkout.</p>
  <a class="wf-link" href="#shipping">Delivery and returns</a>
</section>
```

## Sticky add-to-cart

Use on a product page only. Reserve space so it does not obscure content.
For static screenshots, include the sticky version only in a scrolled state
where the original CTA is out of view. Do not add cart actions to a homepage.

```html
<div class="wf-sticky" aria-label="Purchase selected product">
  <span>Walking shoes<br><strong>$110</strong></span>
  <button class="wf-cta" type="button">Add to bag</button>
</div>
```

## Form with visible labels

Do not use placeholders as labels. Keep only fields needed to complete the
current step and retain consent copy. Do not submit wireframe forms.

```html
<form class="wf-form" aria-label="Request a quote">
  <label for="email">Work email
    <input id="email" name="email" type="email" autocomplete="email" required>
  </label>
  <label for="project">What do you need help with?
    <textarea id="project" name="project" rows="3" required></textarea>
  </label>
  <p class="wf-note">We will use your details to reply to this request.</p>
  <button class="wf-cta" type="button">Request my quote</button>
</form>
```

## Pricing table

Use verified plan names, prices, billing period, limits and feature differences.
Do not call a plan “most popular” without usage evidence. Highlight one next step.

```html
<div class="wf-pricing" aria-label="Compare plans">
  <section class="wf-plan"><h2>Starter</h2><p>$19 / month</p>
    <p>For a single project.</p><a class="wf-link" href="#starter">View Starter</a></section>
  <section class="wf-plan wf-plan-featured"><h2>Team</h2><p>$49 / month</p>
    <p>For shared projects.</p><a class="wf-cta" href="#team">Choose Team</a></section>
  <section class="wf-plan"><h2>Business</h2><p>Custom pricing</p>
    <p>For larger teams.</p><a class="wf-link" href="#contact">Talk to us</a></section>
</div>
```

## FAQ accordion

Keep answers grounded in the business policy. Use `open` when the answer must
be visible in a static screenshot, not hidden behind an unimplemented widget.

```html
<section class="wf-faq" aria-label="Common questions">
  <h2>Before you order</h2>
  <details open><summary>When will my order ship?</summary>
    <p>See the current delivery estimate at checkout.</p></details>
  <details><summary>How do returns work?</summary>
    <p>Read our returns policy for eligibility and instructions.</p></details>
</section>
```

## Guarantee badge

Use only an existing, evidenced guarantee. Preserve restrictions and link to
terms; if unknown, omit the badge and list the missing policy in the notes.

```html
<p class="wf-guarantee">30-day returns, subject to policy</p>
<a class="wf-link" href="#returns">Read returns terms</a>
```

## Footer

```html
<footer class="wf-footer">
  <strong>Allbirds</strong>
  <nav class="wf-actions" aria-label="Footer">
    <a class="wf-link" href="#help">Help</a>
    <a class="wf-link" href="#privacy">Privacy policy</a>
    <a class="wf-link" href="#returns">Returns</a>
  </nav>
</footer>
```

## Annotations: red markers and side legend

Each marker is a positive integer, unique within a page. Use the same number
for the same change in before and after. Before markers are optional; every
annotation must appear in after. Markers are review graphics, not buttons.
They may sit next to copy rather than cover it. Keep the source page width at
390 / 1440; the renderer adds a side legend outside those page boundaries.

```html
<section class="wf-hero wf-annotated">
  <span class="wf-marker" data-annotation="1" aria-label="Change 1">1</span>
  <!-- Actual hero copy and layout here. -->
</section>
```

`annotations.json` is the sole source for the generated comparison legend:

```json
[
  {
    "number": 1,
    "finding_id": "H-1",
    "change": "Move the product benefit above the campaign image.",
    "evidence": "mobile.png: hero image precedes the headline; page.html quotes the benefit."
  }
]
```

For a separate specification sheet (not the 390px page), the kit also supports
`wf-with-legend` with a main column and `aside.wf-legend`. Do not duplicate the
legend inside the rendered page when the comparison already supplies it.
