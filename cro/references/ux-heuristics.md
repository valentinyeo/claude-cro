# UX Heuristics for Conversion Optimization

Evaluation frameworks for assessing user experience quality as it relates to
conversion rate. Use these heuristics to systematically identify friction
points, usability issues, and optimization opportunities.

---

## Nielsen's 10 Usability Heuristics (Conversion-Focused)

### 1. Visibility of System Status

The system should keep users informed about what is going on through
appropriate feedback within a reasonable time.

**Conversion Application:**
- Loading indicators during page transitions and form submissions
- Progress bars in multi-step checkout flows
- Cart item count updates after "add to cart"
- Form validation feedback (inline, real-time)
- Order status and confirmation pages
- Shipping/delivery tracking integration
- Clear indication of selected options (color, size, quantity)

**Severity Indicators:**
- Missing: No feedback after form submission or CTA click = Severity 4
- Delayed: Feedback appears but takes >2 seconds = Severity 3
- Ambiguous: Feedback present but unclear = Severity 2

---

### 2. Match Between System and Real World

The system should speak the users' language, with words, phrases, and concepts
familiar to the user, rather than system-oriented terms.

**Conversion Application:**
- CTA text uses action verbs the audience understands ("Get Started" not "Submit")
- Product descriptions use customer language, not internal jargon
- Navigation labels match user mental models
- Error messages explain the problem in plain language
- Pricing page uses familiar currency and formatting
- Category names match how customers think (not internal taxonomy)

**Severity Indicators:**
- Jargon-heavy CTAs or navigation = Severity 3
- Technical error messages ("Error 422") = Severity 3
- Unfamiliar terminology in key conversion paths = Severity 2

---

### 3. User Control and Freedom

Users often choose system functions by mistake and need a clearly marked
"emergency exit" to leave the unwanted state.

