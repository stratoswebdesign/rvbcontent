# rvbcontent.hu – új weboldal

Statikus HTML/CSS/JS weboldal, amelyet Python-szkriptek generálnak a `tools/` forrásaiból. Pozicionálás: videógyártásra épülő tartalom- és kampánypartner közép- és nagyvállalatoknak – „Egy forgatás. Egy teljes negyedév tartalma.” Hangnem: tegező, felnőtt üzleti hang.

**A blokkerek, az adatbekérés, a forrásleltár, a tesztjelentés és a régi oldal 27 pontos hibalistájának végleges állapota a belső átadási jegyzetben (`_atadas/ATADAS.md`) van. A jegyzet nem része ennek a repónak.**

## Oldalak

| URL | Tartalom |
|---|---|
| `/` | Hero a saját REVERB-kulcsvizuál előnézetével; partnerlogók; „három beszállító → egy csapat”; saját formátumtanulmány (egy kreatív, kilenc kivágás); két esettanulmány videó-előnézettel; vállalások; szolgáltatások vízszintes idővonala; folyamat; együttműködési formák; futó CTA |
| `/munkak/olajcserepont/`, `/munkak/varexo/` | A megrendelő esettanulmányai fejezetekre bontva, eredménytáblával és videókkal |
| `/egyuttmukodes/` | Brand Film / Content System / Growth Partner „-tól” árakkal, árképzés, GYIK |
| `/rolunk/` | Csapat (két tag, nyilvános forrásból), partnerek, a név jelentése |
| `/kapcsolat/` | Konzultációkérő űrlap; amíg nincs fogadó, nem küld (`data-form-mode="off"`), e-mail- és telefon-tartalékot ad |
| `/kapcsolat/koszonjuk/` | Köszönőoldal (noindex), csak valódi fogadó-válasz után |
| `/adatkezeles/`, `/impresszum/` | A megrendelő adatkezelési tervezete és cégadatai; a nyitott pontok jelölve – nevezési blokker |
| `/404.html` | Hibaoldal (noindex) |

## Dizájnrendszer

- **Színek:** a jelenlegi oldal fekete–menta palettája. Akcentus: `#25F79C`. Halvány szöveg: `--mute #858197` (legalább 4,5:1 minden háttéren).
- **Betűk (helyben, SIL OFL 1.1):**
  - Big Shoulders Display (címek)
  - Schibsted Grotesk (szöveg)
  - DM Mono (címkék, időkód)
  - A woff2-fájlok változó betűk: a `-300` a 300–400, a `-400` a 400–500 vastagságot fedi.
- **Saját vizuális anyagok:**
  - izometrikus 3D SVG ikonrendszer (`tools/icons.py`)
  - REVERB-kulcsvizuál (`tools/partials/kv.html`)
  - OG-kép és nevezési borító (`tools/make-images.py`)
- **Mozgás (GSAP 3.13 + ScrollTrigger, Lenis 1.1.20, helyben):**
  - AFTERIMAGE-utókép a görgetés sebességéből, nyugalomban teljesen éles
  - rögzített jelenetek; egyetlen vízszintes szakasz, mobilon natív lapozással
  - egyedi kurzor, mágneses gombok, letterbox-oldalváltás
  - a Munkák némított előnézete csak látótérben fut, szüneteltetéskor és csökkentett mozgásnál nem töltődik le
  - Ha a könyvtárak nem töltődnek be, minden statikusan, teljes állapotban látszik.
- **Hozzáférhetőség:**
  - „Mozgás szüneteltetése” kapcsoló tárolt preferenciával
  - `prefers-reduced-motion` követése: statikus, teljes tartalom
  - fókuszcsapdás mobilmenü, látható fókusz
- **Méret:**
  - JS: `main.js` 33 KB + vendor 131 KB
  - CSS: 60 KB
  - betűk: 160 KB
  - videók: 29 MB (`assets/video/`, 720×1280 H.264), `preload="none"`: betöltéskor csak a poszterek töltődnek (0,4 MB)
- **Képek:**
  - `assets/img/og-reverb-content.jpg` – 1200×630
  - `assets/img/reverb-content-awwwards-cover-1600x1200.png` – Awwwards-borító. Méretkövetelmény: [awwwards.com/faqs](https://www.awwwards.com/faqs/) → Submissions.

## Parancsok (a projekt gyökeréből)

```bash
python3 tools/build-pages.py
```

```bash
python3 tools/check-site.py
```

```bash
python3 tools/make-images.py
```

- **`build-pages.py`:** minden oldalt a `tools/pages/` és `tools/partials/` forrásokból generál, és beágyazza az ikonokat.
- **`check-site.py`:** ellenőrzi a belső linkeket, az asseteket, a duplikált id-ket, a látható helyőrzőket és a külső erőforrásokat.
- **`make-images.py`:** elkészíti az OG-képet és a borítót; macOS-en fut (qlmanage, sips).

## Kitelepítés

- **Ne kerüljön ki:** `_forras/`, `_atadas/`, `tools/`, `.claude/`, `README.md`.
- **Útvonal-előtag:** a GitHub Pages a `stratoswebdesign.github.io/rvbcontent/` alútvonalon szolgálja ki az oldalt, ezért `PATH_PREFIX = "/rvbcontent"` a `tools/build-pages.py`-ban. Saját domainen (rvbcontent.hu) vagy Netlifyn `""`, majd újraépítés. A CSS relatív útvonalakat használ, ezt nem kell állítani. A `.nojekyll` miatt a Pages a fájlokat változtatás nélkül szolgálja ki.
- **Netlify:** a `_redirects` (301/410) és a Netlify Forms azonnal használható. Az űrlapot `data-form-mode="netlify"`-re kell állítani (`tools/pages/kapcsolat.html`), majd újraépíteni.
- **Videó:** a tárhelynek Range-kéréseket kell kezelnie (a Netlify igen).
- **Sütisáv:** ki van kapcsolva, mert nincs mérőkód. Mérés bekötésekor: `COOKIE_BANNER = True` a `tools/build-pages.py`-ban.
- **Futásidőben nincs külső erőforrás.** Licencek: `assets/fonts/OFL-*.txt`, `assets/js/vendor/LICENSE-*`.
