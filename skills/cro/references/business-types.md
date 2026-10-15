# Business Type Detection

The one list of business types. Every CRO skill uses this file; do not copy the
table elsewhere.

| Type | Detection signals | Main conversion | Plan template |
|------|-------------------|-----------------|---------------|
| **SaaS** | `/pricing`, `/features`, "free trial", "start free", "book a demo", `/docs`, `/integrations`, login link | Trial or demo signup | `saas.md` |
| **E-commerce** | `/products`, `/collections`, `/cart`, "add to cart", `Product` JSON-LD, prices, Shopify/WooCommerce markers | Purchase | `ecommerce.md` |
| **Lead Gen** | Prominent form, "get a quote", "book a call", phone number in header, form with 3+ fields | Form submit or call | `lead-gen.md` |
| **Subscription** | `/plans`, "subscribe", recurring price, monthly/annual toggle, membership tiers | Subscription start | `subscription.md` |
| **Local Service** | Street address, service area, "serving [city]", map embed, `LocalBusiness` schema | Call, booking, direction request | `local-service.md` |
| **Agency / B2B services** | `/case-studies`, `/portfolio`, client logos, "we helped", team page, industry pages | Contact or RFP | `lead-gen.md` |
| **Content / Media** | Article layout, bylines, dates, categories, newsletter prompts, ad slots | Newsletter or paid subscription | `subscription.md` |
| **Marketplace** | Buyer and seller language, listings, "sell", "post a listing", prominent search | Listing or first transaction | `generic.md` |
| **Non-profit** | "Donate", mission, impact numbers, volunteer calls | Donation | `generic.md` |

When several match, pick the primary type by the main conversion action and
note secondary types ("Primary: E-commerce, Secondary: Subscription").
If nothing matches with confidence, say so and use `generic.md`.