**Conversion Application:**
- Easy cart modification (remove, adjust quantity)
- Undo actions (remove from cart, clear form, undo filter)
- Back button works correctly in multi-step flows
- Easy unsubscribe from emails and notifications
- Guest checkout option (don't force account creation)
- Clear "cancel" options in modal dialogs
- Ability to edit order before final confirmation

**Severity Indicators:**
- No way to modify cart contents = Severity 4
- Forced account creation blocks checkout = Severity 4
- Back button breaks multi-step form = Severity 3
- No undo for destructive actions = Severity 3

---

### 4. Consistency and Standards

Users should not have to wonder whether different words, situations, or
actions mean the same thing.

**Conversion Application:**
- Consistent CTA styling across all pages (same color, style)
- Consistent navigation structure and placement
- Product card layout uniform across listings
- Pricing display format consistent (currency, decimal, period)
- Form styling and behavior consistent throughout
- Link styling distinguishable from regular text
- Header/footer consistent across all pages

**Severity Indicators:**
- CTA style changes between pages = Severity 3
- Inconsistent pricing display = Severity 3
- Navigation changes between sections = Severity 2
- Mixed button styles = Severity 2

---

### 5. Error Prevention

Even better than good error messages is a careful design that prevents a
problem from occurring in the first place.

**Conversion Application:**
- Form input constraints (email format, phone masking)
- Address autocomplete and validation
- Credit card type auto-detection
- Confirmation dialogs before irreversible actions
- Smart defaults that reduce errors
- Input type attributes (tel, email, number) for mobile keyboards
- Quantity limits on products to prevent over-ordering
- Out-of-stock items clearly marked (not discoverable at checkout)

**Severity Indicators:**
- No input validation until submission = Severity 3
- Stock issues discovered at checkout = Severity 4
- No confirmation before order placement = Severity 3
- Free-text fields where structured input is possible = Severity 2

---

### 6. Recognition Rather Than Recall

Minimize the user's memory load by making objects, actions, and options
visible.

**Conversion Application:**
- Recently viewed products accessible
- Persistent cart summary visible
- Search suggestions and autocomplete
- Breadcrumbs showing current location in site hierarchy
- Filter states clearly displayed and removable
- Product comparison tools
- Saved payment methods and addresses
- Visual product selectors (color swatches, size charts)

**Severity Indicators:**
- Users must remember product details from previous pages = Severity 3
- No search suggestions = Severity 2
- No breadcrumbs in deep navigation = Severity 2
- Cart contents not visible from main pages = Severity 2

---

### 7. Flexibility and Efficiency of Use

Accelerators unseen by the novice user may speed up interaction for expert
users.

**Conversion Application:**
- Quick-buy / buy-now buttons (skip cart)
- Saved payment methods and addresses for returning users
- Quick reorder functionality
- Keyboard shortcuts for power users
- Express checkout options (Apple Pay, Google Pay, PayPal)
- Quick add-to-cart from listing pages (not just PDP)
- Bulk ordering capability (B2B)
- Wishlist and saved-for-later functionality

**Severity Indicators:**
- No express payment options = Severity 2
- Returning users must re-enter all information = Severity 3
- No quick-buy option for repeat purchases = Severity 2

---

### 8. Aesthetic and Minimalist Design

Dialogues should not contain information that is irrelevant or rarely needed.
Every extra unit of information competes with the relevant units.

**Conversion Application:**
- Clean, uncluttered layout with clear visual hierarchy
- Single primary CTA per viewport (not competing CTAs)
- Hero section focused on value proposition (not cluttered with features)
- Whitespace used effectively to guide attention
- Only essential form fields shown
- Progressive disclosure for complex information
- Pop-ups and banners used sparingly
- No auto-playing video or audio

**Severity Indicators:**
- Multiple competing CTAs above the fold = Severity 3
- Cluttered hero with no clear focal point = Severity 3
- Unnecessary pop-ups on entry = Severity 3
- Information overload on product pages = Severity 2

---

### 9. Help Users Recognize, Diagnose, and Recover from Errors

Error messages should be expressed in plain language, precisely indicate the
problem, and constructively suggest a solution.

**Conversion Application:**
- Inline form validation with specific error messages
- Highlight the exact field with the error
- Suggest corrections ("Did you mean gmail.com?")
- Payment failure messages with clear next steps
- 404 pages with search and navigation options
- Out-of-stock alternatives suggested
- Session timeout warnings with save options

**Severity Indicators:**
- Generic "something went wrong" errors = Severity 4
- No indication which form field has the error = Severity 3
- Payment failures with no guidance = Severity 4
- 404 pages with no navigation = Severity 3

---

### 10. Help and Documentation

Even though it is better if the system can be used without documentation,
it may be necessary to provide help and documentation.

**Conversion Application:**
- FAQ section addressing purchase concerns
- Live chat or chatbot for real-time questions
- Tooltips on complex form fields
- Sizing guides and fit tools
- Shipping and return policy easily accessible
- Product comparison and buying guides
- Knowledge base or help center linked from key pages

**Severity Indicators:**
- No FAQ or help during checkout = Severity 2
- Complex product with no guidance = Severity 3
- No way to contact support during purchase flow = Severity 3
- Policies hidden or hard to find = Severity 2

---

## Mobile UX Principles

### Thumb Zone Optimization

On mobile devices, the natural thumb reach determines ease of interaction.

| Zone | Position | Design Recommendation |
|------|----------|----------------------|
| **Easy** | Bottom center of screen | Primary CTAs, key navigation |
| **OK** | Middle and sides | Secondary actions, content |
| **Hard** | Top corners | Non-critical elements, menu icon |

**CRO Implications:**
- Primary CTAs should be in the bottom half of the viewport on mobile.
- Sticky bottom CTAs are effective for long pages.
- Hamburger menus in the top-left are hardest to reach with right-hand use.
- Consider bottom navigation bars for mobile-first sites.

### Tap Target Sizes

| Element | Minimum Size | Recommended Size |
|---------|-------------|-----------------|
| **Buttons** | 44 x 44px | 48 x 48px |
| **Links (inline)** | 44px height with padding | 48px touch target |
| **Form inputs** | 44px height | 48-56px height |
| **Spacing between targets** | 8px minimum | 12px recommended |

**CRO Impact:** Undersized tap targets cause accidental taps and missed
interactions. Forms with small input fields have significantly higher
abandonment on mobile.

### Touch-Friendly Forms

- Use appropriate input types: `type="email"`, `type="tel"`, `type="number"`
- Enable autocomplete attributes: `autocomplete="email"`, `autocomplete="tel"`
- Avoid custom dropdowns that don't work with native mobile selectors
- Use date pickers optimized for mobile (native where possible)
- Set `inputmode` for numeric fields (`inputmode="numeric"`)
- Avoid placeholder-only labels (they disappear on focus)
- Make labels tap targets for their associated inputs

### Mobile Navigation Patterns

| Pattern | Best For | CRO Consideration |
|---------|----------|-------------------|
| **Bottom tab bar** | Apps, high-frequency navigation | Keeps key actions in thumb zone |
| **Hamburger menu** | Content-heavy sites | Hides navigation, reduces discoverability |
| **Sticky header** | E-commerce, content sites | Keeps brand + search + cart accessible |
| **Full-screen overlay** | Complex menus, filters | Clear focus but interrupts browsing |

### Viewport Considerations

- No horizontal scrolling (ever)
- Content readable without pinch-zooming
- Forms don't break when keyboard opens
- Fixed elements don't overlap content on small screens
- Images and videos resize properly
- Tables scroll horizontally or reflow to cards
- Modal dialogs are full-screen on mobile

---

## Form UX Best Practices (Luke Wroblewski)

### Single Column Layout
- Forms should be single-column on all devices.
- Side-by-side fields (e.g., first name / last name) are acceptable only when
  the fields are logically paired and short.
- Multi-column forms increase completion time by 15-30%.

### Label Placement

| Placement | Speed | Best For |
|-----------|-------|----------|
| **Top-aligned** | Fastest completion | Most forms, especially mobile |
| **Left-aligned** | Slower (eye movement) | Complex forms with many fields |
| **Inline/placeholder** | Problematic | Avoid — labels disappear on focus |
| **Floating labels** | Good compromise | Modern forms, space-constrained |

**Recommendation:** Use top-aligned or floating labels. Never use placeholder
text as the only label.

### Inline Validation

- Validate on blur (when user leaves the field), not on input.
- Show success indicators for correctly filled fields.
- Display errors next to the field, not in a summary at the top.
- Use specific error messages ("Please enter a valid email address" not
  "Invalid input").
- Don't validate while the user is still typing.

### Smart Defaults

- Pre-select the most common option (country, shipping method).
- Use geolocation for country/region when possible.
- Default to the most popular plan or option.
- Pre-fill returning user data from cookies or account.
- Set reasonable defaults for quantity (1, not 0).

### Field Masking and Formatting

- Auto-format phone numbers as the user types.
- Auto-format credit card numbers with spaces.
- Use input masking for dates and zip codes.
- Display the expected format as a hint (e.g., "MM/DD/YYYY").
- Auto-capitalize names and addresses.

### Progress Indication for Multi-Step Forms

- Show total steps and current position.
- Use a progress bar or step indicator.
- Allow users to go back to previous steps.
- Save progress between steps (don't lose data on back).
- Show a summary before final submission.

**Step Count Guidance:**
| Form Type | Ideal Steps | Maximum Steps |
|-----------|------------|---------------|
| Newsletter signup | 1 | 1 |
| Lead gen | 1-2 | 3 |
| Account creation | 1-2 | 2 |
| Checkout | 3-4 | 5 |
| Application | 3-5 | 7 |

---

## E-commerce UX Patterns

### Product Detail Page (PDP) Must-Haves

| Element | Priority | Notes |
|---------|----------|-------|
| High-quality product images (multiple angles) | Critical | Zoom capability, lifestyle shots |
| Clear pricing (with savings if applicable) | Critical | Strike-through for discounts |
| Prominent "Add to Cart" button | Critical | Above fold, high contrast |
| Product title and description | Critical | Scannable, benefit-oriented |
| Size/variant selector | Critical | Visual selectors preferred |
| Star rating and review count | High | Link to full reviews |
| Stock availability indicator | High | "In stock" or "Only X left" |
| Shipping information | High | Cost and estimated delivery |
| Return policy summary | High | Linked to full policy |
| Size guide / fit tool | High | For apparel/footwear |
| Product specifications | Medium | Collapsible or tabbed |
| Related/recommended products | Medium | "You might also like" |
| Social sharing buttons | Low | Don't compete with CTA |

### Cart Page Essentials

| Element | Priority | Notes |
|---------|----------|-------|
| Product thumbnails | Critical | Visual confirmation |
| Quantity adjustment | Critical | Easy +/- controls |
| Remove item option | Critical | Clear but not too prominent |
| Subtotal per item and total | Critical | Updated in real-time |
| Proceed to checkout CTA | Critical | Most prominent element |
| Continue shopping link | High | Secondary, less prominent |
| Shipping estimate | High | Before checkout if possible |
| Promo code field | High | Collapsible to avoid distraction |
| Trust badges | High | Security, payment, returns |
| Saved for later option | Medium | Alternative to removing |
| Cross-sell / upsell | Medium | Subtle, don't distract |

### Checkout Flow Best Practices

1. **Guest checkout required** — forced account creation causes 34% cart
   abandonment (Baymard).
2. **3-5 steps maximum** — shipping, payment, review, confirmation.
3. **Show order summary throughout** — persistent sidebar or collapsible.
4. **Multiple payment options** — credit card, PayPal, Apple Pay, Google Pay.
5. **Auto-fill and autocomplete** — reduce typing.
6. **Progress indicator** — show current step and remaining steps.
7. **Edit previous steps** — without losing entered data.
8. **Security indicators** — SSL badge, secure checkout messaging.
9. **Error recovery** — clear messages for payment failures.
10. **Order confirmation** — on-screen and via email.

### Search and Filter UX

| Element | Best Practice |
|---------|--------------|
| **Search bar** | Prominent, always visible, with autocomplete |
| **Search results** | Show product images, prices, ratings |
| **Filters** | Sidebar or top bar, multi-select, show result count |
| **Sort options** | Relevance, price, rating, newest, bestselling |
| **No results** | Suggest alternatives, check spelling, show popular items |
| **Filter state** | Clearly show active filters with easy removal |
| **Pagination** | Infinite scroll or "load more" preferred over pagination |

---

## Severity Rating Scale

Use this scale to rate every usability finding:

| Severity | Label | Definition | CRO Impact |
|----------|-------|------------|------------|
| **0** | Not a problem | Cosmetic only, no users affected | None |
| **1** | Cosmetic | Minor visual issue, users notice but aren't impacted | Negligible |
| **2** | Minor | Users are briefly confused but can recover easily | Low — slight friction |
| **3** | Major | Users struggle significantly, some may abandon | High — measurable conversion loss |
| **4** | Catastrophic | Users cannot complete the task, conversion blocked | Critical — conversions actively blocked |

### Severity Assignment Guidelines

Consider these factors when assigning severity:
- **Frequency:** How many users will encounter this issue?
- **Impact:** How much does it slow down or block the user?
- **Persistence:** Is it a one-time annoyance or ongoing frustration?
- **Location:** Is it on a high-traffic page or a rarely visited one?
- **Alternative paths:** Can users work around it?

| Location | Severity Modifier |
|----------|------------------|
| Homepage / hero | +1 severity (high traffic, first impression) |
| Checkout / payment | +1 severity (high-intent, conversion-critical) |
| Product page | Standard severity |
| About / informational | -1 severity (not directly conversion-path) |
| Footer / secondary | -1 severity (low visibility) |

---

## Accessibility and Conversion

Accessibility improvements often directly improve conversion rates because
they make the site more usable for everyone.

| Accessibility Issue | Conversion Impact |
|-------------------|------------------|
| Low color contrast | Users can't read CTAs or form labels |
| Missing alt text | Images don't communicate on slow connections |
| No keyboard navigation | Power users and assistive tech users blocked |
| Missing form labels | Screen reader users can't complete forms |
| No focus indicators | Tab navigation users lose their place |
| Auto-playing media | Users may leave immediately |
| Missing skip links | Repeated tab-through of navigation on every page |

**Quick Checks:**
- CTA button contrast ratio >= 4.5:1 (WCAG AA) or >= 3:1 (large text)
- All form fields have associated labels
- All images have meaningful alt text
- Page is navigable with keyboard alone
- Focus states are visible on interactive elements
