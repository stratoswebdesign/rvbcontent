"""Az összes oldal összeállítása.

Források: tools/pages/*.html (oldaltartalom + <!--meta {...}--> fejléc),
tools/partials/ (header, footer, cta, kv, cookie), tools/icons.py (3D ikonok).
Tokenek az oldalakban: <!--icon:név--> és <!--part:cta-->.
Kimenet: az oldalak, a régi címek átirányító oldalai (REDIRECTS), sitemap.xml és llms.txt.

Futtatás a projekt gyökeréből:  python3 tools/build-pages.py
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import icons  # noqa: E402

BASE = "https://rvbcontent.hu"
# Útvonal-előtag a gyökér-relatív hivatkozások elé (href, src, poster, action). Saját domainen
# (rvbcontent.hu, CNAME) ""; domain nélküli GitHub Pages projektoldalon "/rvbcontent".
PATH_PREFIX = ""
# A régi oldal címei (a _redirects 301-es sorai). A GitHub Pages nem ismer szerveroldali átirányítást,
# ezért ezekre azonnal továbbító, noindex oldal készül; a 410-es címek a 404-es oldalt kapják.
REDIRECTS = {
    "szolgaltatasok": "/",
    "kontakt": "/kapcsolat/",
    "contacts": "/kapcsolat/",
    "csapatunk": "/rolunk/",
    "team": "/rolunk/",
    "shop": "/",
}
VENDOR = "/assets/js/vendor"  # GSAP 3.13.0, ScrollTrigger, Lenis 1.1.20 – helyi másolat, nincs külső CDN
OG_IMAGE = BASE + "/assets/img/og-reverb-content.jpg"
TODAY = datetime.date.today().isoformat()  # a sitemap lastmod értéke: az építés napja


def read(*parts):
    return open(os.path.join(HERE, *parts), encoding="utf-8").read()


HEADER = read("partials", "header.html")
FOOTER = read("partials", "footer.html")
# Sütisáv csak mérő- vagy hirdetési kód esetén kell; a megrendelő szerint most nincs ilyen.
COOKIE_BANNER = False
if COOKIE_BANNER:
    FOOTER += read("partials", "cookie.html")
PARTS = {"cta": read("partials", "cta.html"), "kv": read("partials", "kv.html")}
ICONS = icons.all_icons()
DEFS = ('  <svg class="ico-defs" aria-hidden="true" focusable="false"><defs>'
        '<radialGradient id="ico-pool"><stop offset="0" stop-color="#25f79c" stop-opacity=".28"/>'
        '<stop offset="1" stop-color="#25f79c" stop-opacity="0"/></radialGradient></defs></svg>\n')

# Inline, festés előtt: .js; .is-still (rendszerszintű csökkentett mozgás); .is-paused (a látogató
# szüneteltette a mozgást, tárolt preferencia); .js-pending (a hero rejtve, amíg a JS át nem veszi);
# .is-intro (csak a főoldalon, munkamenetenként egyszer). Biztonsági időzítő: 3 mp után minden látszik.
BOOT = ('<script>(function(d){var r=matchMedia("(prefers-reduced-motion: reduce)").matches;'
        'd.classList.add("js");if(r)d.classList.add("is-still");else d.classList.add("js-pending");'
        'try{if(localStorage.getItem("rvb-motion")==="paused")d.classList.add("is-paused");'
        'if(!r&&d.hasAttribute("data-intro")&&!sessionStorage.getItem("rvb-intro"))'
        '{d.classList.add("is-intro");sessionStorage.setItem("rvb-intro","1")}}catch(e){}'
        'setTimeout(function(){d.classList.remove("js-pending","is-intro")},3000)})(document.documentElement)</script>')


def set_current(block, path):
    if not path:
        return block
    return re.sub(r'(<a (?:class="nav__link" )?href="%s")' % re.escape(path), r'\1 aria-current="page"', block)


def head(meta):
    canonical = "" if meta.get("nocanonical") else '  <link rel="canonical" href="%s%s">\n' % (BASE, meta["path"])
    robots = '  <meta name="robots" content="noindex, follow">\n' if meta.get("noindex") else ""
    ld = []
    if meta.get("crumb"):
        ld.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Főoldal", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": meta["crumb"], "item": BASE + meta["path"]},
            ],
        })
    if meta.get("jsonld"):
        ld.append(meta["jsonld"])
    ld_html = "".join('  <script type="application/ld+json">%s</script>\n' % json.dumps(x, ensure_ascii=False) for x in ld)
    og_desc = meta.get("ogDescription", meta["description"])
    intro = " data-intro" if meta.get("intro") else ""
    return f"""<!doctype html>
