#!/usr/bin/env python3
"""Share images: link previews (og), WhatsApp status and post cards, and
Google Business Profile images.

Writes one HTML file per image into a folder; tools/render.js turns each
into a PNG of the size in its name. Usage:
    python3 tools/cards.py OUT_DIR && node tools/render.js OUT_DIR
"""
import sys, pathlib, html
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import art

VARS = ("--bg:#eef7f7;--surface:#ffffff;--ink:#0d2a33;--muted:#9aa9ad;--line:#d5e2e3;--sea:#0b6e78;"
        "--sea-deep:#0a3d47;--sun:#f08a24;--sun-ink:#3a1a00;--screen:#c9d8b4;--screen-ink:#1f2a14;"
        "--display:'Bricolage Grotesque',sans-serif;--body:'Inter',sans-serif;--mono:'JetBrains Mono',monospace")
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800'
         '&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@700&display=swap">')

def logo(color="#fff", size=1.0):
    m = art.mark(int(56 * size), wave="#0a3d47", bg="#ffffff", sun="#f08a24")
    return (f'<div class="logo" style="font-size:{34*size}px;color:{color}">{m}<span>Seabreeze</span>'
            f'<b>5G</b></div>')

BASE_CSS = """
*{box-sizing:border-box;margin:0}
html,body{width:100%;height:100%}
body{%VARS%;font-family:var(--body);background:var(--sea-deep);color:#eef7f7;overflow:hidden;position:relative}
.logo{display:flex;align-items:center;gap:.4em;font-family:var(--display);font-weight:800;letter-spacing:-.01em}
.logo b{font-size:.62em;background:var(--sun);color:var(--sun-ink);border-radius:999px;padding:.18em .5em}
h1{font-family:var(--display);font-weight:800;letter-spacing:-.02em;line-height:1.02}
h1 em{font-style:normal;color:var(--sun)}
.sub{color:#c3dcdf;line-height:1.35}
.pill{display:inline-flex;align-items:center;gap:.5em;background:var(--sun);color:var(--sun-ink);font-family:var(--display);font-weight:800;border-radius:999px;padding:.35em .9em}
.mono{font-family:var(--mono);font-weight:700;letter-spacing:.02em}
.waves{position:absolute;left:0;right:0;bottom:0;opacity:.18}
.glow{position:absolute;border-radius:50%;background:radial-gradient(circle,#f08a2455,transparent 65%)}
.foot{color:#9fc3c8}
svg{display:block}
"""

def waves(w, h=140):
    return (f'<svg class="waves" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="none">'
            f'<path d="M0 50 C{w*.15} 10 {w*.35} 90 {w*.5} 50 S{w*.85} 10 {w} 50 V{h} H0Z" fill="#3fb3bd"/>'
            f'<path d="M0 90 C{w*.2} 60 {w*.3} 120 {w*.55} 90 S{w*.8} 60 {w} 90 V{h} H0Z" fill="#3fb3bd"/></svg>')

def page(w, h, body, extra_css=""):
    css = BASE_CSS.replace("%VARS%", VARS) + extra_css
    return (f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{css}</style></head>'
            f'<body style="width:{w}px;height:{h}px">{body}</body></html>')

# ------------------------------------------------------------ link previews
def og(title_html, sub, art_html, tag="Paybill 4129691"):
    body = (f'<div class="glow" style="width:700px;height:700px;right:-160px;top:-260px"></div>{waves(1200)}'
            '<div style="position:absolute;inset:56px 64px;display:grid;grid-template-columns:1fr 430px;gap:40px;align-items:center">'
            f'<div style="display:grid;gap:26px">{logo()}<h1 style="font-size:64px">{title_html}</h1>'
            f'<p class="sub" style="font-size:27px">{sub}</p>'
            f'<div style="display:flex;gap:16px;align-items:center"><span class="pill" style="font-size:26px">{tag}</span>'
            '<span class="foot" style="font-size:22px">seabreezedata.co.ke</span></div></div>'
            f'<div>{art_html}</div></div>')
    return page(1200, 630, body, ".kmap text{font:500 14px var(--body);fill:var(--ink)}.kmap text.ocean{font:italic 500 13px var(--body);fill:var(--sea);text-anchor:middle}")

