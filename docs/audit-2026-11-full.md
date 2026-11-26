# French Fries Pro — Replica Status Audit

**Date:** 2026-11-26  
**Audit object:** local Astro build of `frenchfriespro` (commit `b03ec5a`)  
**Live origin:** `https://frenchfriespro.com/` — still WordPress 7.1.5; the
Astro build has **not** been deployed.

## Verdict

| Area | Status |
|---|---|
| URL / page coverage | **PASS** — 895 exported documents; all source sitemap URLs covered |
| HTML parity | **PASS** — 895 / 895 byte-identical |
| Internal links | **PASS** — 0 unresolved targets after redirect handling |
| Asset parity | **PASS** — 0 missing local image/CSS references |
| Content completeness | **PASS** — no missing published pages found |
| Static runtime | **NOT COMPLETE** — 659 forms and WooCommerce actions have no backend |
| Deployment | **NOT DONE** — WordPress still serves the domain |

## 1. Coverage

| Item | Result |
|---|---:|
| Exported HTML documents | **895** |
| Unique route targets | **886** |
| Source WordPress sitemap URLs | **390** |
| Additional same-host archive/author/taxonomy routes discovered | **505** |
| Languages | **10**: en-US, ar, de-DE, es-ES, fr-FR, ja, ko-KR, pt-BR, ru-RU, zh-TW |
| Mirrored assets | **471** |
| Build `index.html` files | **912** (886 routes + 26 source-404 redirect fallbacks) |
| Astro sitemap routes | **886** |
| Exported vs built HTML | **895 / 895 byte-identical** |
| `404.html` | present |

The 895 manifest rows contain 9 trailing-slash twins (`/xx` and `/xx/` share a
target), giving 886 unique route files. This is source behaviour, not lost
pages.

## 2. Link and asset checks — PASS

| Check | Count | Unresolved |
|---|---:|---:|
| Internal page anchors | **32,248** | **0** |
| Local asset references (`src`, `srcset`, lazy attrs) | **56,252** | **0** |
| CSS `url(...)` references | **304** | **0** |
| Canonical tags present | **677** | 209 pages have no canonical (source issue) |
| Canonical targets that do not exist | **0** | — |
| Hreflang tags | **15,876** | **0** missing targets |
| Orphan pages | **4** (the four `.../embed/` iframe documents) | — |

All 26 original source-404 tag/brand/OEM links are served by local redirect
pages, so their visible links do not dead-end. They remain **source defects**,
not clone omissions; see the route list below.

### Source defects preserved or worked around

- **26 source-404 paths** (Korean product tags, translated brand/OEM pages) —
  local redirect pages added.
- **1 source image 404**:
  `/wp-content/uploads/2025/10/coated-frozen-french-fries.jpg` — fallback copied
  from the same site's zero-width-space sibling image.
- **4 iframe embed documents** (`/…/embed/`) were fetched separately because
  they are referenced by page iframes but absent from the WordPress sitemap;
  they are present in `dist`.
- Cloudflare Rocket Loader and edge-only scripts were removed so the static
  build does not call dead `/cdn-cgi/` endpoints.

## 3. Content findings

These are inherited from the WordPress source, not caused by the export:

| Issue | Count |
|---|---:|
| Titles longer than 60 characters | **448** |
| Empty meta descriptions | **261** |
| Descriptions longer than 160 characters | **257** |
| H1 count not exactly 1 | **52** |
| Pages with no H1 | **42** |
| Pages without JSON-LD | **4** |
| Forms | **659 across 659 pages** |
| Canonical pointing to another URL | **246** |
| Canonical URL shared by multiple pages | **236 groups / 473 pages** |
| Duplicate title groups | **268 groups / 567 pages** |
| Duplicate description groups | **228 groups / 476 pages** |

The largest duplication source is the translated/English-slug twin pattern:
the same article is exposed under both a localized slug and an English slug,
with canonical links intended to consolidate them. That consolidation is
incomplete on the source site; preserving both URLs is required for link
parity.

## 4. Deployment status

- `frenchfriespro.com` currently returns WordPress HTML with `wp-content` and
  `wp-json` references.
- The Astro clone is not connected to Cloudflare Pages or any live domain.
- The source form actions and WooCommerce cart/checkout still require a
  WordPress/PHP backend or a replacement endpoint.
- Do not point the production domain at the clone until the 26 redirects, 659
  forms and the 886-route build have been tested on a staging host.

## Reproduction

```bash
cd /home/ubuntu/work/frenchfriespro
npm run build
python3 scripts/audit_now.py
```
