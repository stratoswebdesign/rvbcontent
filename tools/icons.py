"""Reverb Content – izometrikus 3D SVG ikonrendszer.

Minden ikon ugyanabból a néhány 3D primitívből (hasáb, henger, gömb) épül, egy közös
6×6-os talapzaton, azonos vetítéssel és fényezéssel: sötét matt testek, menta peremfény,
világító (emisszív) részletek. A színek CSS-változókból jönnek (.ico), így hoverre
átszínezhetők. Rétegek: ico__base (talapzat), ico__obj (tárgy), ico__fx (fények).

Használat: python3 tools/icons.py  → kiírja az ikonokat JSON-ként (a build olvassa).
"""
import json
import math
import sys

C = math.cos(math.pi / 6)
SN = 0.5
S = 9.0          # px / egység
OX, OY = 60.0, 58.0


def P(x, y, z):
    return (OX + (x - y) * C * S, OY + (x + y) * SN * S - z * S)


def fmt(ps):
    return " ".join("%.1f,%.1f" % p for p in ps)


def poly(ps, cls):
    return '<polygon class="%s" points="%s"/>' % (cls, fmt(ps))


def line(a, b, cls):
    return '<line class="%s" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (cls, a[0], a[1], b[0], b[1])


def polyline(ps, cls):
    return '<polyline class="%s" points="%s"/>' % (cls, fmt(ps))


def ring(n=48):
    return [2 * math.pi * i / n for i in range(n)]


def hull(points):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


# ---------- primitívek ----------

def box(x, y, z, w, d, h, top="f-t", left="f-l", right="f-r", rim=True):
    t = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    r = [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)]
    l = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    out = [poly(l, left), poly(r, right), poly(t, top)]
    out.append(line(P(x + w, y + d, z), P(x + w, y + d, z + h), "edge"))
    if rim:
        out.append(poly(t, "rim"))
    return out


def ghost_box(x, y, z, w, d, h):
    a = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y, z), P(x + w, y, z + h), P(x, y, z + h), P(x, y + d, z + h), P(x, y + d, z)]
    return [poly(a, "ghost"), line(P(x + w, y + d, z), P(x + w, y + d, z + h), "ghost"),
            polyline([P(x, y + d, z + h), P(x + w, y + d, z + h), P(x + w, y, z + h)], "ghost")]


