"""Az összes oldal összeállítása.

Források: tools/pages/*.html (oldaltartalom + <!--meta {...}--> fejléc),
tools/partials/ (header, footer, cta, kv, cookie), tools/icons.py (3D ikonok).
Tokenek az oldalakban: <!--icon:név--> és <!--part:cta-->.

Futtatás a projekt gyökeréből:  python3 tools/build-pages.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import icons  # noqa: E402

BASE = "https://rvbcontent.hu"
# Útvonal-előtag a gyökér-relatív hivatkozások elé (href, src, poster, action). GitHub Pages
# projektoldalon (stratoswebdesign.github.io/rvbcontent/) "/rvbcontent"; saját domainen vagy Netlifyn "".
PATH_PREFIX = "/rvbcontent"
VENDOR = "/assets/js/vendor"  # GSAP 3.13.0, ScrollTrigger, Lenis 1.1.20 – helyi másolat, nincs külső CDN
OG_IMAGE = BASE + "/assets/img/og-reverb-content.jpg"


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


for name in sorted(os.listdir(os.path.join(HERE, "pages"))):
    if not name.endswith(".html"):
        continue
    raw = read("pages", name)
    m = re.match(r"<!--meta\s*(\{.*?\})\s*-->\s*", raw, re.S)
    meta = json.loads(m.group(1))
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
    page = prefix_paths(page)
    out = os.path.join(SITE, meta["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("wrote", meta["out"], "(%d KB)" % (len(page.encode("utf-8")) // 1024))
