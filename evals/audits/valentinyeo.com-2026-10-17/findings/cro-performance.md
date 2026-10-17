Status: complete

# Performance Impact Analysis (valentinyeo.com)

**Performance Score: 86/100 - Acceptable to good (lab-only, no field data)**

Data limits: PageSpeed API was unavailable. All numbers are from a local throttled headless Chromium run, not Lighthouse, with no real-user (CrUX) data. INP could not be measured, so TBT stands in for it. Treat scores as directional.

## Summary
All three pages are light (26-34 KB transferred, 6-9 requests) and have lab LCP of 1.0-1.7 s, well under the 2.5 s "good" line. Speed is probably not what holds back the "Get your free 20 minute teardown" click. The issues are hygiene problems: duplicate and render-blocking CDN CSS on case-study and contact, a third-party A/B SDK on home and contact, and no cache lifetime on HTML. Fix these to protect the current good result.

## Measurements (lab, mobile)
| Page | LCP | FCP | CLS | TBT | TTFB | Requests | Transfer | HTML |
|---|---|---|---|---|---|---|---|---|
| home | 1.0 s | 1.0 s | 0.084 | 64 ms | 570 ms | 8 | 34 KB | 37.8 KB |
| case-study | 1.7 s | 1.7 s | 0.000 | 43 ms | 882 ms | 6 | 26 KB | 18.1 KB |
| contact | 1.0 s | 1.0 s | 0.000 | 8 ms | 525 ms | 9 | 26 KB | 15.2 KB |

Response headers (all pages): Brotli (`content-encoding: br`), Cloudflare CDN, HTTP/3 advertised, `cache-control: public, max-age=0, must-revalidate`, `cf-cache-status: DYNAMIC`.

## Findings

### 1. Case-study and contact load duplicate, render-blocking third-party CSS (Medium)
Both pages load Pico CSS (cdn.jsdelivr.net) and Font Awesome 6.5.1 (cdnjs) in the head, plus `styles.css`. Font Awesome is linked twice, and the Figtree font stylesheet is linked twice. One copy uses a half-working async pattern (`media="all" onload="this.media='all'"` does not defer anything), and the other is a plain blocking link. Pico and the duplicate links add DNS, TLS and request cost, and they probably explain why case-study FCP and LCP (1.7 s) are slower than home (1.0 s). No `<img>` tags are present, so Font Awesome is likely only used for a few icons. Fix: remove the duplicates, self-host or drop Pico and Font Awesome (inline SVG for the few icons), and merge fonts into one request. This would likely bring case-study to about 1.0 s.
Evidence: pages/case-study/page.html and pages/contact/page.html head `<link>` tags (font-awesome all.min.css x2, Figtree stylesheet x2, pico.min.css); pages/case-study/speed.json lab LCP "1.7 s" vs pages/home/speed.json "1.0 s".

### 2. Third-party A/B testing SDK on home and contact (Medium)
`https://appbe.endlesstesting.ai/api/sdk.js` is loaded with `defer` on home and contact, with an inline `ab-config` script and an `ab-reveal-hook` script. The hook's `reveal()` is empty (comment: "No visual block anymore"), so there is no anti-flicker hide, which is good. Remaining cost is the extra third-party connection and the main-thread work. Home TBT is 64 ms, the highest of the three pages but still low. The SDK is absent on case-study, so the variants shown across the funnel are inconsistent. Keep `defer`, add a `preconnect` for appbe.endlesstesting.ai if the SDK stays, and check that the SDK does not change the hero or CTA after first paint (that would cause layout shift or flicker).
Evidence: pages/home/page.html `<script id="ab-sdk" defer src="https://appbe.endlesstesting.ai/api/sdk.js">` and line ~949 `ab-reveal-hook`; pages/contact/page.html same; pages/case-study/page.html has no ab-sdk; pages/home/speed.json TBT "64 ms".

### 3. Home CLS 0.084 is close to the 0.1 limit (Low-Medium)
Home CLS is 0.084 (still "good") while the other pages score 0.000. The page has no `<img>` tags, so the likely cause is web font swap (Inter with `display=swap`, loaded through a blocking stylesheet) or late changes from the A/B SDK. Any extra element could push it over 0.1. Fix: preload the Inter woff2 file, pick a metric-matched fallback (`size-adjust`), and fix the dimensions of the hero and CTA blocks.
Evidence: pages/home/speed.json lab CLS "0.084 (FAST)"; pages/home/page.html `fonts.googleapis.com/css2?family=Inter...display=swap` (render-blocking stylesheet in head).

