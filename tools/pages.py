#!/usr/bin/env python3
"""Build the area pages (public/airtel-5g/SLUG/) from tools/coverage.py and
refresh the shared footer, coverage list, structured data and sitemap.

Town pages marked keep=True (Malindi, Mpeketoni, Voi) are hand written and
only get the shared parts refreshed. Run `python3 tools/art.py` afterwards
to draw the maps.
"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from coverage import AREAS, GROUPS, chip_label

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://seabreezedata.co.ke"
TEMPLATE = PUB / "airtel-5g" / "voi" / "index.html"

def join(items):
    return ", ".join(items[:-1]) + " and " + items[-1] if len(items) > 1 else items[0]

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")

NAV = [("/#renew", "Renew"), ("/get-airtel-5g/", "Get 5G"), ("/lipa-mdogo-mdogo/", "Lipa Mdogo Mdogo"),
       ("/support/", "Support"), ("/sms/", "SMS alerts"), ("/about/", "About us"), ("/contact/", "Contact")]
MENU_BTN = ('<button class="menu-btn" type="button" aria-label="Menu" aria-expanded="false" aria-controls="mainnav">'
            '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" '
            'stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg></button>')
FOOT_COLS = [
    ("Pay and renew", [("/renew-airtel-5g/", "Renew on Paybill 4129691"), ("/lipa-mdogo-mdogo/", "Lipa Mdogo Mdogo"),
                       ("/get-airtel-5g/", "Get Airtel 5G at home"), ("/#get5g", "Packages and prices")]),
    ("Help", [("/support/", "Help centre"), ("/support/#change-wifi-password", "Change your WiFi name and password"),
              ("/support/#paid-no-internet", "Paid but no internet"), ("/support/#check-expiry", "Check your expiry date"),
              ("/update-details/", "Update your details"), ("/sms/", "SMS reminders: join or stop"), ("/#faq", "Common questions")]),
    ("Company", [("/about/", "About us"), ("/about/#services", "Our services"), ("/#coverage", "Where we work"),
                 ("/contact/", "Contact us"), ("/contact/#float", "Airtel Money float"), ("/we-are-hiring/", "We are hiring")]),
]

def nav_html(path):
    """Main menu, the same on every page; the current page is marked."""
    items = []
    for href, label in NAV:
        cls = ' class="nav-sms"' if href == "/sms/" else ""
        cur = ' aria-current="page"' if href == path else ""
        items.append(f'<a{cls} href="{href}"{cur}>{label}</a>')
    return '<nav class="links" id="mainnav" aria-label="Main">\n      ' + "".join(items) + "\n    </nav>"

def footer_html():
    cols = "".join(f'<nav class="fcol" aria-label="{h}"><b>{h}</b>' + "".join(f'<a href="{u}">{t}</a>' for u, t in links) + "</nav>"
                   for h, links in FOOT_COLS)
    links = "".join(f'<a href="/airtel-5g/{s}/">Airtel 5G {chip_label(s).replace(" (head office)", "")}</a>'
                    for _g, slugs in GROUPS for s in slugs)
    return ('<!--foot--><div>Head office: Malindi, Kilifi County. Agents across the Coast, Nairobi, the Rift Valley and western Kenya.</div>\n'
            f'    <div class="fcols">{cols}</div>\n'
            f'    <div style="flex-basis:100%"><nav aria-label="Areas">{links}<a href="/renew-airtel-5g/">How to renew Airtel 5G</a>'
            '<a href="/support/">Help centre</a><a href="/about/">About us</a><a href="/contact/">Contact us</a></nav></div><!--/foot-->')

def coverage_html():
    rows = []
    for g, slugs in GROUPS:
        chips = "".join(f'<a{" class=\"hq\"" if s == "malindi" else ""} href="/airtel-5g/{s}/">{esc(chip_label(s))}</a>' for s in slugs)
        rows.append(f'<div class="cgroup"><h3>{g}</h3><div class="towns">{chips}</div></div>')
    return "".join(rows)

def area_served():
    names = []
    for _g, slugs in GROUPS:
        for s in slugs:
            a = AREAS[s]
            names.append(a["name"] + " County" if a["kind"] == "county" else a["name"])
    return names + ["Kenya"]

def shared(html, path="/"):
    """Menu, footer, coverage list and areaServed, on every page."""
    if "<!--foot-->" in html:
        html = re.sub(r'<!--foot-->.*?<!--/foot-->', lambda m: footer_html(), html, flags=re.S)
    else:
        html = re.sub(r'<div>Head office: Malindi.*?</nav></div>', lambda m: footer_html(), html, flags=re.S)
    html = re.sub(r'<nav class="links"[^>]*>.*?</nav>', lambda m: nav_html(path), html, flags=re.S)
    if 'class="menu-btn"' not in html:
        html = re.sub(r'(<a class="btn btn-sun btn-sm"[^>]*>[^<]*</a>)', lambda m: m.group(1) + "\n    " + MENU_BTN, html, count=1)
    html = re.sub(r'<!--cov-->.*?<!--/cov-->', lambda m: f"<!--cov-->{coverage_html()}<!--/cov-->", html, flags=re.S)
    html = re.sub(r'"areaServed": \[[^\]]*\]', lambda m: '"areaServed": ' + json.dumps(area_served()), html)
    return html

def county_page(slug, tpl):
    a = AREAS[slug]
    name, towns = a["name"], a["towns"]
    place = a.get("title_place", f"{name} County")
    whole = f"the whole of {name} County"
    title = f"Airtel 5G Home Internet in {place} | Seabreeze 5G"
    desc = (f"Airtel 5G Smart Connect home WiFi across {whole}: {', '.join(towns[:4])} and more. "
            "From KES 1,999 per month, unlimited data. Renew on M-Pesa Paybill 4129691.")
    lead = (f"Unlimited home and office WiFi across {whole}, including {join(towns)}. "
            "Set up by a Seabreeze agent near you. Renew any time on M-Pesa Paybill 4129691.")
    faq = [
        (f"Is Airtel 5G available in {name} County?",
         f"Yes. Our agents cover {whole}, including {join(towns[:5])}. Send your estate and nearest landmark on WhatsApp "
         "and we confirm coverage before you pay anything. The router also works in 4G areas."),
        (f"How much is Airtel 5G home internet in {name} County?",
         "KES 1,999 for 15 Mbps or KES 2,999 for 30 Mbps every 30 days, with unlimited data (1,000 GB fair use). "
         "90 and 180-day plans are cheaper per month and have no connection fee."),
        (f"How do I renew Airtel 5G in {name} County?",
         "M-Pesa, Lipa na M-Pesa, Pay Bill, business number 4129691, account number = your Airtel 5G line number, "
         "then your package amount. Any phone works."),
    ]
    h1_place = (f"<em>{esc(place.split(' and ')[0])}</em> and {esc(place.split(' and ')[1])} County"
                if "title_place" in a else f"<em>{esc(name)}</em> County")
    wa = f"https://wa.me/254734782203?text=Hi%20Seabreeze,%20I%20want%20Airtel%205G%20at%20home%20in%20{name.replace(' ', '%20')}%20County."
    url = f"{SITE}/airtel-5g/{slug}/"

    head_end = tpl.index("<main id=\"top\">")
    foot_start = tpl.index("</main>")
    head, foot = tpl[:head_end], tpl[foot_start:]
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", head)
    for key in ("description", "og:description"):
        head = re.sub(rf'(<meta (?:name|property)="{key}" content=")[^"]*"', lambda m: m.group(1) + esc(desc) + '"', head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda m: m.group(1) + esc(title) + '"', head)
    head = head.replace(f"{SITE}/airtel-5g/voi/", url).replace("/og/town-voi.png", f"/og/town-{slug}.png")
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faq]}
    head = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "FAQPage".*?</script>',
                  lambda m: '<script type="application/ld+json">' + json.dumps(faq_ld) + "</script>", head, flags=re.S)
    head = re.sub(r'\n?<link rel="alternate" hreflang=[^>]+>', "", head)
    chips = "".join(f"<span>{esc(t)}</span>" for t in towns)
    note = f'<p style="color:var(--muted);margin-top:12px">{esc(a["note"])}</p>' if a.get("note") else ""
    body = f'''<main id="top">
<section class="hero">
  <div class="wrap">
    <div>
      <div class="crumbs"><a href="/">Home</a> / <a href="/#coverage">Coverage</a> / {esc(name)} County</div>
      <div class="eyebrow" style="color:var(--sun)">Whole of {esc(name)} County</div>
      <h1 style="margin-top:12px">Airtel 5G home internet in {h1_place}</h1>
      <p class="lead">{esc(lead)}</p>
      <div class="ctas">
        <a class="btn btn-sun" href="{wa}" target="_blank" rel="noopener">Check coverage on WhatsApp</a>
        <a class="btn btn-ghost" href="/renew-airtel-5g/">How to renew</a>
      </div>
    </div>
    <div class="town-map"><!--art:area-{slug}--><!--/art:area-{slug}--></div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="eyebrow">Areas we cover</div>
    <h2 style="margin-top:8px">All of {esc(name)} County</h2>
    <div class="areas">{chips}</div>
    {note}
    <p style="color:var(--muted);margin-top:12px">Your area not listed? It is still covered. Send us your estate on WhatsApp and we check the signal before you pay.</p>
  </div>
</section>
<section style="padding-top:0">
  <div class="wrap">
    <div class="eyebrow">Packages in {esc(name)} County</div>
    <h2 style="margin-top:8px">Same Airtel prices, local help</h2>
'''
    plans_start = tpl.index('    <div class="plans"')
    plans_end = tpl.index("</section>", plans_start)
    body += tpl[plans_start:plans_end] + "</section>\n"
    body += f'''<section id="faq" style="padding-top:0">
  <div class="wrap">
    <h2>Questions from {esc(name)} County</h2>
    <div class="faq">
'''
    for i, (q, t) in enumerate(faq):
        body += f'      <details{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(t)}</p></details>\n'
    body += "    </div>\n  </div>\n</section>\n"
    return head + body + foot

def sitemap():
    urls = ["/", "/get-airtel-5g/", "/renew-airtel-5g/", "/lipa-mdogo-mdogo/", "/sms/", "/contact/", "/we-are-hiring/", "/update-details/", "/support/", "/about/"] + [f"/airtel-5g/{s}/" for _g, ss in GROUPS for s in ss]
    langs = [p.name for p in PUB.iterdir() if p.is_dir() and p.name in ("sw", "it")]
    translated = []
    for lang in langs:
        for u in urls:
            if (PUB / lang / u.strip("/") / "index.html").exists() or (u == "/" and (PUB / lang / "index.html").exists()):
                translated.append(f"/{lang}{u}")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls + translated:
        lines.append(f"  <url><loc>{SITE}{u}</loc><lastmod>2026-11-25</lastmod></url>")
    lines.append("</urlset>")
    (PUB / "sitemap.xml").write_text("\n".join(lines) + "\n")

def main():
    tpl = TEMPLATE.read_text()
    for slug, a in AREAS.items():
        out = PUB / "airtel-5g" / slug / "index.html"
        if a.get("keep"):
            html = out.read_text()
            html = re.sub(r"<!--art:town-([\w-]+)-->.*?<!--/art:town-\1-->", lambda m: f"<!--art:area-{m.group(1)}--><!--/art:area-{m.group(1)}-->", html, flags=re.S)
        else:
            html = county_page(slug, tpl)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
    for f in PUB.rglob("*.html"):
        if f.parts[len(PUB.parts)] in ("sw", "it"):
            continue
        h = f.read_text()
        rel = f.relative_to(PUB).as_posix()
        n = shared(h, "/" + rel[: -len("index.html")] if rel.endswith("index.html") else "")
        if n != h:
            f.write_text(n)
    sitemap()
    print("area pages:", len(AREAS))

if __name__ == "__main__":
    main()
