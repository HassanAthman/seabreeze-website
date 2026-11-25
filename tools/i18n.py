#!/usr/bin/env python3
"""Build the Kiswahili (/sw/) and Italian (/it/) pages from the English ones.

The English pages in public/ are the source. Each translatable piece of a
page (a heading, paragraph, list item, button, form label, meta description,
FAQ answer and so on) is looked up in i18n/sw.json and i18n/it.json, which
map the English text to the translation. Inline markup such as <b> and <a>
stays inside the piece, so translations can reorder words naturally.

    python3 tools/i18n.py            # build /sw/ and /it/
    python3 tools/i18n.py --missing  # list English pieces with no translation

Edit an English page, then run with --missing, add the new pieces to both
JSON files, and build again. The build stops if any piece is missing, so a
language page is never half English.
"""
import json, pathlib, re, sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://seabreezedata.co.ke"
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from coverage import AREAS
PAGES = ["index.html", "renew-airtel-5g/index.html", "lipa-mdogo-mdogo/index.html",
         "sms/index.html", "get-airtel-5g/index.html", "contact/index.html", "we-are-hiring/index.html", "update-details/index.html",
         "support/index.html", "about/index.html"] + [f"airtel-5g/{s}/index.html" for s in AREAS]
LANGS = {"sw": ("Kiswahili", "sw_KE", "sw-KE"), "it": ("Italiano", "it_IT", "it")}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
INLINE = {"a", "b", "strong", "em", "i", "br", "code", "span", "small", "abbr", "kbd", "s", "u", "mark"}
SKIP = {"script", "style", "svg", "noscript"}
ATTRS = {"placeholder", "aria-label", "title", "alt"}
META = {"description", "og:title", "og:description", "twitter:title", "twitter:description"}

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

class Node:
    def __init__(self, tag, attrs, start, inner_start, parent):
        self.tag, self.attrs, self.start, self.inner_start, self.parent = tag, attrs, start, inner_start, parent
        self.children, self.inner_end, self.texts = [], None, []