def glass_box(x, y, z, w, d, h):
    t = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    r = [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)]
    l = [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    back = [line(P(x, y, z), P(x + w, y, z), "ghost"), line(P(x, y, z), P(x, y + d, z), "ghost"), line(P(x, y, z), P(x, y, z + h), "ghost")]
    return back, [poly(l, "glass"), poly(r, "glass"), poly(t, "glass")]


def cyl_v(cx, cy, z0, z1, r, top="f-t", rim=True):
    """Függőleges henger. Az oldal két félre bontva (bal világosabb, jobb sötétebb)."""
    def at(t, z):
        return P(cx + r * math.cos(t), cy + r * math.sin(t), z)
    deg = math.radians
    right = [at(deg(a), z0) for a in range(-45, 46, 6)] + [at(deg(a), z1) for a in range(45, -46, -6)]
    left = [at(deg(a), z0) for a in range(45, 136, 6)] + [at(deg(a), z1) for a in range(135, 44, -6)]
    cap = [at(t, z1) for t in ring()]
    out = [poly(left, "f-l"), poly(right, "f-r"), poly(cap, top)]
    if rim:
        out.append(poly(cap, "rim"))
    return out


def iso_circle(cx, cy, z, r, cls):
    return poly([P(cx + r * math.cos(t), cy + r * math.sin(t), z) for t in ring()], cls)


def cyl_y(cx, cz, y0, y1, r, face="f-l", glass=0.66, emissive=True):
    """Az y tengely mentén fekvő henger (a néző felé – balra lent – néző lencse, tárcsa)."""
    def at(t, y, rr=r):
        return P(cx + rr * math.cos(t), y, cz + rr * math.sin(t))
    side = hull([at(t, y0) for t in ring()] + [at(t, y1) for t in ring()])
    out = [poly(side, "f-t"), poly(side, "rim"), poly([at(t, y1) for t in ring()], face)]
    if glass:
        out.append(poly([at(t, y1, r * glass) for t in ring()], "f-g"))
    if emissive:
        out.append(poly([at(t, y1, r * 0.84) for t in ring()], "rim-e"))
    return out


def sphere(cx, cy, cz, r):
    x, y = P(cx, cy, cz)
    return ['<circle class="f-t" cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, y, r * S),
            '<path class="f-r" d="M%.1f %.1fA%.1f %.1f 0 0 1 %.1f %.1fA%.1f %.1f 0 0 0 %.1f %.1fZ"/>' % (
                x + r * S * 0.2, y - r * S * 0.98, r * S, r * S, x + r * S * 0.2, y + r * S * 0.98, r * S * 0.75, r * S, x + r * S * 0.2, y - r * S * 0.98),
            '<circle class="rim" cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, y, r * S)]


def face_y(x0, x1, y, z0, z1, cls):
    """Téglalap a +y (bal-elülső) síkon – képernyő, felirat, csík."""
    return poly([P(x0, y, z0), P(x1, y, z0), P(x1, y, z1), P(x0, y, z1)], cls)


def face_x(x, y0, y1, z0, z1, cls):
    return poly([P(x, y0, z0), P(x, y1, z0), P(x, y1, z1), P(x, y0, z1)], cls)


def face_z(x0, y0, x1, y1, z, cls):
    return poly([P(x0, y0, z), P(x1, y0, z), P(x1, y1, z), P(x0, y1, z)], cls)


def base():
    """Közös talapzat: vékony lap + fénytócsa."""
    out = box(0.3, 0.3, 0, 5.4, 5.4, 0.32, top="b-t", left="b-l", right="b-r", rim=False)
    t = [P(0.3, 0.3, 0.32), P(5.7, 0.3, 0.32), P(5.7, 5.7, 0.32), P(0.3, 5.7, 0.32)]
    out.append(poly(t, "b-rim"))
    cx, cy = P(3, 3, 0.32)
    out.append('<ellipse class="pool" cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f"/>' % (cx, cy, 2.5 * C * S * 1.414, 2.5 * SN * S * 1.414))
    return out


# ---------- ikonok ----------
Z = 0.32


def i_camera():  # imázsfilm – filmkamera
    obj = []
    obj += box(1.1, 1.3, Z, 3.4, 2.4, 2.2)
    obj += cyl_y(2.7, Z + 1.15, 3.7, 4.9, 0.82)
    obj += cyl_y(1.85, Z + 3.05, 2.1, 2.45, 0.78, face="f-t", glass=0.25, emissive=False)
    obj += cyl_y(3.45, Z + 3.05, 2.1, 2.45, 0.78, face="f-t", glass=0.25, emissive=False)
    fx = ['<circle class="f-e" cx="%.1f" cy="%.1f" r="1.8"/>' % P(4.5, 1.7, Z + 1.85)]
    return obj, fx


def i_clapper():  # reklámfilm – csapó
    obj = []
    obj += box(1.0, 2.7, Z, 4.0, 0.55, 2.4)
    for i, (a, b) in enumerate([(1.4, 3.4), (1.4, 2.6)]):
        obj.append(face_y(1.4, 4.2 if i == 0 else 3.2, 3.25, Z + 0.55 + i * 0.55, Z + 0.75 + i * 0.55, "f-g"))
    # alsó csíkos léc
    obj += box(1.0, 2.7, Z + 2.4, 4.0, 0.55, 0.45, rim=False)
    n = 6
    for i in range(n):
        x0 = 1.0 + 4.0 * i / n
        x1 = 1.0 + 4.0 * (i + 1) / n
        obj.append(poly([P(x0 + 0.25, 3.25, Z + 2.4), P(x1 + 0.25, 3.25, Z + 2.4), P(x1, 3.25, Z + 2.85), P(x0, 3.25, Z + 2.85)], "f-e" if i % 2 == 0 else "f-g"))
    # nyitott kar (forgatva a bal csukló körül)
    a = math.radians(24)
    hx, hz, L, T, y0, y1 = 1.0, Z + 2.95, 4.1, 0.42, 2.7, 3.25

    def R(u, v, y):
        return P(hx + u * math.cos(a) - v * math.sin(a), y, hz + u * math.sin(a) + v * math.cos(a))
    top = [R(0, T, y0), R(L, T, y0), R(L, T, y1), R(0, T, y1)]
    end = [R(L, 0, y0), R(L, 0, y1), R(L, T, y1), R(L, T, y0)]
    front = [R(0, 0, y1), R(L, 0, y1), R(L, T, y1), R(0, T, y1)]
    fx = []
    obj += [poly(end, "f-r"), poly(top, "f-t"), poly(front, "f-l")]
    for i in range(n):
        u0, u1 = L * i / n, L * (i + 1) / n
        if i % 2 == 0:
            fx.append(poly([R(u0 + 0.22, 0, y1), R(u1 + 0.22, 0, y1), R(u1, T, y1), R(u0, T, y1)], "f-e"))
    obj.append(poly(top, "rim"))
    return obj, fx


def i_product():  # termékvideó – termék a forgótányéron
    obj = []
    obj += cyl_v(3, 3, Z, Z + 0.35, 2.2)
    obj += box(2.0, 2.0, Z + 0.35, 2.0, 2.0, 2.0)
    obj.append(face_x(4.0, 2.4, 3.6, Z + 1.0, Z + 1.35, "f-g"))
    cx, cy = P(3, 3, Z + 1.6)
    fx = ['<ellipse class="orbit" cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f"/>' % (cx, cy, 2.55 * C * S * 1.414, 2.55 * SN * S * 1.414)]
    fx.append('<circle class="f-e" cx="%.1f" cy="%.1f" r="2"/>' % (cx + 2.55 * C * S * 1.414, cy))
    return obj, fx


def i_person():  # toborzó videó – munkatárs
    obj = []
    obj += cyl_v(2.8, 3.2, Z, Z + 2.0, 0.95)
    obj += sphere(2.8, 3.2, Z + 2.75, 0.62)
    fx = box(3.9, 1.0, Z + 2.2, 1.1, 0.35, 0.8, top="f-e", left="f-e", right="f-e", rim=False)
    fx = [f.replace("edge", "ghost") for f in fx]
    x, y = P(4.45, 1.35, Z + 2.6)
    fx.append('<polyline class="tick" points="%.1f,%.1f %.1f,%.1f %.1f,%.1f"/>' % (x - 3.2, y - 0.6, x - 1.2, y + 1.6, x + 2.6, y - 2.8))
    return obj, fx


def i_phone():  # social – álló telefon
    obj = []
    obj += box(2.1, 2.6, Z, 1.8, 0.3, 3.25)
    obj.append(face_y(2.25, 3.75, 2.9, Z + 0.25, Z + 3.0, "f-g"))
    fx = []
    a, b, c = P(2.85, 2.9, Z + 1.95), P(2.85, 2.9, Z + 1.25), P(3.35, 2.9, Z + 1.6)
    fx.append('<polygon class="f-e" points="%s"/>' % fmt([a, b, c]))
    for (x, y, z, r) in [(4.6, 2.2, Z + 3.4, 1.9), (4.1, 1.2, Z + 4.3, 1.4), (5.0, 1.4, Z + 2.5, 1.1)]:
        fx.append('<circle class="f-e" cx="%.1f" cy="%.1f" r="%.1f"/>' % (P(x, y, z) + (r,)))
    return obj, fx


def i_chart():  # hirdetéskezelés – növekvő oszlopok
    obj = []
    obj += box(0.9, 3.7, Z, 1.1, 1.1, 1.1)
    obj += box(2.45, 2.45, Z, 1.1, 1.1, 2.1)
    obj += box(4.0, 1.2, Z, 1.1, 1.1, 3.2, top="f-e")
    fx = [polyline([P(1.45, 4.25, Z + 1.8), P(3.0, 3.0, Z + 2.8), P(4.55, 1.75, Z + 4.3)], "trend")]
    x, y = P(4.55, 1.75, Z + 4.3)
    fx.append('<circle class="f-e" cx="%.1f" cy="%.1f" r="2.2"/>' % (x, y))
    return obj, fx


def i_photo():  # céges fotózás – fényképezőgép
    obj = []
    obj += box(1.2, 2.0, Z, 3.6, 1.5, 2.0)
    obj += box(2.5, 2.25, Z + 2.0, 1.2, 1.0, 0.5)
    obj += cyl_y(3.0, Z + 1.0, 3.5, 4.5, 0.78)
    fx = box(1.45, 2.3, Z + 2.0, 0.6, 0.6, 0.22, top="f-e", left="f-e", right="f-e", rim=False)
    fx = [f for f in fx if "edge" not in f]
    return obj, fx


def i_one():  # egy felelős – egy oszlop a három helyett
    obj = []
    back = ghost_box(0.8, 3.8, Z, 1.2, 1.2, 1.2) + ghost_box(3.9, 0.7, Z, 1.2, 1.2, 1.2)
    obj += back
    obj += box(2.35, 2.35, Z, 1.3, 1.3, 3.6, top="f-e")
    fx = [line(P(3.65, 3.65, Z + 0.3), P(3.65, 3.65, Z + 3.3), "beam")]
    return obj, fx


def i_calendar():  # egy határidő – naptár egy kiemelt nappal
    obj = []
    obj += box(1.0, 1.0, Z, 4.0, 4.0, 0.7)
    fx = []
    for i in range(4):
        for j in range(4):
            x0, y0 = 1.35 + i * 0.86, 1.35 + j * 0.86
            cls = "f-e" if (i, j) == (2, 2) else "cell"
            (fx if cls == "f-e" else obj).append(face_z(x0, y0, x0 + 0.6, y0 + 0.6, Z + 0.7, cls))
    obj += cyl_v(1.8, 1.25, Z + 0.7, Z + 1.35, 0.22)
    obj += cyl_v(4.2, 1.25, Z + 0.7, Z + 1.35, 0.22)
    return obj, fx


def i_layers():  # egy vizuális világ – egymásra illeszkedő rétegek
    obj = []
    groups = []
    for k, z in enumerate([Z + 0.5, Z + 1.55, Z + 2.6]):
        g = box(1.0, 1.0, z, 4.0, 4.0, 0.22)
        groups.append('<g class="ico__layer" style="--k:%d">%s</g>' % (k, "".join(g)))
    obj += groups
    fx = ['<g class="ico__layer" style="--k:2">%s</g>' % face_z(2.4, 2.4, 3.6, 3.6, Z + 2.82, "f-e")]
    return obj, fx


def i_budget():  # átlátható keret – üvegkocka, benne a tartalom
    back, front = glass_box(1.2, 1.2, Z, 3.6, 3.6, 3.6)
    obj = back + box(2.35, 2.35, Z, 1.3, 1.3, 1.3, top="f-e") + front
    return obj, []


def i_result():  # mérhető eredmény – kijelző görbével
    obj = []
    obj += box(1.0, 2.8, Z, 4.0, 0.3, 2.7)
    obj.append(face_y(1.15, 4.85, 3.1, Z + 0.2, Z + 2.5, "f-g"))
    pts = [(1.4, 0.45), (2.1, 0.8), (2.7, 0.7), (3.4, 1.35), (4.0, 1.25), (4.6, 2.1)]
    fx = [polyline([P(x, 3.1, Z + 0.2 + z) for x, z in pts], "trend")]
    fx.append('<circle class="f-e" cx="%.1f" cy="%.1f" r="2.2"/>' % P(4.6, 3.1, Z + 2.3))
    return obj, fx


ICONS = {
    "camera": i_camera,
    "clapper": i_clapper,
    "product": i_product,
    "person": i_person,
    "phone": i_phone,
    "chart": i_chart,
    "photo": i_photo,
    "one": i_one,
    "calendar": i_calendar,
    "layers": i_layers,
    "budget": i_budget,
    "result": i_result,
}


def render(name):
    obj, fx = ICONS[name]()
    return ('<svg class="ico ico--%s" viewBox="0 0 120 120" aria-hidden="true" focusable="false">'
            '<g class="ico__base">%s</g><g class="ico__obj">%s</g><g class="ico__fx">%s</g></svg>') % (
        name, "".join(base()), "".join(obj), "".join(fx))


def all_icons():
    return {name: render(name) for name in ICONS}


if __name__ == "__main__":
    json.dump(all_icons(), sys.stdout, ensure_ascii=False)
