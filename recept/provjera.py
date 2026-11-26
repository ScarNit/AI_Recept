"""Faza 6 – automatske (determinističke) provjere prije AI kritike.

* Svaka brojka u tekstu objave mora postojati u izvorima (webshop + brif).
* Ograničenja duljine teksta po polju (ista kao u promptu za izradu).
* Opis objave: duljina, broj hashtagova, poziv na radnju.
* Rezultati mjerenja iz rendera (prelijevanje teksta, smanjeni naslovi).
* Postoji li svaka referencirana fotografija proizvoda.
"""
from __future__ import annotations

import json
import re

# Riječi koje često znače zdravstvenu tvrdnju ili obećanje rezultata. Ako se pojave u
# objavi, a ne pojavljuju se u izvorima, provjera ih označi (dodano nakon ljudske dorade
# plana u kojem je AI dodao "bez nadutosti", a toga nema na stranici proizvoda).
RISKY = ["nadut", "želuc", "probavne tegobe", "lakša probava", "lakšu probavu", "mršav", "skidanje kila", "detoks", "detox", "liječ", "imunitet", "spaljuje", "sagorijeva",
         "topi masno", "ubrzava metabolizam", "garantira", "zajamčen", "bez nuspojava", "čudesn"]

# Oblici 2. lica jednine. Ako brend piše s "vi", njihova pojava je greška (dodano nakon što su
# prve verzije objava bile u ti-formi, a analiza Instagrama pokazala da brend piše s "vi").
TI_FORMA = re.compile(
    r"\b(tvoj\w*|tebi|tebe|tobom|ti\b|si\b|spremi|napiši|podijeli|osiguraj|saznaj|klikni|počasti|"
    r"pripremi|otvori|ugrabi|isprobaj|probaj|naruči|označi|pošalji|odaberi|biraš|znaš|želiš|"
    r"dobivaš|trebaš|možeš|imaš|voliš|ostavi|pogledaj|zaviri|javi|kupi|uzmi|iskoristi|prati|uživaj)\b", re.I)

LIMITS = {"nadnaslov": 28, "naslov": 48, "podnaslov": 160, "tekst": 160, "gumb": 24, "oznaka": 24}
NUM = re.compile(r"(?<![\w#])(\d{1,3}(?:[ .]\d{3})+|\d+)(?:[.,](\d+))?")


def _norm_numbers(text: str) -> set[str]:
    out = set()
    for m in NUM.finditer(text or ""):
        whole = re.sub(r"[ .]", "", m.group(1)) if re.search(r"[ .]\d{3}", m.group(1)) else m.group(1)
        frac = (m.group(2) or "").rstrip("0")
        out.add(f"{int(whole)}" + (f".{frac}" if frac else ""))
    return out


def corpus_numbers(sources: dict, brief: dict) -> set[str]:
    parts = [json.dumps(brief, ensure_ascii=False)]
    for p in sources.get("proizvodi", []):
        parts += [p.get("naziv", ""), p.get("kratki_opis", ""), p.get("kratki_opis_jsonld", ""),
                  p.get("dugi_opis", ""), p.get("tablica", ""), str(p.get("ocjena", "")),
                  str(p.get("broj_recenzija", ""))]
        for v in p.get("varijante", []):
            parts += [v.get("naziv", ""), f"{v.get('cijena', '')}"]
    # datum provjere cijene ("cijena na dan 25.11.") je legitimna brojka iz samog recepta
    for d in {p.get("dohvaceno", "")[:10] for p in sources.get("proizvodi", [])}:
        if d:
            y, m, dd = d.split("-")
            parts.append(f"{int(dd)}.{int(m)}. {int(dd)}.{m}. {y}")
    nums = set()
    for t in parts:
        nums |= _norm_numbers(t)
    return nums