<html lang="hu"{intro}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{meta["title"]}</title>
  <meta name="description" content="{meta["description"]}">
{canonical}{robots}  <meta property="og:type" content="website">
  <meta property="og:locale" content="hu_HU">
  <meta property="og:site_name" content="Reverb Content">
  <meta property="og:title" content="{meta["title"]}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:url" content="{BASE}{meta["path"]}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="REVERB – tovább élő tartalom. Videógyártás, ami a forgatás után is dolgozik.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#020002">
  <link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <link rel="preload" href="/assets/fonts/big-shoulders-display-300-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/fonts.css">
  <link rel="stylesheet" href="/assets/css/style.css">
  {BOOT}
  <script src="{VENDOR}/gsap.min.js" defer></script>
  <script src="{VENDOR}/ScrollTrigger.min.js" defer></script>
  <script src="{VENDOR}/lenis.min.js" defer></script>
  <script src="/assets/js/main.js" defer></script>
{ld_html}</head>
<body>
"""


def expand(body):
    body = re.sub(r"<!--part:(\w+)-->", lambda m: PARTS[m.group(1)], body)

    def icon(m):
        name = m.group(1)
        if name not in ICONS:
            raise SystemExit("ismeretlen ikon: " + name)
        return ICONS[name]
    return re.sub(r"<!--icon:([\w-]+)-->", icon, body)


def prefix_paths(page):
    if not PATH_PREFIX:
        return page
    return re.sub(r'(\s(?:href|src|poster|action)=")/(?!/)', r"\g<1>" + PATH_PREFIX + "/", page)


def indent(text, pad="    "):
    return "\n".join((pad + line) if line.strip() else "" for line in text.splitlines())


def write(rel, text):
    out = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("wrote", rel, "(%d KB)" % (len(text.encode("utf-8")) // 1024))


def redirect_page(target):
    url = PATH_PREFIX + target
    return f"""<!doctype html>
<html lang="hu">
<head>
  <meta charset="utf-8">
  <title>Átirányítás | Reverb Content</title>
  <meta name="robots" content="noindex">
  <link rel="canonical" href="{BASE}{target}">
  <meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
  <p>Az oldal új címe: <a href="{url}">rvbcontent.hu{target}</a></p>
</body>
</html>
"""


def sitemap(metas):
    urls = "".join("  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n" % (BASE, m["path"], TODAY) for m in metas)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!-- A tools/build-pages.py generálja: minden indexelhető oldal (noindex és hibaoldal nélkül). -->\n"
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")


def llms(metas):
    # llms.txt (llmstxt.org): rövid összefoglaló nyelvi modelleknek; a leírások az oldalak meta-leírásai.
    home = next(m for m in metas if m["path"] == "/")
    org = next(x for x in home["jsonld"]["@graph"] if x["@type"] == "Organization")
    groups = {"Oldalak": [], "Esettanulmányok": [], "Optional": []}
    for m in metas:
        key = "Esettanulmányok" if m["path"].startswith("/munkak/") else "Optional" if m["path"] in ("/adatkezeles/", "/impresszum/") else "Oldalak"
        title = m["title"].replace(" | Reverb Content", "")
        groups[key].append("- [%s](%s%s): %s" % (title, BASE, m["path"], m["description"]))
    text = "# Reverb Content\n\n> %s\n\n%s Kapcsolat: %s, %s.\n" % (
        org["description"], home["description"], org["email"], "+36 20 382 6638")
    for key, lines in groups.items():
        text += "\n## %s\n\n%s\n" % (key, "\n".join(lines))
    return text


metas = []
for name in sorted(os.listdir(os.path.join(HERE, "pages"))):
    if not name.endswith(".html"):
        continue
    raw = read("pages", name)
    m = re.match(r"<!--meta\s*(\{.*?\})\s*-->\s*", raw, re.S)
    meta = json.loads(m.group(1))
    if not meta.get("noindex"):
        metas.append(meta)
    body = expand(raw[m.end():].rstrip())
    page = (
        head(meta)
        + DEFS
        + set_current(HEADER, meta.get("nav", meta["path"]))
        + '  <main id="tartalom">\n'
        + indent(body)
        + "\n  </main>\n\n"
        + FOOTER
        + "</body>\n</html>\n"
    )
    write(meta["out"], prefix_paths(page))

for old, target in REDIRECTS.items():
    write(old + "/index.html", redirect_page(target))

metas.sort(key=lambda m: m["path"])
write("sitemap.xml", sitemap(metas))
write("llms.txt", llms(metas))
