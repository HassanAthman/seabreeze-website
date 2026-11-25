#!/usr/bin/env python3
"""Build the help centre: /support/ (hub) and one page per guide at /support/<slug>/.

All English text lives here. tools/i18n.py translates the pages into /sw/ and /it/.
Phone-screen mock-ups carry translate="no", because M-Pesa menus and router pages
are in English on the phone itself.

    python3 tools/support.py      (tools/build.sh runs it)
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://seabreezedata.co.ke"
WA = "https://wa.me/254734782203"

# ---------- icons (24x24 line icons, stroke = currentColor) ----------
P = {
    "wallet": '<path d="M3 7h15a3 3 0 0 1 3 3v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M3 7l12-4 2 4"/><circle cx="16.5" cy="13.5" r="1.3"/>',
    "nowifi": '<path d="M2 8.5a15 15 0 0 1 8-3.8M14 4.7a15 15 0 0 1 8 3.8M5.5 12a10 10 0 0 1 4-2.2M18.5 12a10 10 0 0 0-2-1.5M9 15.5a5 5 0 0 1 6 0"/><circle cx="12" cy="19" r="1"/><path d="M3 3l18 18"/>',
    "wifi": '<path d="M2 8.5a15 15 0 0 1 20 0M5.5 12a10 10 0 0 1 13 0M9 15.5a5 5 0 0 1 6 0"/><circle cx="12" cy="19" r="1"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "msg": '<path d="M4 4h16v12H8l-4 4z"/><path d="M8 9h8M8 12h5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "power": '<path d="M12 3v8"/><path d="M6.3 6.3a8 8 0 1 0 11.4 0"/>',
    "chat": '<path d="M4 20l1.4-4A8 8 0 1 1 8 18.6z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 1c-1-.5-1.8-1.3-2.3-2.3l1-1-1-2z"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "router": '<rect x="7" y="3" width="10" height="18" rx="3"/><circle cx="12" cy="8" r="1"/><circle cx="12" cy="11" r="1"/><circle cx="12" cy="14" r="1"/>',
    "plug": '<path d="M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0z"/><path d="M12 16v5"/>',
    "lights": '<rect x="7" y="3" width="10" height="18" rx="3"/><path d="M12 7v.01M12 11v.01M12 15v.01" stroke-width="3"/>',
    "devices": '<rect x="2" y="5" width="13" height="10" rx="1.5"/><path d="M6 19h5M8.5 15v4"/><rect x="17" y="8" width="5" height="11" rx="1"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "window": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M12 3v18M4 12h16"/>',
    "tag": '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8" r="1.4"/>',
    "key": '<circle cx="8" cy="14" r="4"/><path d="M11 11l9-9M17 5l2 2M15 7l2 2"/>',
    "bell": '<path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 20a2 2 0 0 0 4 0"/>',
    "lock": '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "cash": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M2 3l20 18"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "cube": '<path d="M12 2l9 5v10l-9 5-9-5V7z"/><path d="M12 12l9-5M12 12v10M12 12L3 7"/>',
    "coins": '<ellipse cx="9" cy="7" rx="6" ry="3"/><path d="M3 7v5c0 1.7 2.7 3 6 3s6-1.3 6-3V7"/><path d="M9 15v2c0 1.7 2.7 3 6 3s6-1.3 6-3v-5c0-1.7-2.7-3-6-3"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "map": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
}

def icon(name, cls="ic"):
    return (f'<svg class="{cls}" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[name]}</svg>')

# ---------- step visuals ----------
def mpesa(title, rows=None, sel=None, inp=None, soft="OK"):
    """A basic-phone M-Pesa screen."""
    body = "".join(f'<div{" class=\"sel\"" if i == sel else ""}>{r}</div>' for i, r in enumerate(rows or []))
    if inp:
        body += f'<div class="inp">{inp}</div>'
    return (f'<div class="mk mk-basic" translate="no" aria-hidden="true"><div class="mk-scr"><div class="mk-st"><span>Safaricom</span><span>12:40</span></div>'
            f'<div class="mk-t">{title}</div>{body}<div class="mk-soft"><span>{soft}</span><span>Back</span></div></div></div>')

def web(top, body, url="192.168.1.1"):
    """A smartphone browser showing the router's settings page."""
    return (f'<div class="mk mk-smart" translate="no" aria-hidden="true"><div class="mk-scr"><div class="mk-url">{url}</div>'
            f'<div class="mk-top">{top}</div><div class="mk-body">{body}</div></div></div>')

