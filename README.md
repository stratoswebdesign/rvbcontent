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
| `/kapcsolat/` | Konzultációkérő űrlap; a kitöltött adatokkal a látogató levelezőprogramját nyitja meg (`data-form-mode="mailto"`), a weboldal nem továbbít adatot |
| `/kapcsolat/koszonjuk/` | Köszönőoldal (noindex), csak valódi fogadó-válasz után |
| `/adatkezeles/`, `/impresszum/` | Adatkezelési tájékoztató (hatályos 2026. november 17-től) és impresszum a cégjegyzék adataival (e-cegjegyzek.hu, 01-09-470745) |
| `/404.html` | Hibaoldal (noindex) |
| `/kontakt/`, `/contacts/`, `/csapatunk/`, `/team/`, `/szolgaltatasok/`, `/shop/` | A régi oldal címei: azonnal továbbító, noindex oldalak (`REDIRECTS` a `tools/build-pages.py`-ban) |
| `/sitemap.xml`, `/llms.txt`, `/robots.txt` | Az első kettőt a build generálja a meta-leírásokból; a robots.txt kizárja a `/tools/` mappát |

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

- **`build-pages.py`:** minden oldalt a `tools/pages/` és `tools/partials/` forrásokból generál, beágyazza az ikonokat, és elkészíti a sitemap.xml-t, az llms.txt-t és a régi címek átirányító oldalait.
- **`check-site.py`:** ellenőrzi a belső linkeket, az asseteket, a duplikált id-ket, a látható helyőrzőket és a külső erőforrásokat.
- **`make-images.py`:** elkészíti az OG-képet és a borítót; macOS-en fut (qlmanage, sips).

## Kitelepítés

- **Tárhely: GitHub Pages, `main` ág, gyökér, saját domain (`CNAME`: rvbcontent.hu).** Minden push a `main`-re élesít. A repó gyökere nyilvános, ezért a `tools/` és a `README.md` is elérhető; a robots.txt kizárja a `/tools/` mappát. A `_forras/` és az `_atadas/` nincs a repóban (`.gitignore`). A `.nojekyll` miatt a Pages a fájlokat változtatás nélkül szolgálja ki.
- **DNS (a domainszolgáltatónál):** az `rvbcontent.hu` A rekordjai 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153; AAAA rekordjai 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153; a `www` CNAME rekordja `stratoswebdesign.github.io`. A www → rvbcontent.hu átirányítást a GitHub automatikusan elvégzi. A tanúsítvány kiadása után a repó Settings → Pages oldalán be kell kapcsolni az „Enforce HTTPS” opciót.
- **Útvonal-előtag:** `PATH_PREFIX = ""` a `tools/build-pages.py`-ban. Domain nélküli GitHub Pages projektoldalon (`stratoswebdesign.github.io/rvbcontent/`) `"/rvbcontent"` kell, majd újraépítés. A CSS relatív útvonalakat használ.
- **Átirányítások:** a GitHub Pages nem kezel szerveroldali 301-et, ezért a régi címekre azonnal továbbító oldalak készülnek (`REDIRECTS`). A 410-es címek 404-et adnak. A `_redirects` Netlify-formátumú tartalék, ha az oldal Netlifyra költözik.
- **Űrlap:** `data-form-mode="mailto"`: a látogató levelezőprogramja nyílik meg a kitöltött adatokkal, összhangban az adatkezelési tájékoztató 6. pontjával. Netlifyn `"netlify"` is választható, de akkor a tájékoztatót módosítani kell.
- **Videó:** a tárhelynek Range-kéréseket kell kezelnie; a GitHub Pages ezt teszi (206 válasz).
- **Sütisáv:** ki van kapcsolva, mert nincs mérőkód. Mérés bekötésekor: `COOKIE_BANNER = True` a `tools/build-pages.py`-ban.
- **Futásidőben nincs külső erőforrás.** Licencek: `assets/fonts/OFL-*.txt`, `assets/js/vendor/LICENSE-*`.
