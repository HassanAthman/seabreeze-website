# Seabreeze Data Ventures website

Public website for Seabreeze Data Ventures Ltd (Malindi, Kenya), an authorised Airtel Kenya Enterprise Solution Partner. It is a plain static site with no build step, hosted on Cloudflare Pages. The site files live in `public/`.

## Pages

| Path | Purpose |
| --- | --- |
| `/` | Home: renew on Paybill 4129691, offers, packages, services, coverage, enquiry form (opens WhatsApp), FAQ |
| `/renew-airtel-5g/` | "How to pay Airtel 5G with M-Pesa" page for search traffic |
| `/airtel-5g/<town>/` | One page per town where Seabreeze has agents |
| `/update-details/` | Clients send their 5G line, name and SMS phone; staff verify and approve in CBriz > Website Approvals |
| `404.html` | Not-found page |

Shared files: `styles.css`, `app.js`, `favicon.svg`, `og.png` (link preview image), `sitemap.xml`, `robots.txt`, `_headers` (Cloudflare security and caching headers).

## Deploying on Cloudflare

The site is served by the Cloudflare Pages project `seabreeze-management`, connected to this repository. `wrangler.jsonc` sets its build output directory to `public/` (Cloudflare reads it from the file, so the dashboard field is locked). There is no build command. Every merge to `main` deploys automatically and each pull request gets a preview link.

Custom domains `seabreezedata.co.ke` and `www.seabreezedata.co.ke` are added under the project's Custom domains tab.

If Cloudflare shows "This project is disconnected from your Git account", reinstall or reconfigure the Cloudflare Workers and Pages app in GitHub (Settings > Applications) so it can access this repository.

## SMS preferences form

`/sms/` lets clients join or stop renewal reminders and offers. It posts to `functions/api/sms-preferences.js` (a Pages Function), which writes to the shared CBriz D1 database through the `DB` binding in `wrangler.jsonc`. The tables come from cbriz-dashboard `migrations/007_sms_preferences.sql`, which must be run in the D1 console before this goes live. The cbriz-sms-sender worker checks `sms_preferences` before every reminder or marketing SMS. Payment receipts are always sent.

## Update details form

`/update-details/` (also `/sw/` and `/it/`) posts to `functions/api/update-details.js`, which saves the client's line, name and SMS phone in `website_client_updates` (cbriz-dashboard `migrations/012_website_client_updates.sql`, run it in the D1 console first) and queues an SMS alert to the management phone (0782 998 842) through `sms_outbox`. Nothing in the client database changes until staff approve it in CBriz > Website Approvals. A link `?line=0712345678` pre-fills the line.

## Domain

All page addresses (canonical links, sitemap, share links, Google data) use `https://seabreezedata.co.ke`. If the domain ever changes, replace that text in every file and resubmit `sitemap.xml` in Google Search Console.

## Things to keep current

- Offer text (Black November runs 24 November to 31 December 2026): home page and town pages.
- Package prices: home page, town pages and the Google data in each page's head.
- Contact numbers: WhatsApp Business 0782 998 842, office 0782 998 842.

## Artwork

All artwork is original and drawn as SVG in `tools/art.py` (logo, coverage
map, Lipa Mdogo Mdogo meter, agent network, icons). It uses the site's
colour variables, so it follows light and dark mode. After changing it, run
`python3 tools/art.py` to re-insert it into the pages between
`<!--art:NAME-->` markers.

Share images (`public/og/*.png`, shown when a page link is posted on
WhatsApp, Facebook or X) are made by `tools/cards.py`, which also makes
WhatsApp status and post cards and Google Business Profile images:

    python3 tools/cards.py /tmp/cards && node tools/render.js /tmp/cards

Copy `/tmp/cards/og/NAME_1200x630.png` to `public/og/NAME.png` to update
the site.

## Coverage areas and languages

- `tools/coverage.py` lists every county and town page, the map pins and
  the homepage groups. Add an area there.
- `i18n/sw.json` and `i18n/it.json` hold the Kiswahili and Italian text,
  keyed by the English text. `_patterns` translates the generated area pages.
- After any change, run `tools/build.sh`. It regenerates the area pages,
  maps, `/sw/` and `/it/` pages and the sitemap, and stops if an English
  sentence has no translation (`python3 tools/i18n.py --missing` lists them).