def chat(msgs):
    """A WhatsApp-style chat. Messages are translated."""
    rows = "".join(f'<p class="b-{side}">{t}</p>' for side, t in msgs)
    return f'<div class="mk mk-smart mk-chat" aria-hidden="true"><div class="mk-scr"><div class="mk-wa"><b>Seabreeze 5G</b></div><div class="mk-msgs">{rows}</div></div></div>'

def sms(msgs, who="CBriz Data"):
    """A phone's Messages app. Messages are translated."""
    rows = "".join(f'<p class="b-{side}">{t}</p>' for side, t in msgs)
    return f'<div class="mk mk-smart mk-chat mk-sms" aria-hidden="true"><div class="mk-scr"><div class="mk-wa"><b>{who}</b></div><div class="mk-msgs">{rows}</div></div></div>'

SMS_NO = "0734 782 203"
# (word, what you get) for the SMS auto-answer on 0734 782 203
SMS_WORDS = [
    ("EXPIRY", "When your Airtel 5G ends. Sent only to the phone registered on the line."),
    ("PAID", "Whether we got your payment. You can also send the M-Pesa code."),
    ("RENEW", "How to pay on Paybill 4129691."),
    ("PRICE", "All packages and prices."),
    ("MDOGO", "How Lipa Mdogo Mdogo works."),
    ("WIFI", "A link to change your WiFi name and password."),
    ("AGENT", "A person from our team gets back to you."),
    ("STOP", "Stop offers and reminders. Send START to turn them back on."),
]

def sms_band():
    """'Instant answers by SMS' card: help centre home and Contact page."""
    chips = "".join(f'<span translate="no">{w}</span>' for w, _ in SMS_WORDS[:6])
    return f'''<div class="sms-band">
      <div class="sb-ic">{icon("msg")}</div>
      <div class="sb-txt">
        <h2>Instant answers by SMS</h2>
        <p>Text one word to <b>{SMS_NO}</b> and get a reply in seconds, day or night. Works on any phone.</p>
        <div class="sb-words">{chips}</div>
      </div>
      <a class="btn btn-sun" href="/support/sms-answers/">See all SMS words</a>
    </div>'''

def ico(name):
    return f'<div class="st-ico">{icon(name)}</div>'

BTN = '<span class="mk-btn">{}</span>'
FIELD = '<label>{}</label><div class="mk-in{}">{}</div>'
TOG = '<div class="mk-tog"><span>Optimize</span><i class="on"></i></div>'

# ---------- guides ----------
# Each guide: title, summary, minutes, topic, icon, optional before / done / tip,
# steps [(action, detail, visual)], or qa [(question, answer)], or widget (HTML).
G = {}

G["renew-paybill"] = dict(
    title="Renew with M-Pesa", icon="wallet", topic="pay", minutes=2,
    summary="Pay for your Airtel 5G from any phone using Paybill 4129691.",
    steps=[
        ("Open M-Pesa", "Choose Lipa na M-Pesa, then Pay Bill.",
         mpesa("Lipa na M-PESA", ["1 Pay Bill", "2 Buy Goods"], sel=0)),
        ("Enter the business number", "Type <b>4129691</b>.", mpesa("Business no.", inp="4129691")),
        ("Enter your Airtel 5G number as the account", "For example 0101234567.", mpesa("Account no.", inp="0101234567")),
        ("Enter the amount", "KES 1,999 for 15 Mbps or KES 2,999 for 30 Mbps.", mpesa("Amount", inp="1999")),
        ("Enter your PIN and send", "You get an SMS when your line is renewed.",
         mpesa("Pay KES 1,999 to", ["SEABREEZE", "Acc 0101234567", "Enter PIN"], inp="****")),
    ],
    done="Your internet comes back within minutes.",
    tip='Short of the full amount? <a href="../lipa-mdogo-mdogo/">Pay in small amounts</a>.',
)

