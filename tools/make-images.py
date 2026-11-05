"""OG-kép (1200×630 JPEG) és Awwwards-nevezési borító (1600×1200 PNG) – saját kompozíció.

A helyi woff2 betűk base64-ként kerülnek az SVG-be, a raszterezés macOS Quick Look-kal
(qlmanage) és sips-szel történik, így nincs külső szolgáltatás vagy függőség.
Futtatás a projekt gyökeréből (macOS):  python3 tools/make-images.py
Kimenet: assets/img/og-reverb-content.jpg, assets/img/reverb-content-awwwards-cover-1600x1200.png
"""
import base64
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MUTE, INK, PAPER, SIGNAL, RULE, STAGE2 = "#858197", "#020002", "#f7f7f8", "#25f79c", "#34313b", "#0c0810"


def b64(rel):
    return base64.b64encode(open(os.path.join(ROOT, rel), "rb").read()).decode()


FONTS = """
@font-face{font-family:'Big Shoulders Display';font-weight:300 400;src:url(data:font/woff2;base64,%s) format('woff2')}
@font-face{font-family:'Big Shoulders Display';font-weight:300 400;src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:U+0100-02BA}
@font-face{font-family:'DM Mono';src:url(data:font/woff2;base64,%s) format('woff2')}
@font-face{font-family:'DM Mono';src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:U+0100-02BA}
@font-face{font-family:'Schibsted Grotesk';font-weight:400 500;src:url(data:font/woff2;base64,%s) format('woff2')}
@font-face{font-family:'Schibsted Grotesk';font-weight:400 500;src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:U+0100-02BA}
""" % (
    b64("assets/fonts/big-shoulders-display-300-latin.woff2"), b64("assets/fonts/big-shoulders-display-300-latin-ext.woff2"),
    b64("assets/fonts/dm-mono-400-latin.woff2"), b64("assets/fonts/dm-mono-400-latin-ext.woff2"),
    b64("assets/fonts/schibsted-grotesk-400-latin.woff2"), b64("assets/fonts/schibsted-grotesk-400-latin-ext.woff2"),
)
LOGO = b64("assets/img/reverb-content-logo.png")
# a weboldal kulcsvizuálja (tools/partials/kv.html) – ugyanaz a szimbólum
KV = open(os.path.join(HERE, "partials", "kv.html"), encoding="utf-8").read()
KV_DEFS = KV[KV.index("<defs>") + 6:KV.index("</defs>")]