class Tree(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer("\n", src):
            self.lines.append(m.end())
        self.root = Node("#root", [], 0, 0, None)
        self.cur = self.root
        self.attr_spans = []  # (node, attr name, value)
        self.feed(src)
    def off(self):
        l, c = self.getpos()
        return self.lines[l - 1] + c
    def handle_starttag(self, tag, attrs):
        start = self.off()
        text = self.get_starttag_text()
        n = Node(tag, attrs, start, start + len(text), self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is self.root:
            return
        n.inner_end = self.off()
        self.cur = n.parent
    def handle_data(self, data):
        start = self.off()
        self.cur.texts.append((start, start + len(data)))
    handle_entityref = handle_charref = None

def has_block(n):
    for c in n.children:
        if c.tag not in INLINE or has_block(c):
            return True
    return False

def in_skip(n):
    while n:
        if n.tag in SKIP:
            return True
        n = n.parent
    return False

def segments(src):
    """Yield (start, end, english) spans of the source that need translating."""
    t = Tree(src)
    out = []
    def walk(n):
        if n.tag in SKIP:
            return
        d = dict(n.attrs)
        for a in ATTRS:
            v = d.get(a)
            if v and re.search(r"[A-Za-z]{2}", v) and not in_skip(n):
                out.append(("attr", n, a, v))
        if n.tag == "meta" and (d.get("name") in META or d.get("property") in META):
            out.append(("attr", n, "content", d["content"]))
        if n.tag == "title":
            out.append(("span", n.inner_start, n.inner_end))
            return
        if n.tag == "nav" and d.get("class") == "lang":
            return
        direct_text = any(src[a:b].strip() for a, b in n.texts)
        if (n.tag != "#root" and n.inner_end is not None and not has_block(n) and not direct_text
                and len(n.children) >= 2 and n.tag not in {"title", "option"}):
            for c in n.children:
                if c.inner_end is not None and re.search(r"[A-Za-z]", re.sub(r"<[^>]+>", "", src[c.inner_start:c.inner_end])):
                    out.append(("span", c.inner_start, c.inner_end))
                cd = dict(c.attrs)
                for a in ATTRS:
                    if cd.get(a) and re.search(r"[A-Za-z]{2}", cd[a]):
                        out.append(("attr", c, a, cd[a]))
            return
        if n.tag != "#root" and n.inner_end is not None and not has_block(n) and n.tag not in INLINE | {"option", "textarea"}:
            inner = src[n.inner_start:n.inner_end]
            if re.search(r"[A-Za-z]", re.sub(r"<[^>]+>", "", inner)):
                out.append(("span", n.inner_start, n.inner_end))
            return
        if n.tag == "option" and n.inner_end is not None:
            out.append(("span", n.inner_start, n.inner_end))
            return
        # mixed content: inline runs between block children
        kids = sorted([("t", s, e) for s, e in n.texts] + [("n", c.start, c) for c in n.children], key=lambda x: x[1])
        run = []
        def flush():
            if not run:
                return
            s, e = run[0][0], run[-1][1]
            if re.search(r"[A-Za-z]", re.sub(r"<[^>]+>", "", src[s:e])):
                lead = len(src[s:e]) - len(src[s:e].lstrip())
                trail = len(src[s:e]) - len(src[s:e].rstrip())
                out.append(("span", s + lead, e - trail))
            run.clear()
        for k in kids:
            if k[0] == "t":
                run.append((k[1], k[2]))
            else:
                c = k[2]
                if c.tag in INLINE and not has_block(c) and c.inner_end is not None and n.tag not in {"#root", "html", "head", "body", "main", "section", "div", "form", "nav", "footer", "header", "ul", "ol", "fieldset"}:
                    end = src.index(">", c.inner_end) + 1
                    run.append((c.start, end))
                else:
                    flush()
                    walk(c)
        flush()
    walk(t.root)
    return out

def jsonld_strings(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("name", "text", "description") and isinstance(v, str):
                acc.append(v)
            else:
                jsonld_strings(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            jsonld_strings(v, acc)

def page_strings(src):
    keys = []
    for seg in segments(src):
        if seg[0] == "attr":
            keys.append(norm(seg[3]))
        else:
            keys.append(norm(src[seg[1]:seg[2]]))
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        acc = []
        jsonld_strings(json.loads(blk), acc)
        keys += [norm(a) for a in acc]
    for scr in re.findall(r"<script>(.*?)</script>", src, re.S):
        keys += re.findall(r"'([A-Z][^'\\]*[a-z.…][^'\\]*)'", scr)
    return [k for k in keys if re.search(r"[A-Za-z]", re.sub(r"<[^>]+>", "", k))]

# keys that must never be translated (names, numbers, brands)
KEEP = re.compile(r"^([A-Z]{2}|Content-Type|Lipa Mdogo Mdogo|Lipa na M-Pesa|Seabreeze( 5G| Data Ventures Ltd)?|Seabreeze <b class=\"g5\">5G</b>|Airtel 5G Smart Connect|Airtel 5G|M-PESA|M-Pesa|TikTok|WhatsApp|FAQ|CCTV|Paybill 4129691|4129691|WhatsApp 0734 782 203|KES [\d,]+|<b>KES [\d,]+</b>|\d+ Mbps|English|Kiswahili|Italiano|Black November|e\.g\. 0\d.*|0\d{9})$")
from coverage import PINS
NAMES = {a["name"] for a in AREAS.values()} | {t for a in AREAS.values() for t in a.get("towns", [])} | {p[0] for p in PINS} | {a["county"] for a in AREAS.values() if a.get("county")} | {"Kenya"}

def lookup(table, key, missing):
    if key in table:
        return table[key]
    if KEEP.match(key) or key in NAMES:
        return key
    # patterns for the generated area pages: "_patterns": [[regex, template], ...]
    # {1} inserts group 1, {L1} turns " and " in it into the language's word,
    # {T1} translates group 1 itself (for example "Nakuru County")
    for pat, tmpl in table.get("_patterns", []):
        m = re.fullmatch(pat, key)
        if m:
            def sub(t):
                g = m.group(int(t.group(2)))
                if t.group(1) == "L":
                    g = g.replace(" and ", f" {table['_and']} ")
                elif t.group(1) == "T":
                    g = lookup(table, g, missing)
                return g
            return re.sub(r"\{([LT]?)(\d)\}", sub, tmpl)
    missing.add(key)
    return key

def local_href(href, lang):
    """Point links to pages that exist in this language at the translated copy."""
    m = re.match(r"^/(#.*)?$", href)
    if m:
        return f"/{lang}/" + (m.group(1) or "")
    for p in PAGES[1:]:
        base = "/" + p[: -len("index.html")]
        if href.startswith(base):
            return f"/{lang}" + href
    return href

def alternates(page):
    path = "/" + page[: -len("index.html")]
    links = [f'<link rel="alternate" hreflang="en-KE" href="{SITE}{path}">']
    for lang, (_n, _l, code) in LANGS.items():
        links.append(f'<link rel="alternate" hreflang="{code}" href="{SITE}/{lang}{path}">')
    links.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{path}">')
    return "\n".join(links)

def switcher(page, current):
    path = "/" + page[: -len("index.html")]
    items = [("en", "EN", "English", path)] + [(l, l.upper(), LANGS[l][0], f"/{l}{path}") for l in LANGS]
    parts = []
    for code, short, name, href in items:
        cur = ' aria-current="true"' if code == current else ""
        parts.append(f'<a href="{href}" hreflang="{code}" lang="{code}" title="{name}"{cur}>{short}</a>')
    return '<nav class="lang" aria-label="Language">' + "".join(parts) + "</nav>"

def add_chrome(src, page, lang):
    """hreflang links and the language switcher, on every language version."""
    src = re.sub(r'\n?<link rel="alternate" hreflang=[^>]+>', "", src)
    src = src.replace('<link rel="canonical"', alternates(page) + '\n<link rel="canonical"', 1)
    src = re.sub(r'\s*<nav class="lang".*?</nav>', "", src, flags=re.S)
    src = src.replace('<a class="btn btn-sun btn-sm"', switcher(page, lang) + '\n    <a class="btn btn-sun btn-sm"', 1)
    return src

def translate(src, page, lang, table, missing):
    reps = []
    for seg in segments(src):
        if seg[0] == "attr":
            _k, n, a, v = seg
            tag = src[n.start:n.inner_start]
            new_v = lookup(table, norm(v), missing)
            esc = new_v.replace('"', "&quot;")
            new_tag = tag.replace(f'{a}="{v}"', f'{a}="{esc}"', 1)
            if new_tag != tag:
                reps.append((n.start, n.inner_start, new_tag))
        else:
            _k, s, e = seg
            reps.append((s, e, lookup(table, norm(src[s:e]), missing)))
    # apply attribute replacements on tags separately from inner spans: sort, skip overlaps
    reps.sort(key=lambda r: (r[0], -r[1]))
    out, pos = [], 0
    for s, e, new in reps:
        if s < pos:
            continue
        out.append(src[pos:s]); out.append(new); pos = e
    out.append(src[pos:])
    html = "".join(out)

    def fix_ld(m):
        data = json.loads(m.group(1))
        def tr(o):
            if isinstance(o, list):
                return [tr(v) for v in o]
            if not isinstance(o, dict):
                return o
            r = {}
            for k, v in o.items():
                if isinstance(v, str) and (k in ("text", "description") or (k == "name" and o.get("@type") == "Question")):
                    r[k] = lookup(table, norm(v), missing)
                else:
                    r[k] = tr(v)
            return r
        data = tr(data)
        if data.get("@type") == "FAQPage":
            data["inLanguage"] = LANGS[lang][2]
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"
    html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, html, flags=re.S)

    def fix_js(m):  # quoted messages inside inline page scripts
        return re.sub(r"'([A-Z][^'\\]*[a-z.…][^'\\]*)'", lambda q: "'" + lookup(table, q.group(1), missing).replace("'", "\\'") + "'", m.group(0))
    html = re.sub(r"<script>.*?</script>", fix_js, html, flags=re.S)

    for k, v in table.get("_svg", {}).items():  # words drawn inside the artwork
        html = html.replace(f">{k}<", f">{v}<")
    path = "/" + page[: -len("index.html")]
    html = re.sub(r'<html lang="[^"]*"', f'<html lang="{LANGS[lang][2]}"', html, count=1)
    html = html.replace(f'<link rel="canonical" href="{SITE}{path}">', f'<link rel="canonical" href="{SITE}/{lang}{path}">')
    html = html.replace(f'<meta property="og:url" content="{SITE}{path}">', f'<meta property="og:url" content="{SITE}/{lang}{path}">')
    html = re.sub(r'<meta property="og:locale" content="[^"]*">', f'<meta property="og:locale" content="{LANGS[lang][1]}">', html)
    html = re.sub(r'href="(/[^"]*)"', lambda m: f'href="{local_href(m.group(1), lang)}"', html)
    # the switcher keeps its own links
    html = re.sub(r'<nav class="lang".*?</nav>', switcher(page, lang), html, flags=re.S)
    return html

def main():
    show_missing = "--missing" in sys.argv
    tables = {l: json.loads((ROOT / "i18n" / f"{l}.json").read_text()) for l in LANGS}
    all_missing = {l: set() for l in LANGS}
    for page in PAGES:
        f = PUB / page
        src = add_chrome(f.read_text(), page, "en")
        f.write_text(src)
        for lang in LANGS:
            html = translate(src, page, lang, tables[lang], all_missing[lang])
            if not show_missing:
                out = PUB / lang / page
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(html)
    if show_missing:
        keys = []
        for page in PAGES:
            for k in page_strings((PUB / page).read_text()):
                if k not in keys and any(k in m for m in all_missing.values()):
                    keys.append(k)
        print(json.dumps(keys, ensure_ascii=False, indent=1))
        return
    bad = {l: sorted(m) for l, m in all_missing.items() if m}
    if bad:
        for l, m in bad.items():
            print(f"{l}: {len(m)} missing, for example:", *m[:5], sep="\n  ")
        sys.exit(1)
    print("built", ", ".join(f"/{l}/" for l in LANGS))

if __name__ == "__main__":
    main()