G["paid-no-internet"] = dict(
    title="I paid but there is no internet", icon="nowifi", topic="fix", minutes=2,
    summary="Most payments reflect within minutes. If yours has not, follow these steps.",
    steps=[
        ("Check the M-Pesa message", "Make sure you paid to 4129691 with the right Airtel 5G number.", ico("msg")),
        ("SMS PAID to 0734 782 203", "We reply in seconds and tell you if your payment has arrived.", ico("chat")),
        ("Wait 30 minutes", "Most renewals show within a few minutes.", ico("clock")),
        ("Restart the router", 'Unplug it, wait 30 seconds, then plug it back in. <a href="../restart-router/">See how</a>', ico("power")),
        ("Still off? Send us the M-Pesa message", "WhatsApp it to 0734 782 203 with your Airtel 5G number.", ico("chat")),
    ],
    cta=("WhatsApp the M-Pesa message", "Hi Seabreeze, I paid but my internet is still off. Here is my M-Pesa message:"),
)

G["change-wifi-password"] = dict(
    title="Change your WiFi name and password", icon="key", topic="wifi", minutes=3,
    summary="Do this on a phone or laptop connected to your router's WiFi.",
    before="Connect your phone to the router's WiFi first.",
    steps=[
        ("Open Chrome or any browser", "", web("", '<div class="mk-search">Search or type web address</div>', url="")),
        ("Type 192.168.1.1 and open it", "This opens your router's settings page.",
         web("", '<div class="mk-search on">192.168.1.1</div><div class="mk-keys"><span>1</span><span>9</span><span>2</span><span>.</span><span>1</span><span>6</span><span>8</span><span>Go</span></div>', url="192.168.1.1")),
        ("Tap Login at the top right", "", web('<b>5G CPE</b>' + BTN.format("Login"), '<div class="mk-card">Status: Connected</div><div class="mk-card">Signal: 5G</div>')),
        ("Enter admin as the username and password", "Both are <b>admin</b>.",
         web('<b>5G CPE</b>', FIELD.format("Username", "", "admin") + FIELD.format("Password", "", "admin") + BTN.format("Login"))),
        ("Open WiFi settings", "", web('<b>5G CPE</b>', '<div class="mk-menu"><div>Home</div><div class="sel">WiFi settings</div><div>Network</div><div>System</div></div>')),
        ("Choose 5G WiFi settings", "", web('<b>WiFi settings</b>', '<div class="mk-menu"><div>2.4G WiFi settings</div><div class="sel">5G WiFi settings</div></div>')),
        ("Switch on Optimize", "", web('<b>5G WiFi settings</b>', TOG + '<div class="mk-card dim">WiFi name</div><div class="mk-card dim">Password</div>')),
        ("Type your new WiFi name and password", "Use at least 8 characters that you can remember.",
         web('<b>5G WiFi settings</b>', TOG + FIELD.format("WiFi name", " edit", "MyHome5G") + FIELD.format("Password", " edit", "••••••••••"))),
        ("Tap SAVE", "", web('<b>5G WiFi settings</b>', FIELD.format("WiFi name", "", "MyHome5G") + FIELD.format("Password", "", "••••••••••") + BTN.format("SAVE") + '<div class="mk-toast">Saved</div>')),
    ],
    done="Your phones and TVs disconnect. Connect them again with the new name and password.",
    tip="Your router's pages may look a little different from these pictures.",
)

G["check-expiry"] = dict(
    title="Check when your plan ends", icon="clock", topic="account", minutes=1,
    summary="We tell you your expiry date and the amount to pay.",
    steps=[
        ("Open WhatsApp", "Start a chat with 0734 782 203.", ico("chat")),
        ("Send your Airtel 5G number", "For example 0101234567.", chat([("me", "0101234567")])),
        ("We reply with your expiry date", "And the amount to pay.",
         chat([("me", "0101234567"), ("them", "Your plan ends on 12 December. Renew with KES 1,999 on Paybill 4129691.")])),
    ],
    cta=("Ask on WhatsApp", "Hi Seabreeze, when does my plan end? My Airtel 5G number is:"),
    tip='Faster: SMS <b>EXPIRY</b> to 0734 782 203 for an instant answer. <a href="../sms-answers/">How it works</a>',
)

G["slow-internet"] = dict(
    title="My internet is slow", icon="chart", topic="fix", minutes=2,
    summary="Try these steps in order. Most slow connections are fixed by the first two.",
    steps=[
        ("Restart the router", 'Unplug it, wait 30 seconds, then plug it back in. <a href="../restart-router/">See how</a>', ico("power")),
        ("Move the router near a window", "Put it high up, away from metal and thick walls.", ico("window")),
        ("Check how many devices are on", "Many phones and TVs streaming at once share the speed.", ico("devices")),
        ("Check your data use", "After 1,000 GB in one plan, the speed drops to 2 Mbps until you renew.", ico("chart")),
    ],
    cta=("Still slow? WhatsApp us", "Hi Seabreeze, my internet is slow. My Airtel 5G number is:"),
)