### 4. HTML is not cached at the edge and measured response time varies (Low-Medium)
`cf-cache-status: DYNAMIC` and `max-age=0, must-revalidate` mean every visit goes back to origin. Server-Timing shows low origin time (cfOrigin 48-59 ms, cfEdge 38-60 ms), so the server is not the issue. Lab TTFB is 525-882 ms. The fetch tool recorded 2.3-3.7 s total response time, but that was a browser-driven fetch and is not comparable to real-user timing, so I did not use it for scoring. The case-study URL (`/inne-case-study.html`) also redirects to `/inne-case-study`, adding a hop for any link that uses the `.html` form. Fix: add a Cloudflare Cache Rule ("Cache Everything" with a short edge TTL), and update internal links and ads to the final URLs.
Evidence: pages/home/fetch.json headers `cache-control`, `cf-cache-status`, `server-timing`; pages/case-study/fetch.json `url` "inne-case-study.html" vs `final_url` "inne-case-study", and speed.json TTFB "882 ms".

### 5. Font loading: four families/stylesheets and mismatched fonts (Low)
Home uses Inter (4 weights, 400-700) while case-study and contact use Figtree 700 only. Each page needs a Google Fonts CSS request plus a gstatic font file (two connections). Loading fewer weights, or self-hosting a variable woff2 with `font-display: swap` and `preload`, removes two third-party hops on the conversion path. The preconnect hints are present (also set as an HTTP `Link` header), which is good.
Evidence: pages/home/page.html Inter `wght@400;500;600;700` link; pages/contact/page.html Figtree `wght@700` links; pages/home/fetch.json `link` header.

### 6. Unneeded Cloudflare beacon as a module script (Low)
`static.cloudflareinsights.com/beacon.min.js` loads as `type="module"` (deferred by default) on all pages. It is low impact. Keep it if you use Cloudflare analytics; otherwise disable it for one fewer request.
Evidence: pages/home/page.html, pages/case-study/page.html and pages/contact/page.html `<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js/...">`.

## Resource analysis (approximate, from speed.json and HTML)
| Type | Home | Case-study | Contact | Notes |
|---|---|---|---|---|
| HTML | 37.8 KB | 18.1 KB | 15.2 KB | Brotli; two inline `<style>` blocks on home and contact, one on case-study |
| CSS | inline plus Google Fonts | styles.css, Pico, FA (x2), fonts (x2) | same as case-study | Blocking, 4-5 stylesheets on inner pages |
| JS | 3 inline plus A/B SDK plus beacon | beacon only | same as home | A/B SDK deferred |
| Images | 0 `<img>` | 0 | 0 | Only the SVG favicon; no raster weight |
| Total transfer | 34 KB / 8 req | 26 KB / 6 req | 26 KB / 9 req | Very light |

Third-party domains: fonts.googleapis.com / fonts.gstatic.com (fonts), cdn.jsdelivr.net (Pico CSS), cdnjs.cloudflare.com (Font Awesome), appbe.endlesstesting.ai (A/B testing), static.cloudflareinsights.com (analytics). Total 6 domains, with 4 of them on the case-study and contact pages for CSS alone.

## Mobile notes
- Viewport meta is present and correct on all pages: `width=device-width,initial-scale=1`.
- No `touch-action: manipulation` was found, but modern browsers remove the 300 ms tap delay when a viewport meta is set, so this is not an issue.
- Lazy loading, srcset and image formats are not applicable (no `<img>` elements found).
- Lab runs are mobile-throttled, so the desktop gap was not measured.

## Conversion link
Reported in case studies (e.g. Google/Deloitte "Milliseconds Make Millions"), small mobile speed gains are linked to higher conversion rates. This site starts from a good baseline, so these changes protect the CTA click rather than rescue it. Prioritize consistency (no flicker or shift of the teardown CTA) over more speed work.

## Priority recommendations
**High:** none critical. Lab LCP and TBT are good on all pages.
**Medium:**
1. Remove duplicate Font Awesome and Figtree links and replace Pico / Font Awesome with inline CSS and SVG on case-study and contact (finding 1).
2. Make A/B SDK usage consistent across pages and confirm it does not move the CTA (finding 2).
**Low:**
3. Fix the font strategy to stabilise CLS on home (findings 3 and 5).
4. Cache HTML at the Cloudflare edge and update links that redirect (finding 4).

## Positive findings
- 26-34 KB transfer per page, 6-9 requests, no images to optimise.
- Brotli, Cloudflare CDN, HTTP/3, and preconnect hints are all in place.
- `font-display: swap` is used, and A/B script is deferred with no anti-flicker hiding.
- CLS is 0.000 on case-study and contact.
- Viewport meta is correct.
