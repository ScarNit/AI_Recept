"""Faza 1 – prikupljanje provjerljivih podataka s webshopa.

Za svaki URL proizvoda iz brifa čita strukturirane podatke (schema.org JSON-LD:
naziv, opis, cijene po varijanti, ocjene, slike) i tekst opisa sa stranice, te
skida službene fotografije proizvoda i logotip. Sve što kasnije završi u objavi
kao činjenica mora se moći pronaći u ovdje spremljenim izvorima.

Instagram se NE scrapea (traži prijavu i to nije dopušteno uvjetima korištenja);
umjesto toga brif prima snimke zaslona profila koje korisnik priloži.
"""
from __future__ import annotations

import glob
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

UA = "Mozilla/5.0 (compatible; AI-recept/1.0; +demonstracija zadatka)"


def _get(url: str, **kw) -> requests.Response:
    for attempt in range(3):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=40, **kw)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(2 + 3 * attempt)
    raise RuntimeError(f"Ne mogu dohvatiti {url}")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def scrape_product(url: str) -> dict:
    html = _get(url).text
    soup = BeautifulSoup(html, "html.parser")
    product: dict = {"url": url, "dohvaceno": time.strftime("%Y-%m-%d %H:%M")}

    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except json.JSONDecodeError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for n in nodes:
            if isinstance(n, dict) and n.get("@type") == "Product":
                offers = n.get("offers", {})
                variants = offers.get("offers", [offers]) if isinstance(offers, dict) else offers
                product.update({
                    "naziv": _clean(n.get("name")),
                    "kategorija": _clean(n.get("category")),
                    "brend": (n.get("brand") or {}).get("name"),
                    "kratki_opis_jsonld": _clean(n.get("description")),
                    "slike": n.get("image", []),
                    "ocjena": (n.get("aggregateRating") or {}).get("ratingValue"),
                    "broj_recenzija": (n.get("aggregateRating") or {}).get("reviewCount"),
                    "varijante": [
                        {"naziv": _clean(v.get("name")), "cijena": v.get("price"),
                         "valuta": v.get("priceCurrency"),
                         "dostupno": "InStock" in str(v.get("availability"))}
                        for v in variants if isinstance(v, dict)
                    ],
                })

    def section(sel: str, limit: int) -> str:
        el = soup.select_one(sel)
        return _clean(el.get_text(" ", strip=True))[:limit] if el else ""

    product["kratki_opis"] = section("[data-test='pdp-product-description-short']", 1500).removesuffix(
        "Pročitaj više").strip()
    product["dugi_opis"] = section("[data-test='pdp-product-description-long']", 7000) or section(
        "#description", 7000)
    product["tablica"] = section("[data-test='pdp-product-description-table']", 3000)
    if not product.get("naziv"):
        product["naziv"] = section("[data-test='pdp-product-name']", 200)
    # sve fotografije iz kataloga koje se pojavljuju na stranici (galerija varijanti)
    found = re.findall(r"https://[^\"'&;\s]+/media/catalog/product/[^\"'&;\s]+\.(?:png|jpe?g|webp)", html)
    product["_galerija"] = list(dict.fromkeys(re.sub(r"/cache/[0-9a-f]{32}/", "/", u) for u in found))
    return product


def download(url: str, dest_dir: Path) -> Path | None:
    """Skida sliku; prvo pokušava original bez /cache/ (veća rezolucija)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    candidates = [re.sub(r"/cache/[0-9a-f]{32}/", "/", url), url]
    for u in dict.fromkeys(candidates):
        name = Path(urlparse(u).path).name
        out = dest_dir / name
        if out.exists():
            return out
        try:
            r = _get(u)
        except RuntimeError:
            continue
        out.write_bytes(r.content)
        try:
            Image.open(out).verify()
            return out
        except Exception:
            out.unlink(missing_ok=True)
    return None


def run(brief: dict, run_dir: Path) -> dict:
    assets = run_dir / "assets"
    sources: dict = {"proizvodi": [], "web": {}, "logo": None, "instagram_reference": []}

    site = brief.get("web_stranica")
    if site:
        html = _get(site).text
        soup = BeautifulSoup(html, "html.parser")
        sources["web"] = {
            "url": site,
            "naslov": _clean(soup.title.string if soup.title else ""),
            "meta_opis": (soup.find("meta", attrs={"name": "description"}) or {}).get("content", ""),
            "bannerima_istaknuto": sorted({Path(urlparse(i["src"]).path).name for i in soup.find_all("img", src=True)
                                           if "bannerslider" in i["src"]})[:20],
        }

    logo_url = brief.get("logo_url")
    if logo_url:
        r = _get(logo_url)
        p = assets / "logo" / Path(urlparse(logo_url).path).name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        sources["logo"] = str(p.relative_to(run_dir))

    for item in brief.get("proizvodi", []):
        url = item["url"] if isinstance(item, dict) else item
        print(f"  · {url}")
        prod = scrape_product(url)
        prod["id"] = (item.get("id") if isinstance(item, dict) else None) or Path(urlparse(url).path).stem
        prod["napomena_korisnika"] = item.get("napomena", "") if isinstance(item, dict) else ""
        # Odabir fotografija: JSON-LD slike + (opcionalno) slike iz galerije čiji naziv
        # odgovara uzorku iz brifa. Uzorak je ljudska odluka zapisana u brifu, npr. kad su
        # glavne slike promotivni banneri umjesto čistih packshota.
        chosen = [] if (isinstance(item, dict) and item.get("preskoci_glavne_slike")) else list(prod.get("slike", []))
        pattern = item.get("slike_uzorak") if isinstance(item, dict) else None
        if pattern:
            chosen += [u for u in prod["_galerija"] if re.search(pattern, Path(urlparse(u).path).name)]
        prod.pop("_galerija", None)
        chosen = list(dict.fromkeys(chosen))
        local = []
        for img_url in chosen[: (item.get("max_slika") if isinstance(item, dict) else None)
                              or brief.get("max_slika_po_proizvodu", 4)]:
            p = download(img_url, assets / "proizvodi" / prod["id"])
            if p:
                w, h = Image.open(p).size
                local.append({"datoteka": str(p.relative_to(run_dir)), "izvor": img_url, "dimenzije": [w, h]})
        prod["lokalne_slike"] = local
        sources["proizvodi"].append(prod)

    # snimke Instagram profila / objava koje je priložio korisnik
    for ref in brief.get("instagram_reference", []):
        matches = sorted(glob.glob(ref)) if any(c in ref for c in "*?[") else [ref]
        for m in matches:
            if Path(m).is_file():
                sources["instagram_reference"].append(m)
    if not sources["instagram_reference"]:
        print("  ! nema priloženih snimki Instagrama – analiza feeda bit će označena kao pretpostavka")

    sources["hash"] = hashlib.sha1(json.dumps(sources, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]
    return sources