def map_card(highlight=None):
    return (f'<div style="background:#eef7f7;border-radius:28px;padding:12px">'
            f'{art.kenya_map(highlight=highlight, links=False)}</div>')

def paybill_card(scale=1.0):
    s = scale
    return (f'<div style="background:#eef7f7;color:#0d2a33;border-radius:{28*s}px;padding:{34*s}px {34*s}px;display:grid;gap:{14*s}px;'
            f'box-shadow:0 30px 60px #0006">'
            f'<div style="font:600 {18*s}px var(--body);letter-spacing:.08em;text-transform:uppercase;color:#0b6e78">Lipa na M-Pesa · Pay Bill</div>'
            f'<div class="mono" style="font-size:{72*s}px;line-height:1">4129691</div>'
            f'<div style="height:2px;background:#d5e2e3"></div>'
            f'<div style="font:600 {18*s}px var(--body);letter-spacing:.08em;text-transform:uppercase;color:#0b6e78">Account number</div>'
            f'<div style="font:700 {30*s}px var(--display)">Your Airtel 5G line</div>'
            f'<div style="font:500 {19*s}px var(--body);color:#4d6870">e.g. 0101234567</div></div>')

def mdogo_card():
    return art.mdogo_art().replace('class="mdogo-art"', 'class="mdogo-art" width="430"')

def sms_card():
    return art.sms_art().replace('class="sms-art"', 'class="sms-art" width="430"')

# ------------------------------------------------------ WhatsApp status 9:16
def status(title_html, sub, art_html, cta, w=1080, h=1920):
    body = (f'<div class="glow" style="width:1100px;height:1100px;right:-420px;top:-380px"></div>{waves(w, 260)}'
            f'<div style="position:absolute;inset:110px 84px 150px;display:flex;flex-direction:column;gap:54px">'
            f'{logo(size=1.5)}<h1 style="font-size:112px">{title_html}</h1>'
            f'<p class="sub" style="font-size:44px">{sub}</p>'
            f'<div style="flex:1;display:grid;place-items:center">{art_html}</div>'
            f'<div style="display:grid;gap:22px;justify-items:start"><span class="pill" style="font-size:46px">{cta}</span>'
            '<span class="foot" style="font-size:36px">WhatsApp 0720 499 691 · seabreezedata.co.ke</span></div></div>')
    return page(w, h, body, ".kmap text{font:500 14px var(--body);fill:var(--ink)}.kmap text.ocean{font:italic 500 13px var(--body);fill:var(--sea);text-anchor:middle}")

def square(title_html, sub, art_html, cta):
    body = (f'<div class="glow" style="width:800px;height:800px;right:-300px;top:-300px"></div>{waves(1080, 180)}'
            '<div style="position:absolute;inset:64px 70px 80px;display:flex;flex-direction:column;gap:26px">'
            f'{logo(size=1.15)}<h1 style="font-size:80px">{title_html}</h1>'
            f'<p class="sub" style="font-size:34px">{sub}</p>'
            f'<div style="flex:1;display:grid;place-items:center;min-height:0">{art_html}</div>'
            f'<div style="display:flex;gap:20px;align-items:center"><span class="pill" style="font-size:36px">{cta}</span>'
            '<span class="foot" style="font-size:28px">WhatsApp 0720 499 691</span></div></div>')
    return page(1080, 1080, body, ".kmap text{font:500 14px var(--body);fill:var(--ink)}.kmap text.ocean{font:italic 500 13px var(--body);fill:var(--sea);text-anchor:middle}")

def price_card():
    row = lambda sp, p: (f'<div style="display:flex;justify-content:space-between;align-items:baseline;padding:22px 0;border-bottom:2px solid #d5e2e3">'
                         f'<b style="font:800 52px var(--display)">{sp}</b><span class="mono" style="font-size:46px">KES {p}</span></div>')
    return (f'<div style="background:#eef7f7;color:#0d2a33;border-radius:36px;padding:30px 48px;width:820px">'
            f'{row("15 Mbps", "1,999")}{row("30 Mbps", "2,999")}'
            '<p style="font:500 28px var(--body);color:#4d6870;padding-top:20px">Per 30 days, unlimited. KES 1,000 connection fee on 30-day plans.</p></div>')

