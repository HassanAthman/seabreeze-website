# Seabreeze Data Ventures website

Public website for Seabreeze Data Ventures Ltd (Malindi, Kenya), an authorised Airtel Kenya Enterprise Solution Partner. It is a plain static site with no build step, hosted on Cloudflare Workers (static assets). The site files live in `public/`.

## Pages

| Path | Purpose |
| --- | --- |
| `/` | Home: renew on Paybill 4129691, offers, packages, services, coverage, enquiry form (opens WhatsApp), FAQ |
| `/renew-airtel-5g/` | "How to pay Airtel 5G with M-Pesa" page for search traffic |
| `/airtel-5g/<town>/` | One page per town where Seabreeze has agents |
| `404.html` | Not-found page |

Shared files: `styles.css`, `app.js`, `favicon.svg`, `og.png` (link preview image), `sitemap.xml`, `robots.txt`, `_headers` (Cloudflare security and caching headers).

## Deploying on Cloudflare

The site is served by the Cloudflare Pages project `seabreeze-management`, connected to this repository. `wrangler.jsonc` sets its build output directory to `public/` (Cloudflare reads it from the file, so the dashboard field is locked). There is no build command. Every merge to `main` deploys automatically and each pull request gets a preview link.

Custom domains `seabreezedata.co.ke` and `www.seabreezedata.co.ke` are added under the project's Custom domains tab.

If Cloudflare shows "This project is disconnected from your Git account", reinstall or reconfigure the Cloudflare Workers and Pages app in GitHub (Settings > Applications) so it can access this repository.

## Domain

All page addresses (canonical links, sitemap, share links, Google data) use `https://seabreezedata.co.ke`. If the domain ever changes, replace that text in every file and resubmit `sitemap.xml` in Google Search Console.

## Things to keep current

- Offer text (Black November runs 24 November to 31 December 2026): home page and town pages.
- Package prices: home page, town pages and the Google data in each page's head.
- Contact numbers: WhatsApp Business 0720 499 691, office 0782 998 842.