G["restart-router"] = dict(
    title="Restart your router", icon="power", topic="fix", minutes=3,
    summary="A restart fixes most connection problems. Watch the 3D guide, then follow the steps.",
    widget="restart",
    steps=[
        ("Unplug the power cable", "From the back of the router.", ico("plug")),
        ("Wait 30 seconds", "", ico("clock")),
        ("Plug the power cable back in", "", ico("plug")),
        ("Wait for the lights", "In 2 to 3 minutes the power, signal and WiFi lights come on. Then connect again.", ico("lights")),
    ],
)

G["no-internet"] = dict(
    title="No internet at all", icon="nowifi", topic="fix", minutes=2,
    summary="Find out if it is the power, your plan or the router.",
    steps=[
        ("Look at the router lights", "No lights? Check the power cable and try another socket.", ico("lights")),
        ("Check if your plan has ended", '<a href="../check-expiry/">Ask us your expiry date</a> on WhatsApp.', ico("clock")),
        ("Renew if it has ended", '<a href="../renew-paybill/">Pay on Paybill 4129691</a>.', ico("wallet")),
        ("Restart the router", '<a href="../restart-router/">See how</a>', ico("power")),
    ],
    cta=("Still off? WhatsApp us", "Hi Seabreeze, I have no internet. My Airtel 5G number is:"),
)

G["forgot-wifi-password"] = dict(
    title="I forgot my WiFi password", icon="lock", topic="wifi", minutes=1,
    summary="You can find it or set a new one.",
    steps=[
        ("Look at the label on the router", "If you never changed the password, it is printed there.", ico("tag")),
        ("Changed it before? Set a new one", 'Use a phone that is still connected and follow <a href="../change-wifi-password/">Change your WiFi name and password</a>.', ico("key")),
        ("No device can connect? Call us", "Do not reset the router before talking to us.", ico("phone")),
    ],
)

G["router-placement"] = dict(
    title="Best place for your router", icon="map", topic="wifi", minutes=1,
    summary="Where you put the router decides how fast your WiFi is.",
    steps=[
        ("Near a window", "The router gets the strongest signal there.", ico("window")),
        ("High up", "On a shelf or table, not on the floor.", ico("chart")),
        ("Away from metal", "Keep it away from metal roofs, fridges and microwaves.", ico("shield")),
        ("Always on", "Turning it off and on many times a day slows it down.", ico("power")),
    ],
    tip='Big house? We sell WiFi extenders and set them up. <a href="/contact/">Contact us</a>.',
)

G["router-guide"] = dict(
    title="Get to know your router", icon="cube", topic="wifi", minutes=2,
    summary="Turn the 3D router with your finger and tap a number to see what each part does.",
    widget="explore",
)

G["lipa-mdogo-mdogo"] = dict(
    title="Pay in small amounts", icon="coins", topic="pay", minutes=1,
    summary="Lipa Mdogo Mdogo: pay bit by bit and we renew when it adds up.",
    steps=[
        ("Send any amount from KES 500", "To Paybill 4129691, with your Airtel 5G number as the account.", ico("wallet")),
        ("Get an SMS with your balance", "After every payment.", ico("msg")),
        ("We renew when it adds up", "At KES 1,999 (15 Mbps) or KES 2,999 (30 Mbps). No extra charge.", ico("check")),
    ],
    tip='<a href="/lipa-mdogo-mdogo/">How Lipa Mdogo Mdogo works</a>',
)

G["payment-questions"] = dict(
    title="Payment questions", icon="list", topic="pay", minutes=2,
    summary="Paying early, paying for someone else, mistakes and prices.",
    qa=[
        ("Can I pay before my plan ends?", "Yes. Pay any time. Your new plan starts when the current one ends, so you never lose days."),
        ("Can I pay for someone else?", "Yes. Use their Airtel 5G line number as the account number. You can pay from any M-Pesa line."),
        ("I used the wrong account number", "WhatsApp us on 0734 782 203 with the M-Pesa message and the correct Airtel 5G number. We move the payment to the right line."),
        ("How much are the packages?", "PRICES"),
    ],
)