def agents_card(width=520):
    return art.agents_art().replace('class="agents-art"', f'class="agents-art" width="{width}"')

# ----------------------------------------------------------------- main
def build(out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    files = {}
    # link previews (site)
    files["og/home_1200x630"] = og("Airtel 5G home internet. Renew from <em>any phone</em>.",
                                   "Unlimited home WiFi from KES 1,999 a month. Authorised Airtel ESP in Malindi, serving Kenya.",
                                   paybill_card(.95))
    files["og/renew_1200x630"] = og("Renew Airtel 5G on <em>M-Pesa</em> in 4 steps",
                                    "Works on any phone. No app, no data bundle, no *400#.", paybill_card(.95))
    files["og/lipa-mdogo-mdogo_1200x630"] = og("Lipa <em>Mdogo Mdogo</em> for Airtel 5G",
                                               "Pay from KES 500 at a time. We renew your line when it adds up.", mdogo_card())
    files["og/sms_1200x630"] = og("Choose the <em>SMS</em> you get from us",
                                  "Join or stop renewal reminders and offers. Payment receipts always sent.", sms_card(), tag="seabreezedata.co.ke/sms")
    for slug, (name, *_rest) in art.TOWNS.items():
        files[f"og/town-{slug}_1200x630"] = og(f"Airtel 5G home internet in <em>{html.escape(name)}</em>",
                                               "Set up by a local Seabreeze agent. Renew any time on M-Pesa.", map_card(slug))
    # WhatsApp status and post cards (for Hassan to share; not on the site)
    files["share/status-renew_1080x1920"] = status("Renew your Airtel 5G from <em>any phone</em>",
        "Lipa na M-Pesa. No app, no data bundle, no *400# needed.", paybill_card(1.6), "Paybill 4129691")
    files["share/status-mdogo_1080x1920"] = status("Lipa <em>Mdogo Mdogo</em>",
        "Pay from KES 500 at a time to Paybill 4129691. We renew your line when it adds up. No extra charge.",
        art.mdogo_art().replace('class="mdogo-art"', 'class="mdogo-art" width="860"'), "Paybill 4129691")
    files["share/status-get5g_1080x1920"] = status("Fast home WiFi, <em>no cables</em>",
        "Airtel 5G Smart Connect, installed by a Seabreeze agent near you.", price_card(), "WhatsApp to get connected")
    files["share/status-agent_1080x1920"] = status("Become a <em>Shujaa</em> agent",
        "Earn for every client you connect, and again every time they renew through our paybill.", agents_card(860), "Join on WhatsApp")
    files["share/post-renew_1080x1080"] = square("Renew Airtel 5G from <em>any phone</em>",
        "Lipa na M-Pesa. Account number = your Airtel 5G line.", paybill_card(1.05), "Paybill 4129691")
    files["share/post-mdogo_1080x1080"] = square("Lipa <em>Mdogo Mdogo</em>",
        "From KES 500 at a time. We renew when it adds up.", art.mdogo_art().replace('class="mdogo-art"', 'class="mdogo-art" width="560"'), "Paybill 4129691")
    files["share/post-coverage_1080x1080"] = square("Seabreeze agents near <em>you</em>",
        "From Malindi and the coast to Kisumu and western Kenya.", map_card().replace("padding:12px", "padding:12px;width:520px"), "Get connected")
    # Google Business Profile
    files["gbp/logo_720x720"] = page(720, 720, f'<div style="position:absolute;inset:0;display:grid;place-items:center;background:#0a3d47">'
                                     f'{art.mark(520, wave="#0a3d47", bg="#ffffff", sun="#f08a24")}</div>')
    files["gbp/cover_1024x576"] = page(1024, 576, f'<div class="glow" style="width:600px;height:600px;right:-120px;top:-220px"></div>{waves(1024)}'
        '<div style="position:absolute;inset:60px;display:grid;gap:24px;align-content:center">'
        f'{logo(size=1.2)}<h1 style="font-size:60px">Airtel 5G home internet,<br>renew from <em>any phone</em></h1>'
        '<div><span class="pill" style="font-size:28px">M-Pesa Paybill 4129691</span></div></div>')
    for name, doc in files.items():
        p = out / f"{name}.html"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(doc)
    print(len(files), "cards")

if __name__ == "__main__":
    build(sys.argv[1])