def _post_texts(post: dict) -> list[tuple[str, str]]:
    items = []
    for i, k in enumerate(post.get("kadrovi", []), 1):
        for f in ("nadnaslov", "naslov", "podnaslov", "tekst", "gumb", "oznaka"):
            if k.get(f):
                items.append((f"kadar {i}.{f}", str(k[f]).replace("*", "")))
        if isinstance(k.get("brojka"), dict):
            items.append((f"kadar {i}.brojka", f"{k['brojka'].get('vrijednost', '')} {k['brojka'].get('opis', '')}"))
        for j, s in enumerate(k.get("stavke") or [], 1):
            txt = " ".join(str(v) for v in s.values()) if isinstance(s, dict) else str(s)
            items.append((f"kadar {i}.stavka {j}", txt))
        for c in k.get("cinjenice") or []:
            items.append((f"kadar {i}.cinjenica", str(c)))
        for o in k.get("opcije") or []:
            items.append((f"kadar {i}.opcija", str(o.get("naziv", ""))))
        st = k.get("story_naljepnica")
        if isinstance(st, dict):
            vals = [st.get("tekst"), st.get("pitanje")] + list(st.get("opcije") or [])
            items.append((f"kadar {i}.naljepnica", " ".join(str(v) for v in vals if v)))
    items.append(("opis", post.get("opis", "")))
    return items


def corpus_text(sources: dict) -> str:
    return " ".join(" ".join(str(p.get(k, "")) for k in ("kratki_opis", "dugi_opis", "tablica"))
                    for p in sources.get("proizvodi", [])).lower()


def check_post(post: dict, corpus: set[str], render_report: list | None, product_ids: set[str],
               source_text: str = "", oblik: str = "") -> dict:
    problems, warnings = [], []

    if oblik.startswith("vi"):
        ti = []
        for where, txt in _post_texts(post):
            ti += [f"„{m.group(0)}” ({where})" for m in TI_FORMA.finditer(txt)]
        if ti:
            problems.append("Ti-forma, a brend piše s 'vi': " + ", ".join(ti[:12]) + (" …" if len(ti) > 12 else ""))

    all_text = " ".join(t for _, t in _post_texts(post)).lower()
    risky = [w for w in RISKY if w in all_text and w not in source_text]
    if risky:
        problems.append("Moguća zdravstvena tvrdnja / obećanje bez izvora: " + ", ".join(risky))

    unsourced = []
    for where, txt in _post_texts(post):
        for n in sorted(_norm_numbers(txt) - corpus):
            unsourced.append(f"{n} ({where})")
    if unsourced:
        warnings.append("Brojke koje nisu pronađene u izvorima (provjeri jesu li činjenice ili samo "
                        "nabrajanje/datum): " + ", ".join(unsourced))

    for i, k in enumerate(post.get("kadrovi", []), 1):
        for f, lim in LIMITS.items():
            v = str(k.get(f) or "").replace("*", "")
            if len(v) > lim:
                warnings.append(f"kadar {i}: polje '{f}' ima {len(v)} znakova (preporuka ≤ {lim})")
        refs = [k.get("proizvod")] + [o.get("proizvod") for o in k.get("opcije") or []]
        for r in refs:
            if isinstance(r, dict) and r.get("id") not in product_ids:
                problems.append(f"kadar {i}: nepoznat proizvod '{r.get('id')}'")

    cap = post.get("opis", "")
    tags = post.get("hashtagovi", [])
    full = cap + "\n\n" + " ".join(tags)
    if len(full) > 2200:
        problems.append(f"opis s hashtagovima ima {len(full)} znakova (Instagram dopušta 2200)")
    if not 5 <= len(tags) <= 15:
        warnings.append(f"broj hashtagova je {len(tags)} (preporuka 5–10)")
    fmt = post.get("format")
    n = len(post.get("kadrovi", []))
    if fmt == "karusel" and not 2 <= n <= 20:
        problems.append(f"karusel mora imati 2–20 kadrova (ima {n})")
    if fmt == "slika" and n != 1:
        problems.append(f"format 'slika' mora imati 1 kadar (ima {n})")

    for r in render_report or []:
        for pr in r.get("problemi", []):
            problems.append(f"kadar {r['kadar']}: {pr}")
        if r.get("smanjen_naslov_posto"):
            warnings.append(f"kadar {r['kadar']}: naslov automatski smanjen na {r['smanjen_naslov_posto'][0]} %")

    return {"greske": problems, "upozorenja": warnings, "prolazi": not problems}