G["sms-reminders"] = dict(
    title="Start or stop SMS reminders", icon="bell", topic="account", minutes=1,
    summary="Get a reminder before your plan ends, or stop messages any time.",
    steps=[
        ("Open the SMS form", '<a href="/sms/">SMS preferences form</a>', ico("bell")),
        ("Or text STOP", "Send STOP to 0734 782 203 to stop offers and reminders.", ico("msg")),
    ],
    tip="Payment receipts are always sent.",
)

G["stay-safe"] = dict(
    title="Stay safe from fraud", icon="shield", topic="account", minutes=1,
    summary="Four rules that keep your money safe.",
    steps=[
        ("We never ask for your M-Pesa PIN", "Never share it with anyone.", ico("lock")),
        ("Our only paybill is 4129691", "Do not pay to any other number.", ico("wallet")),
        ("Never pay an installer in cash", "Airtel installation is paid through Airtel.", ico("cash")),
        ("Our only numbers", "0782 998 842 and 0734 782 203.", ico("phone")),
    ],
)

G["sms-answers"] = dict(
    title="Get instant answers by SMS", icon="msg", topic="account", minutes=1,
    summary="Text one word to 0734 782 203 and get an answer in seconds, day or night.",
    steps=[
        ("Open Messages on any phone", "No smartphone, app or internet needed.", ico("msg")),
        ("Send one word to 0734 782 203", "For example EXPIRY. Small letters are fine, in English or Kiswahili.", sms([("me", "expiry")], who="0734 782 203")),
        ("Get the answer in seconds", "The reply comes from CBriz Data.",
         sms([("me", "expiry"), ("them", "Your Airtel 5G 0101234567 ends on 12 December. Renew with KES 1,999 on Paybill 4129691.")])),
    ],
    words=True,
    tip="For your safety, we send expiry dates and payment details only to the phone number registered on your line.",
)

TOPICS = [
    ("pay", "Pay and renew", "wallet", ["renew-paybill", "lipa-mdogo-mdogo", "payment-questions"]),
    ("fix", "No internet or slow", "nowifi", ["paid-no-internet", "no-internet", "slow-internet", "restart-router"]),
    ("wifi", "WiFi and router", "wifi", ["change-wifi-password", "forgot-wifi-password", "router-placement", "router-guide"]),
    ("account", "Account and safety", "shield", ["sms-answers", "check-expiry", "sms-reminders", "stay-safe", ("/update-details/", "Update your details")]),
]
TOPIC_NAME = {t[0]: t[1] for t in TOPICS}
POPULAR = ["renew-paybill", "paid-no-internet", "change-wifi-password", "check-expiry", "slow-internet", "restart-router"]
# old /support/#anchor links (SMS, footer) -> new pages
OLD = {"change-wifi-password": "change-wifi-password", "renew-paybill": "renew-paybill", "paid-no-internet": "paid-no-internet",
       "check-expiry": "check-expiry", "restart-router": "restart-router", "forgot-wifi-password": "forgot-wifi-password",
       "router-placement": "router-placement", "lipa-mdogo": "lipa-mdogo-mdogo", "renew-early": "payment-questions",
       "pay-for-someone": "payment-questions", "wrong-account": "payment-questions", "prices": "payment-questions",
       "no-internet": "no-internet", "lights-off": "no-internet", "slow-internet": "slow-internet",
       "sms-reminders": "sms-reminders", "stay-safe": "stay-safe", "router-3d": "router-guide", "sms": "sms-answers"}

PAGES = ["support/index.html"] + [f"support/{s}/index.html" for s in G]

# ---------- shared pieces ----------
def contact_block():
    return f'''<section class="hc-contact" id="contact-us">
  <div class="wrap">
    <h2>Still need help?</h2>
    <p class="hc-sub">Talk to a person. We answer from 8am to 8pm, every day.</p>
    <div class="hc-ch">
      <a class="ch ch-wa" href="{WA}?text=Hi%20Seabreeze%2C%20I%20need%20help%20with%20my%20Airtel%205G." target="_blank" rel="noopener">{icon("chat")}<b>WhatsApp</b><span>0734 782 203</span><i>Fastest</i></a>
      <a class="ch" href="tel:+254782998842">{icon("phone")}<b>Call</b><span>0782 998 842</span></a>
      <a class="ch" href="tel:+254734782203">{icon("phone")}<b>Call</b><span>0734 782 203</span></a>
      <a class="ch ch-mail" href="mailto:support@seabreezedata.co.ke">{icon("mail")}<b>Email</b><span>support@seabreezedata.co.ke</span></a>
    </div>
  </div>
</section>'''

