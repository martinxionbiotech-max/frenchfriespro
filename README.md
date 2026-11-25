# French Fries Pro — Astro static replica

Static Astro export of the public WordPress/WooCommerce site
`https://frenchfriespro.com` (WordPress 7.1.5, WooCommerce, TranslatePress).

## Coverage

- **895 exported HTML documents** (including internal archive/tag pages found by
  following links).
- **886 unique sitemap routes** after collapsing language-root slash variants.
- **10 languages**: `en-US`, `ru-RU`, `pt-BR`, `es-ES`, `zh-TW`, `fr-FR`,
  `de-DE`, `ar`, `ja`, `ko-KR`.
- **471 mirrored assets** under `public/`: CSS, JS, images, fonts and flags.
- Exact full-page HTML: Astra/GeneratePress-style theme header/footer, WooCommerce
  templates, inline CSS and original page markup are preserved.
- Internal anchors checked: **35,643**, with **0 unresolved page/asset targets**
  and **0 missing image sources** after local redirects/fallbacks.
- `npm audit`: **0 vulnerabilities**.

## Build

```bash
npm install
npm run build
```

Output: `dist/`.

## Structure

- `src/html/` — full source HTML documents.
- `src/data/pages.json` — route/file/source/language manifest.
- `src/pages/index.astro` and `src/pages/[...slug].astro` — Astro renderer.
- `public/` — assets, `robots.txt`, redirect fallbacks.
- `scripts/extract.py` — asset/link localisation.
- `scripts/crawl_missing.py` — discovers archive/tag pages not present in Rank Math sitemaps.

## Source defects and static limits

- The source image `/wp-content/uploads/2025/10/coated-frozen-french-fries.jpg`
  returns 404. Its same-site zero-width-space sibling image was copied as a
  fallback so the page does not show a broken image.
- The source has 26 broken tag/brand/OEM links (mostly Korean product-tag URLs
  and translated manufacturer pages). These are preserved as static redirect
  pages to the nearest language home/product page.
- Contact/inquiry forms and WooCommerce actions still use the original
  WordPress/WooCommerce AJAX markup; a static host has no PHP backend, so form
  submission and cart/checkout need a separate endpoint or a hosted backend.
- WordPress REST/feed endpoints are not part of the static runtime.
- The site is exported as published public pages; private drafts/orders/customer
  data are not included.

## URL parity

- Source sitemap URLs: **390**.
- Discovered internal/archive URLs: **505** (total exported documents 895).
- Unique sitemap routes: **886** (nine language roots exist with and without a
  trailing slash in the source data and collapse to the same file).
- 26 source-broken link targets are served by local redirect pages.