def sliced(cx, base, size, x0, y0, x1, y1, shift, band, uid):
    """Metszésvonal mentén elcsúsztatott REVERB, menta sávval és két utókép-sávval."""
    def line(dy, th):
        return "%d,%.1f %d,%.1f %d,%.1f %d,%.1f" % (x0, y0 + dy, x1, y1 + dy, x1, y1 + dy + th, x0, y0 + dy + th)
    t = ("<text x='%d' y='%d' text-anchor='middle' style=\"font-family:'Big Shoulders Display';font-weight:300;"
         "font-size:%dpx;letter-spacing:%dpx;fill:%s\">REVERB</text>") % (cx, base, size, size // 110, PAPER)
    return f"""
<clipPath id="{uid}a"><polygon points="{x0},-50 {x1},-50 {x1},{y1} {x0},{y0}"/></clipPath>
<clipPath id="{uid}b"><polygon points="{x0},{y0} {x1},{y1} {x1},2000 {x0},2000"/></clipPath>
<polygon points="{line(band * 4.6, band * 0.32)}" fill="{SIGNAL}" opacity=".22"/>
<polygon points="{line(band * 2.6, band * 0.55)}" fill="{SIGNAL}" opacity=".5"/>
<g clip-path="url(#{uid}a)">{t}</g>
<g clip-path="url(#{uid}b)" transform="translate({shift[0]} {shift[1]})">{t}</g>
<polygon points="{line(0, band)}" fill="{SIGNAL}"/>"""


def corners(w, h, inset, length):
    p = lambda d: '<path d="%s"/>' % d
    i, l = inset, length
    return ('<g fill="none" stroke="%s" stroke-width="2">' % SIGNAL
            + p("M%d %dV%dh%d" % (i, i + l, i, l)) + p("M%d %dh%dv%d" % (w - i - l, i, l, l))
            + p("M%d %dv%dh%d" % (i, h - i - l, l, l)) + p("M%d %dh%dv%d" % (w - i - l, h - i, l, -l)) + "</g>")


def mono(x, y, text, size, fill=MUTE, anchor="start", ls=3):
    return ("<text x='%d' y='%d' text-anchor='%s' style=\"font-family:'DM Mono';font-size:%dpx;letter-spacing:%dpx;fill:%s\">%s</text>"
            % (x, y, anchor, size, ls, fill, text))


def og():
    w, h = 1200, 630
    body = (f'<rect width="{w}" height="{h}" fill="{INK}"/>'
            + '<g stroke="rgba(247,247,248,0.05)"><line x1="300" y1="0" x2="300" y2="630"/><line x1="600" y1="0" x2="600" y2="630"/><line x1="900" y1="0" x2="900" y2="630"/></g>'
            + sliced(600, 440, 300, 0, 520, 1200, 280, (20, 11), 11, "o")
            + corners(w, h, 28, 28)
            + f'<image x="52" y="50" width="40" height="40" href="data:image/png;base64,{LOGO}"/>'
            + mono(104, 77, "REVERB CONTENT", 15) + mono(1148, 77, "RVBCONTENT.HU", 15, anchor="end")
            + f"<text x='52' y='560' style=\"font-family:'Big Shoulders Display';font-weight:400;font-size:46px;fill:{PAPER}\">Videógyártás, ami a forgatás után is dolgozik.</text>"
            + mono(1148, 560, "TOVÁBB ÉLŐ TARTALOM", 20, SIGNAL, "end", 4))
    return w, h, body


def cover():
    """Nevezési borító: nagy metszéses REVERB + kontaktlap ugyanannak a KV-nak öt képarányáról."""
    w, h = 1600, 1200
    frames = [  # (képarány, szélesség, magasság, KV-kivágás)
        ("16:9 · FŐ KREATÍV", 444, 250, "0 0 1600 900"),
        ("9:16", 141, 250, "600 80 450 800"),
        ("1:1", 250, 250, "420 150 760 760"),
        ("4:5", 200, 250, "560 120 600 750"),
        ("3:2", 325, 217, "200 250 900 600"),
    ]
    x, bottom, row = 72, 1080, []
    for label, fw, fh, vb in frames:
        y = bottom - fh
        row.append(f'<rect x="{x}" y="{y}" width="{fw}" height="{fh}" fill="{STAGE2}"/>'
                   f'<svg x="{x}" y="{y}" width="{fw}" height="{fh}" viewBox="{vb}" preserveAspectRatio="xMidYMid slice">'
                   f'<use href="#kv" x="0" y="0" width="1600" height="900"/></svg>'
                   f'<rect x="{x}" y="{y}" width="{fw}" height="{fh}" fill="none" stroke="{RULE}" stroke-width="1.5"/>'
                   + mono(x, bottom + 34, label, 16))
        x += fw + 24
    body = (f'<rect width="{w}" height="{h}" fill="{INK}"/>'
            + '<g stroke="rgba(247,247,248,0.05)">' + "".join('<line x1="%d" y1="0" x2="%d" y2="1200"/>' % (v, v) for v in (400, 800, 1200)) + "</g>"
            + sliced(800, 600, 540, 0, 560, 1600, 340, (30, 16), 16, "c")
            + mono(240, 700, "TOVÁBB ÉLŐ TARTALOM", 28, SIGNAL, ls=6)
            + corners(w, h, 40, 40)
            + f'<image x="72" y="68" width="52" height="52" href="data:image/png;base64,{LOGO}"/>'
            + mono(140, 103, "REVERB CONTENT", 20) + mono(1528, 103, "RVBCONTENT.HU", 20, anchor="end")
            + mono(72, 806, "SAJÁT FORMÁTUMTANULMÁNY · EGY KREATÍV, ÖT KÉPARÁNY", 18, SIGNAL)
            + "".join(row))
    return w, h, body


def render(name, w, h, body, out, fmt):
    side = max(w, h)
    # Quick Look 768 pontos négyzetbe rajzol; a tartalmat középre tesszük, majd középről vágunk.
    vb = "%d %d %d %d" % (-(side - w) // 2, -(side - h) // 2, side, side)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="768" height="768" viewBox="{vb}">'
           f"<style>{FONTS}</style><defs>{KV_DEFS}</defs>{body}</svg>")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, name + ".svg")
    open(src, "w", encoding="utf-8").write(svg)
    subprocess.run(["qlmanage", "-t", "-s", str(side), "-o", tmp, src], check=True, capture_output=True)
    png = src + ".png"
    args = ["sips", "-c", str(h), str(w), png]
    if fmt == "jpeg":
        args += ["-s", "format", "jpeg", "-s", "formatOptions", "88"]
    subprocess.run(args + ["--out", out], check=True, capture_output=True)
    print("wrote", os.path.relpath(out, ROOT), "%dx%d" % (w, h))


if __name__ == "__main__":
    w, h, body = og()
    render("og", w, h, body, os.path.join(ROOT, "assets/img/og-reverb-content.jpg"), "jpeg")
    w, h, body = cover()
    render("cover", w, h, body, os.path.join(ROOT, "assets/img/reverb-content-awwwards-cover-1600x1200.png"), "png")