def mins(n):
    return "Takes about 1 minute" if n == 1 else f"Takes about {n} minutes"

def article_link(slug, cls="art"):
    if isinstance(slug, tuple):
        return f'<a class="{cls}" href="{slug[0]}">{icon("arrow", "ic go")}<span>{slug[1]}</span></a>'
    g = G[slug]
    return f'<a class="{cls}" href="/support/{slug}/">{icon("arrow", "ic go")}<span>{g["title"]}</span></a>'

# ---------- hub ----------
def hub():
    pop = "".join(
        f'<a class="pop" href="/support/{s}/"><span class="pop-ic">{icon(G[s]["icon"])}</span><b>{G[s]["title"]}</b><span class="pop-d">{G[s]["summary"]}</span></a>'
        for s in POPULAR)
    topics = "".join(
        f'<div class="topic2" id="{tid}"><div class="t2-h"><span class="t2-ic">{icon(ic)}</span><h3>{name}</h3></div>'
        f'<div class="t2-list">{"".join(article_link(s) for s in arts)}</div></div>'
        for tid, name, ic, arts in TOPICS)
    chips = "".join(f'<a href="/support/{s}/">{G[s]["title"]}</a>' for s in POPULAR[:4])
    old = json.dumps(OLD)
    return f'''<main id="top">
<section class="hero hc-hero">
  <div class="wrap">
    <div class="crumbs"><a href="/">Home</a> / Support</div>
    <h1>Hi, how can we <em>help</em>?</h1>
    <form class="hc-search" role="search" onsubmit="return false">
      <label for="hcq" class="sr">Search the help centre</label>
      {icon("search", "ic hc-sicon")}
      <input id="hcq" type="search" placeholder="Search, for example WiFi password" autocomplete="off" aria-controls="hcres">
      <div class="hc-res" id="hcres" role="listbox" hidden></div>
    </form>
    <p class="hc-none" id="hcnone" hidden>No guide found. WhatsApp us on 0734 782 203 and we will help.</p>
    <div class="hc-chips"><span>Popular:</span>{chips}</div>
  </div>
</section>

<section class="hc-sec hc-smssec">
  <div class="wrap">
    {sms_band()}
  </div>
</section>

<section class="hc-sec">
  <div class="wrap">
    <h2>Top questions</h2>
    <div class="pops">{pop}</div>
  </div>
</section>

<section class="hc-sec hc-alt">
  <div class="wrap">
    <h2>Browse by topic</h2>
    <div class="topics2">{topics}</div>
  </div>
</section>

<section class="hc-sec">
  <div class="wrap">
    <h2>Interactive guides</h2>
    <div class="feats">
      <a class="feat" href="/support/router-guide/"><span class="feat-art feat-3d">{icon("cube")}</span><b>Your router in 3D</b><span>Turn it with your finger and tap each part to learn what it does.</span></a>
      <a class="feat" href="/support/restart-router/"><span class="feat-art">{icon("power")}</span><b>Restart, step by step</b><span>Watch the router restart in 3D, then do it yourself.</span></a>
      <a class="feat" href="/support/change-wifi-password/"><span class="feat-art">{icon("key")}</span><b>WiFi password in pictures</b><span>Every screen you will see, from 192.168.1.1 to SAVE.</span></a>
    </div>
  </div>
</section>
</main>
<script>var HC_OLD={old};</script>
'''

# ---------- guide pages ----------
def prices_table():
    return ('<table class="ptable"><tr><th>Speed</th><th>30 days</th><th>90 days</th><th>180 days</th></tr>'
            '<tr><td>15 Mbps</td><td>KES 1,999</td><td>KES 5,399</td><td>KES 9,999</td></tr>'
            '<tr><td>30 Mbps</td><td>KES 2,999</td><td>KES 8,099</td><td>KES 14,999</td></tr></table>'
            '<p class="qa-note">Unlimited data with a fair use limit of 1,000 GB per plan.</p>')

