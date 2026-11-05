"""Reprodukálható ellenőrzés a generált oldalakra.

Futtatás a projekt gyökeréből:  python3 tools/check-site.py
Ellenőrzi: belső linkek és horgonyok, hiányzó assetek (HTML + CSS url()), duplikált id-k,
<use href="#…"> hivatkozások, látható helyőrzők ([…] vagy .ph), külső erőforrás-hivatkozások.
Kilépési kód: 0, ha nincs hiba; a jogi oldalak helyőrzői ismert nevezési blokkerként külön jelennek meg.
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"tools", "_forras", "_atadas", ".claude", ".git", "node_modules"}
KNOWN_BLOCKER_PAGES = {"adatkezeles/index.html", "impresszum/index.html"}
BRACKET = re.compile(r"\[[^\[\]\n]{2,}\]")
# Ugyanaz az útvonal-előtag, amellyel a build-pages.py generál (GitHub Pages: "/rvbcontent").
PATH_PREFIX = re.search(r'^PATH_PREFIX = "([^"]*)"', open(os.path.join(ROOT, "tools", "build-pages.py"), encoding="utf-8").read(), re.M).group(1)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.uses, self.ph, self.text = [], [], [], 0, []
        self.skip = 0
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "link" and (a.get("rel") or "") == "canonical":
            return  # kanonikus URL, nem betöltött erőforrás
        for key in ("href", "src", "poster"):
            if a.get(key) and not (tag == "use"):
                self.refs.append((tag, key, a[key]))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                self.refs.append((tag, "srcset", part.strip().split(" ")[0]))
        if tag == "use" and a.get("href"):
            self.uses.append(a["href"])
        if "ph" in (a.get("class") or "").split():
            self.ph += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def pages():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            if f.endswith(".html"):
                full = os.path.join(dirpath, f)
                yield os.path.relpath(full, ROOT).replace(os.sep, "/"), full


def resolve(page_rel, url):
    """URL → (fájl a lemezen, horgony) vagy None külső/nem fájl hivatkozásnál."""
    u = urlparse(url)
    if u.scheme in ("http", "https", "mailto", "tel", "data", "javascript") or url.startswith("//"):
        return None
    path = unquote(u.path)
    if not path:
        return page_rel, u.fragment
    if path.startswith("/"):
        if PATH_PREFIX and not (path + "/").startswith(PATH_PREFIX + "/"):
            return "(előtag nélkül)" + path, u.fragment  # a tárhelyen nem létező cél → hiba
        rel = path[len(PATH_PREFIX):].lstrip("/")
    else:
        rel = os.path.normpath(os.path.join(os.path.dirname(page_rel), path)).replace(os.sep, "/")
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    elif not os.path.splitext(rel)[1]:
        rel += "/index.html"
    return rel, u.fragment


def main():
    errors, blockers, external = [], [], set()
    parsed = {}
    for rel, full in pages():
        p = Page()
        p.feed(open(full, encoding="utf-8").read())
        parsed[rel] = p

    for rel, p in sorted(parsed.items()):
        dup = sorted({i for i in p.ids if p.ids.count(i) > 1})
        if dup:
            errors.append("%s: duplikált id: %s" % (rel, ", ".join(dup)))
        for ref in p.uses:
            if ref.startswith("#") and ref[1:] not in p.ids:
                errors.append("%s: <use> hivatkozás nem létező id-re: %s" % (rel, ref))
        for tag, key, url in p.refs:
            if url.startswith(("http://", "https://", "//")):
                if tag in ("script", "link", "img", "source", "video", "iframe"):
                    external.add("%s %s=%s" % (tag, key, url))
                continue
            r = resolve(rel, url)
            if not r:
                continue
            target, frag = r
            if not os.path.exists(os.path.join(ROOT, target)):
                errors.append("%s: hiányzó cél: %s (%s)" % (rel, url, tag))
                continue
            if frag and target.endswith(".html"):
                tp = parsed.get(target)
                if tp is not None and frag not in tp.ids:
                    errors.append("%s: hiányzó horgony: %s" % (rel, url))
        visible = " ".join(p.text)
        brackets = BRACKET.findall(visible)
        if p.ph or brackets:
            msg = "%s: %d .ph elem, %d [..] szövegrész" % (rel, p.ph, len(brackets))
            (blockers if rel in KNOWN_BLOCKER_PAGES else errors).append(msg + ("" if rel in KNOWN_BLOCKER_PAGES else "  " + " | ".join(brackets[:5])))

    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "assets")):
        for f in filenames:
            if f.endswith(".css"):
                full = os.path.join(dirpath, f)
                css = open(full, encoding="utf-8").read()
                for url in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", css):
                    if url.startswith(("data:", "#", "http")):
                        if url.startswith("http"):
                            external.add("css url=" + url)
                        continue
                    target = url.lstrip("/") if url.startswith("/") else os.path.relpath(os.path.join(dirpath, url), ROOT)
                    if (url.startswith("/") and PATH_PREFIX) or not os.path.exists(os.path.join(ROOT, target)):
                        errors.append("%s: hiányzó CSS-asset: %s" % (os.path.relpath(full, ROOT), url))

    print("Ellenőrzött oldalak: %d" % len(parsed))
    print("\nHIBÁK (%d)" % len(errors))
    for e in errors:
        print("  - " + e)
    print("\nISMERT NEVEZÉSI BLOKKEREK – jogi oldalak hiányzó adatai (%d)" % len(blockers))
    for b in blockers:
        print("  - " + b)
    print("\nKÜLSŐ ERŐFORRÁSOK (%d)" % len(external))
    for x in sorted(external):
        print("  - " + x)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
