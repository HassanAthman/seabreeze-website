#!/usr/bin/env python3
"""Seabreeze website artwork.

All artwork is original, drawn here as SVG so it stays sharp, small and
follows the site's light and dark colours (it uses the CSS variables from
public/styles.css). Run `python3 tools/art.py` from the repo root to
re-insert the artwork into the pages between <!--art:NAME--> markers.
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"

# --------------------------------------------------------------- brand mark
def mark(size=32, wave="var(--bg)", bg="var(--sea)", sun="var(--sun)"):
    """Round badge: a sun rising over a sea wave, with a signal arc."""
    return (
        f'<svg viewBox="0 0 64 64" width="{size}" height="{size}" aria-hidden="true">'
        f'<circle cx="32" cy="32" r="31" fill="{bg}"/>'
        f'<path d="M20 35a12 12 0 0 1 24 0z" fill="{sun}"/>'
        f'<path d="M14 24a22 22 0 0 1 36 0" stroke="{wave}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".9"/>'
        f'<path d="M6 42c6.5-5 13-5 19.5 0s13 5 19.5 0 13-5 13-5" stroke="{wave}" stroke-width="5" fill="none" stroke-linecap="round"/>'
        f'<path d="M10 51c5.5-4 11-4 16.5 0s11 4 16.5 0 11-4 11-4" stroke="{wave}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".55"/>'
        "</svg>"
    )

def logo_file(dark_bg=False):
    ink = "#ffffff" if dark_bg else "#0d2a33"
    m = mark(64, wave="#ffffff" if not dark_bg else "#0a3d47", bg="#0b6e78" if not dark_bg else "#ffffff", sun="#f08a24")
    m = m.replace('<svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">', '<g>').replace("</svg>", "</g>")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 64" role="img" aria-label="Seabreeze 5G">'
        f"{m}"
        f'<text x="78" y="44" font-family="Bricolage Grotesque, Segoe UI, sans-serif" font-weight="800" font-size="36" fill="{ink}" letter-spacing="-0.5">Seabreeze</text>'
        '<rect x="262" y="14" width="62" height="38" rx="19" fill="#f08a24"/>'
        '<text x="293" y="42" text-anchor="middle" font-family="Bricolage Grotesque, Segoe UI, sans-serif" font-weight="800" font-size="26" fill="#3a1a00">5G</text>'
        "</svg>\n"
    )

# ------------------------------------------------------------ Kenya map
# Simplified, illustrative outline of Kenya (lon, lat). Not survey accurate.
KENYA = [
    (33.95, 4.22), (34.39, 4.62), (35.3, 5.15), (35.85, 4.65), (36.9, 4.42), (38.1, 3.62),
    (39.5, 3.45), (40.75, 4.0), (41.9, 3.98), (41.0, 2.8), (41.0, -0.85), (41.56, -1.68),
    (41.1, -1.95), (40.65, -2.35), (40.25, -2.65), (40.12, -3.2), (39.85, -3.7), (39.6, -4.15),
    (39.2, -4.68), (37.75, -3.65), (37.6, -3.0), (34.07, -1.0), (33.92, -0.45), (33.99, 0.23),
    (34.43, 0.85), (34.6, 1.2), (34.82, 1.85), (35.0, 2.45), (34.6, 3.3), (34.4, 3.75),
]
LAKE_VICTORIA = [(34.07, -1.0), (33.92, -0.45), (33.99, 0.12), (34.25, 0.05), (34.5, -0.22),
                 (34.78, -0.12), (34.62, -0.38), (34.35, -0.55), (34.2, -0.8)]
LAKE_TURKANA = [(35.95, 4.55), (36.25, 4.45), (36.35, 3.6), (36.6, 2.75), (36.55, 2.4),
                (36.38, 2.55), (36.15, 3.3), (35.95, 4.0)]

COAST = [(41.56, -1.68), (41.1, -1.95), (40.65, -2.35), (40.25, -2.65), (40.12, -3.2),
         (39.85, -3.7), (39.6, -4.15), (39.2, -4.68)]

TOWNS = {  # slug: (name, lon, lat, label side)
    "malindi": ("Malindi", 40.12, -3.22, "r"),
    "kilifi": ("Kilifi", 39.85, -3.63, "r"),
    "mombasa": ("Mombasa", 39.67, -4.05, "r"),
    "lamu": ("Lamu", 40.90, -2.27, "r"),
    "mpeketoni": ("Mpeketoni", 40.69, -2.39, "l"),
    "voi": ("Voi", 38.56, -3.40, "l"),
    "kisumu": ("Kisumu", 34.76, -0.09, "r"),
    "kakamega": ("Kakamega", 34.75, 0.28, "l", 4),
    "bungoma": ("Bungoma", 34.56, 0.56, "l", -5),
    "kapsabet": ("Kapsabet", 35.10, 0.20, "r"),
    "kapenguria": ("Kapenguria", 35.12, 1.24, "r"),
}

K = 46          # pixels per degree
X0, Y0 = 32.55, 5.5  # top left corner in lon/lat
W, H = 480, 480

def px(lon, lat):
    return round((lon - X0) * K, 1), round((Y0 - lat) * K, 1)

def poly(points):
    return "M" + " L".join(f"{x},{y}" for x, y in (px(*p) for p in points)) + "Z"

def kenya_map(highlight=None, links=True, labels=True, cls="kmap"):
    """Coverage map. highlight = town slug to emphasise (town pages)."""
    out = [f'<svg class="{cls}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="{cls}-t">'
           f'<title id="{cls}-t">Map of Kenya showing towns where Seabreeze agents work. Illustration, not to scale.</title>'
           '<defs><linearGradient id="kocean" x1="0" x2="1"><stop offset="0" stop-color="var(--sea)" stop-opacity="0"/>'
           '<stop offset="1" stop-color="var(--sea)" stop-opacity=".22"/></linearGradient>'
           '<pattern id="kdots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.1" fill="var(--sea)" opacity=".28"/></pattern></defs>'
           f'<path d="{poly(COAST + [(39.2, -6), (43.5, -6), (43.5, -0.2), (42.4, -0.45)])}" fill="url(#kocean)"/>']
    ox, oy = px(41.75, -4.25)
    out.append(f'<text x="{ox}" y="{oy}" class="ocean">Indian Ocean</text>')
    out.append(f'<path d="{poly(KENYA)}" fill="var(--surface)" stroke="var(--sea)" stroke-width="2" stroke-linejoin="round"/>')
    out.append(f'<path d="{poly(KENYA)}" fill="url(#kdots)"/>')
    for lake in (LAKE_VICTORIA, LAKE_TURKANA):
        out.append(f'<path d="{poly(lake)}" fill="var(--sea)" opacity=".35"/>')
    # coast and west clusters: soft halos
    for lon, lat, r in ((40.0, -3.2, 72), (34.85, 0.45, 64)):
        x, y = px(lon, lat)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--sun)" opacity=".10"/>')
    for slug, (name, lon, lat, side, *dy) in TOWNS.items():
        dy = dy[0] if dy else 0
        x, y = px(lon, lat)
        hq = slug == "malindi"
        on = highlight == slug
        dim = highlight and not on
        r = 7 if (hq or on) else 5
        g = []
        if hq or on:
            g.append(f'<circle class="pulse" cx="{x}" cy="{y}" r="{r+6}" fill="var(--sun)" opacity=".35"/>')
        g.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"var(--sun)" if not dim else "var(--muted)"}" stroke="var(--surface)" stroke-width="2.5"/>')
        if labels:
            tx = x + 11 if side == "r" else x - 11
            anchor = "start" if side == "r" else "end"
            weight = ' font-weight="700"' if (hq or on) else ""
            g.append(f'<text x="{tx}" y="{y + 4.5 + dy}" text-anchor="{anchor}"{weight}>{name}{" HQ" if hq and not highlight else ""}</text>')
        body = "".join(g)
        if links and not on:
            out.append(f'<a href="/airtel-5g/{slug}/" aria-label="Airtel 5G in {name}">{body}</a>')
        else:
            out.append(body)
    out.append("</svg>")
    return "".join(out)

# --------------------------------------------------------- Lipa Mdogo Mdogo
def mdogo_art():
    """Three M-Pesa payments drop into a meter that fills to 1,999 and lights the router."""
    coins = [("500", 0), ("700", 1), ("799", 2)]
    parts = ['<svg class="mdogo-art" viewBox="0 0 360 280" role="img" aria-labelledby="md-t">'
             '<title id="md-t">KES 500, 700 and 799 add up to 1,999 and the 5G line is renewed</title>'
             '<rect x="0" y="0" width="360" height="280" rx="22" fill="var(--sea-deep)"/>'
             
             # meter tube
             '<rect x="132" y="40" width="74" height="200" rx="37" fill="#0d4c57" stroke="#2f6670" stroke-width="3"/>'
             '<clipPath id="md-clip"><rect x="135" y="43" width="68" height="194" rx="34"/></clipPath>'
             '<g clip-path="url(#md-clip)">'
             '<rect class="md-fill" x="135" y="43" width="68" height="194" fill="url(#md-g)"/>'
             '<path class="md-wave" d="M120 52c10-6 20-6 30 0s20 6 30 0 20-6 30 0 20 6 30 0v12H120z" fill="#ffd2a3" opacity=".6"/>'
             "</g>"
             '<defs><linearGradient id="md-g" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#3fb3bd"/><stop offset="1" stop-color="#f08a24"/></linearGradient></defs>'
             '<g font-family="var(--mono)" font-size="11" fill="#9fc3c8">'
             '<text x="214" y="56">1,999</text><path d="M206 52h6" stroke="#9fc3c8"/>'
             '<text x="214" y="240">0</text><path d="M206 236h6" stroke="#9fc3c8"/></g>']
    for label, i in coins:
        y = 62 + i * 52
        parts.append(
            f'<g class="md-coin md-c{i}"><circle cx="64" cy="{y}" r="24" fill="var(--sun)"/>'
            f'<circle cx="64" cy="{y}" r="18" fill="none" stroke="#5a2c00" stroke-width="1.5" opacity=".35"/>'
            f'<text x="64" y="{y+5}" text-anchor="middle" font-family="var(--display)" font-weight="800" font-size="15" fill="#3a1a00">{label}</text>'
            f'<path d="M92 {y}c14 0 22 4 34 {14 - i*8}" stroke="#2f6670" stroke-width="2" stroke-dasharray="4 5" fill="none"/></g>')
    parts.append(
        '<text x="64" y="236" text-anchor="middle" font-family="var(--body)" font-size="12" fill="#9fc3c8">From KES 500</text>'
        # router
        '<g transform="translate(262 126)">'
        '<path class="md-sig" d="M14 -2a26 26 0 0 1 36 0M21 8a15 15 0 0 1 22 0" stroke="var(--sun)" stroke-width="4" fill="none" stroke-linecap="round"/>'
        '<rect x="8" y="18" width="48" height="74" rx="12" fill="#eef7f7"/>'
        '<rect x="18" y="32" width="28" height="4" rx="2" fill="#0b6e78"/><circle cx="32" cy="76" r="5" fill="#3fb3bd"/>'
        '<rect x="0" y="100" width="64" height="26" rx="13" fill="#3fb3bd"/>'
        '<text x="32" y="118" text-anchor="middle" font-family="var(--display)" font-weight="800" font-size="13" fill="#04252b">Renewed</text></g>'
        '<path d="M212 150h40" stroke="#f08a24" stroke-width="3" stroke-linecap="round"/><path d="M246 143l8 7-8 7" stroke="#f08a24" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>")
    return "".join(parts)

# ----------------------------------------------------------------- agents
def agents_art():
    """A Shujaa agent network: one router, agents around it, earnings badges."""
    people = [(70, 70), (250, 56), (300, 170), (196, 236), (54, 196)]
    p = ['<svg class="agents-art" viewBox="0 0 360 290" role="img" aria-labelledby="ag-t">'
         '<title id="ag-t">Seabreeze Shujaa agents connected to clients and earning on every renewal</title>'
         '<circle cx="180" cy="145" r="118" fill="none" stroke="#1f5a64" stroke-width="2" stroke-dasharray="3 7"/>'
         '<circle cx="180" cy="145" r="72" fill="#0d4c57"/>']
    for x, y in people:
        p.append(f'<path d="M180 145L{x} {y}" stroke="#2f6670" stroke-width="2"/>')
    p.append('<g transform="translate(156 108)"><path d="M6 6a26 26 0 0 1 36 0M13 16a15 15 0 0 1 22 0" stroke="#f5a04a" stroke-width="4" fill="none" stroke-linecap="round"/>'
             '<rect x="6" y="24" width="36" height="52" rx="10" fill="#eef7f7"/><rect x="15" y="34" width="18" height="3.5" rx="1.7" fill="#0b6e78"/><circle cx="24" cy="64" r="4" fill="#3fb3bd"/></g>')
    shirts = ["#f08a24", "#3fb3bd", "#f5c06b", "#eef7f7", "#3fb3bd"]
    for (x, y), c in zip(people, shirts):
        p.append(f'<g><circle cx="{x}" cy="{y}" r="30" fill="#0a3d47" stroke="#2f6670" stroke-width="2"/>'
                 f'<circle cx="{x}" cy="{y-8}" r="9" fill="#c98b5e"/>'
                 f'<path d="M{x-16} {y+20}a16 14 0 0 1 32 0z" fill="{c}"/></g>')
    for (x, y), t in zip([(108, 32), (290, 108), (128, 262)], ["+ KES", "+ KES", "+ KES"]):
        p.append(f'<g><rect x="{x-26}" y="{y-13}" width="52" height="26" rx="13" fill="#f08a24"/>'
                 f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="var(--display)" font-weight="800" font-size="13" fill="#3a1a00">{t}</text></g>')
    p.append("</svg>")
    return "".join(p)

# ------------------------------------------------------------- small icons
def why_icons():
    return {
        "phone": '<svg class="why-ico" viewBox="0 0 48 48" aria-hidden="true"><rect x="14" y="4" width="20" height="40" rx="5" fill="var(--sea)"/><rect x="17.5" y="9" width="13" height="11" rx="1.5" fill="var(--screen)"/><g fill="var(--bg)"><circle cx="19.5" cy="26" r="1.8"/><circle cx="24" cy="26" r="1.8"/><circle cx="28.5" cy="26" r="1.8"/><circle cx="19.5" cy="31" r="1.8"/><circle cx="24" cy="31" r="1.8"/><circle cx="28.5" cy="31" r="1.8"/><circle cx="19.5" cy="36" r="1.8"/><circle cx="24" cy="36" r="1.8"/><circle cx="28.5" cy="36" r="1.8"/></g><circle cx="38" cy="10" r="7" fill="var(--sun)"/><path d="M35 10l2 2 4-4" stroke="var(--sun-ink)" stroke-width="2" fill="none" stroke-linecap="round"/></svg>',
        "bell": '<svg class="why-ico" viewBox="0 0 48 48" aria-hidden="true"><path d="M6 10a4 4 0 0 1 4-4h22a4 4 0 0 1 4 4v14a4 4 0 0 1-4 4H18l-8 7v-7a4 4 0 0 1-4-4z" fill="var(--sea)"/><rect x="11" y="12" width="18" height="3" rx="1.5" fill="var(--bg)"/><rect x="11" y="18" width="12" height="3" rx="1.5" fill="var(--bg)"/><path d="M33 26a7 7 0 0 1 14 0v6l2 4H31l2-4z" fill="var(--sun)"/><circle cx="40" cy="39.5" r="2.5" fill="var(--sun)"/></svg>',
        "person": '<svg class="why-ico" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="17" r="9" fill="var(--sea)"/><path d="M8 44a16 15 0 0 1 32 0z" fill="var(--sea)"/><path d="M13 19a11 11 0 0 1 22 0" stroke="var(--sun)" stroke-width="3" fill="none"/><rect x="10" y="17" width="5" height="9" rx="2.5" fill="var(--sun)"/><rect x="33" y="17" width="5" height="9" rx="2.5" fill="var(--sun)"/><path d="M35.5 26c0 4-3 6-7 6" stroke="var(--sun)" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg>',
    }

def sms_art():
    return ('<svg class="sms-art" viewBox="0 0 320 200" role="img" aria-labelledby="sm-t"><title id="sm-t">A phone with SMS switches for reminders and offers</title>'
            '<rect width="320" height="200" rx="20" fill="var(--sea-deep)"/>'
            '<rect x="34" y="22" width="96" height="170" rx="16" fill="#1d2326"/><rect x="42" y="36" width="80" height="128" rx="6" fill="#c9d8b4"/>'
            '<rect x="50" y="46" width="56" height="20" rx="8" fill="#0b6e78"/><rect x="66" y="74" width="48" height="20" rx="8" fill="#f08a24"/><rect x="50" y="102" width="50" height="20" rx="8" fill="#0b6e78"/>'
            '<g font-family="var(--body)" font-size="15" fill="#e6f2f3">'
            '<text x="156" y="68">Reminders</text><text x="156" y="122">Offers</text></g>'
            '<rect x="240" y="52" width="50" height="26" rx="13" fill="#3fb3bd"/><circle cx="277" cy="65" r="10" fill="#fff"/>'
            '<rect x="240" y="106" width="50" height="26" rx="13" fill="#2f6670"/><circle cx="253" cy="119" r="10" fill="#9fc3c8"/>'
            '<text x="156" y="168" font-family="var(--body)" font-size="12" fill="#9fc3c8">Receipts always sent</text></svg>')

# ---------------------------------------------------------------- patching
def put(html, name, content):
    pat = re.compile(rf"<!--art:{name}-->.*?<!--/art:{name}-->", re.S)
    block = f"<!--art:{name}-->{content}<!--/art:{name}-->"
    if not pat.search(html):
        raise SystemExit(f"marker art:{name} missing")
    return pat.sub(lambda m: block, html)

def brand_link():
    return mark(32) + "\n      <span>Seabreeze <b class=\"g5\">5G</b></span>"

def main():
    (PUB / "brand").mkdir(exist_ok=True)
    (PUB / "brand" / "logo.svg").write_text(logo_file())
    (PUB / "brand" / "logo-white.svg").write_text(logo_file(dark_bg=True))
    mark_file = mark(64, wave="#ffffff", bg="#0b6e78", sun="#f08a24").replace(
        '<svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">')
    (PUB / "favicon.svg").write_text(mark_file + "\n")
    (PUB / "brand" / "mark.svg").write_text(mark_file + "\n")

    icons = why_icons()
    pages = sorted(PUB.rglob("*.html"))
    for page in pages:
        html = page.read_text()
        orig = html
        if "<!--art:brand-->" in html:
            html = put(html, "brand", brand_link())
        if "<!--art:fbrand-->" in html:
            html = put(html, "fbrand", mark(40))
        if "<!--art:kenya-->" in html:
            html = put(html, "kenya", kenya_map())
        if "<!--art:mdogo-->" in html:
            html = put(html, "mdogo", mdogo_art())
        if "<!--art:agents-->" in html:
            html = put(html, "agents", agents_art())
        if "<!--art:sms-->" in html:
            html = put(html, "sms", sms_art())
        for k, v in icons.items():
            if f"<!--art:why-{k}-->" in html:
                html = put(html, f"why-{k}", v)
        m = re.search(r"<!--art:town-(\w+)-->", html)
        if m:
            html = put(html, f"town-{m.group(1)}", kenya_map(highlight=m.group(1), links=False, cls="kmap kmap-town"))
        if html != orig:
            page.write_text(html)
            print("updated", page.relative_to(ROOT))

if __name__ == "__main__":
    main()