def widget(kind):
    restart = kind == "restart"
    return f'''<div class="r3 r3-art"{' data-start="restart"' if restart else ''}>
      <div class="r3-stage">
        <canvas id="router3d" aria-label="Interactive 3D model of a 5G router. Use the buttons to see each part." role="img"></canvas>
        <div class="r3-hs" id="r3hs">
          <button type="button" data-part="lights" aria-label="Status lights">1</button>
          <button type="button" data-part="label" aria-label="Label">2</button>
          <button type="button" data-part="power" aria-label="Power socket">3</button>
          <button type="button" data-part="lan" aria-label="Network ports">4</button>
          <button type="button" data-part="reset" aria-label="Reset hole">5</button>
        </div>
        <p class="r3-cap">An example 5G router. Yours may look a little different.</p>
      </div>
      <div class="r3-side">
        <div class="r3-tabs" role="group" aria-label="Guide">
          <button type="button" id="r3Explore" aria-pressed="true">Explore the parts</button>
          <button type="button" id="r3Restart" aria-pressed="false">Play: restart the router</button>
        </div>
        <div class="r3-info" id="r3Info" aria-live="polite">
          <div data-info="intro"><h3>Tap a number</h3><p>Each number on the router shows one part. Start with 1, the lights on the front.</p></div>
          <div data-info="lights" hidden><h3>1. Status lights</h3><p>Power, signal and WiFi. When all three are on, your internet is working.</p></div>
          <div data-info="label" hidden><h3>2. Label</h3><p>Shows the default WiFi name and password. If you never changed your password, use this one.</p></div>
          <div data-info="power" hidden><h3>3. Power socket</h3><p>Use only the charger that came with the router. To restart, unplug here for 30 seconds.</p></div>
          <div data-info="lan" hidden><h3>4. Network (LAN) ports</h3><p>Connect a TV, computer or CCTV recorder with a cable for the steadiest connection.</p></div>
          <div data-info="reset" hidden><h3>5. Reset hole</h3><p>Do not press it. A reset deletes your WiFi name, password and settings. Call us first.</p></div>
        </div>
        <ol class="r3-steps" id="r3Steps" hidden>
          <li>Unplug the power cable from the back of the router.</li>
          <li>Wait 30 seconds.</li>
          <li>Plug the power cable back in.</li>
          <li>Wait 2 to 3 minutes until the power, signal and WiFi lights are on. Then connect again.</li>
        </ol>
      </div>
    </div>'''

def guide(slug):
    g = G[slug]
    parts = []
    if g.get("before"):
        parts.append(f'<div class="g-before">{icon("check")}<p><b>Before you start:</b> {g["before"]}</p></div>')
    if g.get("widget"):
        parts.append(widget(g["widget"]))
    if g.get("steps"):
        lis = []
        for i, (act, det, vis) in enumerate(g["steps"], 1):
            d = f'<p>{det}</p>' if det else ""
            lis.append(f'<li class="gs"><div class="gs-txt"><span class="gs-n">{i}</span><div><h3>{act}</h3>{d}</div></div><div class="gs-vis">{vis}</div></li>')
        parts.append(f'<ol class="gsteps{" gsteps-ico" if all(s[2].startswith("<div class=\"st-ico") for s in g["steps"]) else ""}">{"".join(lis)}</ol>')
    if g.get("words"):
        rows = "".join(f'<tr><td><b translate="no">{w}</b></td><td>{d}</td></tr>' for w, d in SMS_WORDS)
        parts.append(f'<div class="qa"><h3>Words you can send</h3><table class="ptable kwtable"><tr><th>Send</th><th>You get</th></tr>{rows}</table>'
                     '<p class="qa-note">You can also write a full question, like "when does my internet end?"</p></div>')
    if g.get("qa"):
        qa = "".join(f'<div class="qa"><h3>{q}</h3>{prices_table() if a == "PRICES" else f"<p>{a}</p>"}</div>' for q, a in g["qa"])
        parts.append(f'<div class="qas">{qa}</div>')
    if g.get("done"):
        parts.append(f'<div class="g-done">{icon("check")}<p><b>Done.</b> {g["done"]}</p></div>')
    if g.get("tip"):
        parts.append(f'<p class="g-tip">{g["tip"]}</p>')
    if g.get("cta"):
        label, msg = g["cta"]
        parts.append(f'<a class="btn btn-sun g-cta" href="{WA}?text={msg.replace(" ", "%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F")}" target="_blank" rel="noopener">{label}</a>')
    parts.append(f'''<div class="helpful" data-guide="{slug}">
        <b>Was this helpful?</b>
        <div class="hf-btns"><button type="button" data-v="yes">Yes</button><button type="button" data-v="no">No</button></div>
        <p class="hf-yes" hidden>Thank you! Glad it worked.</p>
        <p class="hf-no" hidden>Sorry about that. <a href="{WA}?text=Hi%20Seabreeze%2C%20I%20need%20help%20with%20my%20Airtel%205G." target="_blank" rel="noopener">WhatsApp us on 0734 782 203</a> and a person will help you.</p>
      </div>''')
    topic = g["topic"]
    related = [s for s in next(t[3] for t in TOPICS if t[0] == topic) if s != slug]
    rel = "".join(article_link(s, "rel") for s in related[:4])
    return f'''<main id="top">
<section class="hero hc-hero hc-hero-sm">
  <div class="wrap">
    <div class="crumbs"><a href="/">Home</a> / <a href="/support/">Support</a> / <a href="/support/#{topic}">{TOPIC_NAME[topic]}</a></div>
    <h1>{g["title"]}</h1>
    <p class="lead">{g["summary"]}</p>
    <p class="g-meta">{icon("clock")}<span>{mins(g["minutes"])}</span></p>
  </div>
</section>
<section class="g-sec">
  <div class="wrap g-grid">
    <article class="g-main">
      {"".join(parts)}
    </article>
    <aside class="g-side">
      <div class="g-box"><b>Related guides</b>{rel}<a class="rel rel-all" href="/support/">{icon("arrow", "ic go")}<span>All help topics</span></a></div>
      <div class="g-box g-talk"><b>Need a person?</b><p>WhatsApp 0734 782 203 or call 0782 998 842.</p><a class="btn btn-sun btn-sm" href="{WA}" target="_blank" rel="noopener">WhatsApp us</a></div>
    </aside>
  </div>
</section>
</main>
'''

