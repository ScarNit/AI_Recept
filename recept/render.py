"""Faza 5 – render: JSON sadržaj objave → gotove PNG slike (1080×1350 ili 1080×1920).

Grafika se slaže iz HTML predloška (boje i logo brenda) i NEPROMIJENJENIH službenih
fotografija proizvoda. Ako u mapi ``<run>/ai_slike/`` postoji AI scena za kadar
(``objava2_kadar1.png``), koristi se kao pozadina tog kadra.

Nakon rendera skripta u pregledniku mjeri tekst: preveliki naslov se smanjuje (do 70 %),
a sve što i dalje ne stane prijavljuje se u izvještaj za fazu provjere.
"""
from __future__ import annotations

import html
import os
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
SIZES = {"karusel": (1080, 1350), "slika": (1080, 1350), "story": (1080, 1920)}

FIT_JS = """
() => {
  const box = document.querySelector('[data-fit-box]');
  const kadar = document.querySelector('.kadar');
  const shrunk = [];
  for (const el of document.querySelectorAll('h1[data-fit]')) {
    const start = parseFloat(getComputedStyle(el).fontSize);
    let size = start;
    while (box.scrollHeight > box.clientHeight + 1 && size > start * 0.7) {
      size *= 0.96; el.style.fontSize = size + 'px';
    }
    if (size < start) shrunk.push(Math.round(100 * size / start));
  }
  const problems = [];
  if (box.scrollHeight > box.clientHeight + 2)
    problems.push(`sadržaj je viši od prostora za ${box.scrollHeight - box.clientHeight}px`);
  const kr = kadar.getBoundingClientRect();
  for (const el of box.querySelectorAll('h1, p, .stavka, .chip, .gumb, .op-naziv, .broj, .broj-opis, .nadnaslov')) {
    const r = el.getBoundingClientRect();
    if (r.right > kr.right - 40 || r.bottom > kr.bottom - 20)
      problems.push(`element .${el.className || el.tagName} izlazi izvan sigurne zone`);
    if (el.scrollWidth > el.clientWidth + 2)
      problems.push(`predugačka riječ u .${el.className || el.tagName}`);
  }
  return {shrunk, problems};
}
"""


def trim_white(src: Path, dest_dir: Path, margin: float = 0.04) -> Path:
    """Obreže samo prazni bijeli rub oko fotografije – proizvod ostaje nepromijenjen."""
    from PIL import Image, ImageChops
    dest = dest_dir / (src.stem + ".png")
    if dest.exists():
        return dest
    dest_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGBA")
    flat = Image.new("RGBA", im.size, (255, 255, 255, 255))
    flat.alpha_composite(im)
    diff = ImageChops.difference(flat.convert("RGB"), Image.new("RGB", im.size, (255, 255, 255)))
    bbox = diff.convert("L").point(lambda v: 255 if v > 10 else 0).getbbox()
    if bbox:
        m = int(max(im.size) * margin)
        bbox = (max(0, bbox[0] - m), max(0, bbox[1] - m), min(im.width, bbox[2] + m), min(im.height, bbox[3] + m))
        flat = flat.crop(bbox)
    flat.convert("RGB").save(dest, optimize=True)
    return dest


def _highlight(text: str | None) -> Markup:
    esc = html.escape(text or "")
    return Markup(re.sub(r"\*(.+?)\*", r'<span class="hl">\1</span>', esc))


def _env() -> Environment:
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    env.filters["highlight"] = _highlight
    return env


def _launch(p):
    exe = os.environ.get("CHROMIUM_PATH")
    if exe:
        return p.chromium.launch(executable_path=exe)
    try:
        return p.chromium.launch()
    except Exception:
        if Path("/opt/pw-browsers/chromium").exists():
            return p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        raise


def render_posts(posts: list[dict], sources: dict, brand_cfg: dict, run_dir: Path, out_dir: Path,
                 only: set[int] | None = None) -> dict:
    from playwright.sync_api import sync_playwright

    images = {p["id"]: p.get("lokalne_slike", []) for p in sources["proizvodi"]}

    def img(ref):
        if not isinstance(ref, dict) or ref.get("id") not in images:
            return None
        lst = images[ref["id"]]
        if not lst:
            return None
        i = ref.get("slika", 0)
        i = i if isinstance(i, int) and 0 <= i < len(lst) else 0
        trimmed = trim_white(run_dir / lst[i]["datoteka"], run_dir / "assets" / "obrezano")
        return {"src": trimmed.resolve().as_uri(), "datoteka": lst[i]["datoteka"]}

    logo_svg = (run_dir / sources["logo"]).read_text(encoding="utf-8") if sources.get("logo") else ""
    logo_svg = re.sub(r'<svg width="\d+" height="\d+"', "<svg", logo_svg, count=1)
    tpl = _env().get_template("kadar.html.j2")
    html_dir = run_dir / "render_html"
    html_dir.mkdir(parents=True, exist_ok=True)
    report: dict = {}

    with sync_playwright() as p:
        browser = _launch(p)
        for post in posts:
            n = post["broj"]
            if only and n not in only:
                continue
            fmt = post.get("format", "karusel")
            W, H = SIZES.get(fmt, SIZES["karusel"])
            page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
            pdir = out_dir / f"objava_{n}"
            pdir.mkdir(parents=True, exist_ok=True)
            for old in pdir.glob("kadar_*.png"):
                old.unlink()
            slides = post["kadrovi"]
            report[n] = []
            for i, k in enumerate(slides):
                k = dict(k)
                k["proizvod_img"] = img(k.get("proizvod"))
                for o in k.get("opcije") or []:
                    o["proizvod_img"] = img(o.get("proizvod"))
                for ext in ("png", "jpg", "jpeg", "webp"):
                    ai = run_dir / "ai_slike" / f"objava{n}_kadar{i + 1}.{ext}"
                    if ai.exists():
                        k["ai_pozadina_src"] = ai.resolve().as_uri()
                        k["tema"] = "tamna"
                        break
                if k.get("tema") not in ("tamna", "svijetla", "narancasta"):
                    k["tema"] = "tamna"
                page_html = tpl.render(
                    k=k, indeks=i, ukupno=len(slides), format=fmt, story=fmt == "story", W=W, H=H,
                    logo_svg=Markup(logo_svg), web=brand_cfg.get("web_oznaka", ""),
                    boje=brand_cfg["boje"], fonts=(ROOT / "fonts").resolve().as_uri())
                hf = html_dir / f"objava{n}_kadar{i + 1}.html"
                hf.write_text(page_html, encoding="utf-8")
                page.goto(hf.resolve().as_uri())
                page.wait_for_load_state("networkidle")
                page.evaluate("document.fonts.ready")
                fit = page.evaluate(FIT_JS)
                out = pdir / f"kadar_{i + 1:02d}.png"
                page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": W, "height": H})
                report[n].append({"kadar": i + 1, "datoteka": str(out), "smanjen_naslov_posto": fit["shrunk"],
                                  "problemi": fit["problems"],
                                  "fotografije": [x["datoteka"] for x in [k.get("proizvod_img")] +
                                                  [o.get("proizvod_img") for o in k.get("opcije") or []] if x]})
                print(f"    objava {n} · kadar {i + 1}/{len(slides)}"
                      + (f"  ! {'; '.join(fit['problems'])}" if fit["problems"] else ""))
            page.close()
        browser.close()
    return report