# ---------- page shell ----------
def shell(path, title, desc, main, scripts, ld):
    src = (PUB / "about" / "index.html").read_text()
    head = src[:src.index('<main id="top">')]
    foot = src[src.index("</main>") + len("</main>"):]
    head = head.replace(f"{SITE}/about/", f"{SITE}{path}")
    head = head.replace('<a href="/about/" aria-current="page">', '<a href="/about/">')
    head = head.replace('<a href="/support/">Support</a>', '<a href="/support/" aria-current="page">Support</a>', 1)
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head)
    for k in ('name="description"', 'property="og:description"'):
        head = re.sub(rf'(<meta {k} content=")[^"]*"', lambda m: m.group(1) + desc + '"', head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda m: m.group(1) + title + '"', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld) + "</script>", head, flags=re.S)
    foot, n = re.subn(r'(<script src="/app\.js(?:\?v=\w+)?" defer></script>)', lambda m: m.group(1) + scripts, foot, count=1)
    assert n == 1, "app.js script tag not found in the page shell"
    foot = re.sub(r'\n?<script src="/(?:support|guide3d)\.js" defer></script>', "", foot) if False else foot
    return head + main + foot

def main():
    hub_ld = {"@context": "https://schema.org", "@type": "WebPage", "url": f"{SITE}/support/", "name": "Seabreeze help centre",
              "about": {"@id": f"{SITE}/#business"}}
    (PUB / "support").mkdir(exist_ok=True)
    (PUB / "support" / "index.html").write_text(shell(
        "/support/", "Help centre: Airtel 5G support | Seabreeze 5G",
        "Seabreeze help centre for Airtel 5G home internet: renew on Paybill 4129691, fix no internet, change your WiFi password, check your expiry date.",
        hub(), '\n<script src="/support.js" defer></script>', hub_ld))
    for slug, g in G.items():
        ld = {"@context": "https://schema.org", "@type": "HowTo" if g.get("steps") else "WebPage", "name": g["title"],
              "description": g["summary"], "url": f"{SITE}/support/{slug}/"}
        if g.get("steps"):
            ld["step"] = [{"@type": "HowToStep", "text": a} for a, _d, _v in g["steps"]]
        scripts = '\n<script src="/support.js" defer></script>' + ('\n<script src="/guide3d.js" defer></script>' if g.get("widget") else "")
        out = PUB / "support" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(shell(f"/support/{slug}/", f'{g["title"]} | Seabreeze 5G help', g["summary"], guide(slug), scripts, ld))
    print("support pages:", len(G) + 1)

if __name__ == "__main__":
    main()
