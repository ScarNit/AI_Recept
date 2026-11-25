"""Opcionalni korak – AI pozadinske scene za odabrane kadrove.

Ulaz: ``<run>/ai_scene.yaml`` – popis {objava, kadar, format, prompt}. Ako ne postoji,
stvara se iz polja ``ai_scena_prompt`` iz faze izrade (za prvi kadar svake objave), a
čovjek ga može doraditi. Svakom promptu dodaju se pravila brenda (bez teksta, logotipa i
ambalaže – proizvod uvijek dolazi iz originalne fotografije).

Izlaz: ``<run>/ai_slike/objava{N}_kadar{M}.png``; render ih koristi kao pozadinu kadra.

Generatori: ``rucno`` (PROMPTOVI.md za ChatGPT/Gemini aplikaciju – preporučeno) i
``pollinations`` (automatski, bez ključa, ali niža rezolucija i vodeni žig – samo za test).
Hugging Face je isproban 25. 11. 2026. i odbačen: besplatni modeli za slike su ukinuti
(HTTP 410), a preostali traže kupljene kredite (HTTP 402).
"""
from __future__ import annotations

import io
import json
import os
import time
import urllib.parse
from pathlib import Path

import requests
import yaml
from PIL import Image

RULES = ("No text, no letters, no numbers, no logos, no watermarks, no product packaging. "
         "Keep the lower half of the frame dark and simple: a product card and text will be placed there.")
SIZES = {"karusel": (1080, 1350), "slika": (1080, 1350), "story": (1080, 1920)}


def spec(run_dir: Path) -> list[dict]:
    f = run_dir / "ai_scene.yaml"
    if f.exists():
        return yaml.safe_load(f.read_text(encoding="utf-8")) or []
    content = json.loads((run_dir / "05_sadrzaj.json").read_text(encoding="utf-8"))
    items = [{"objava": p["broj"], "kadar": 1, "format": p.get("format", "karusel"), "prompt": p["ai_scena_prompt"]}
             for p in content["objave"] if p.get("ai_scena_prompt")]
    f.write_text("# AI pozadinske scene – uredi prompt po želji, zatim: python -m recept scene\n"
                 + yaml.safe_dump(items, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return items


def full_prompt(item: dict) -> str:
    ratio = "vertical 9:16" if item.get("format") == "story" else "vertical 4:5"
    return f"{item['prompt'].strip()} {RULES} Format: {ratio}."


def _save(img_bytes: bytes, out: Path, size: tuple[int, int]):
    im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    # izreži na točan omjer kadra (cover), bez rastezanja
    W, H = size
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - W) // 2, (im.height - H) // 2
    im.crop((left, top, left + W, top + H)).save(out, optimize=True)


def pollinations(prompt: str, size, seed: int = 7) -> bytes:
    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
           f"?width={size[0]}&height={size[1]}&seed={seed}&nologo=true")
    r = requests.get(url, timeout=300)
    if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
        raise RuntimeError(f"Pollinations HTTP {r.status_code}")
    return r.content


def run(run_dir: Path, cfg: dict, generator: str | None = None, overwrite: bool = False):
    gen = generator or cfg.get("generator", "rucno")
    out_dir = run_dir / "ai_slike"
    out_dir.mkdir(parents=True, exist_ok=True)
    items = spec(run_dir)
    if gen == "rucno":
        lines = ["# Promptovi za AI pozadinske scene", "",
                 "Svaki prompt zalijepi u ChatGPT ili Gemini (novi chat), preuzmi sliku i spremi je pod",
                 "navedenim imenom u ovu mapu. Zatim: `python -m recept pokreni --run <run> --od render`.", ""]
        for it in items:
            lines += [f"## objava{it['objava']}_kadar{it['kadar']}.png ({it.get('format')})", "", "```",
                      full_prompt(it), "```", ""]
        (out_dir / "PROMPTOVI.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"  → {out_dir / 'PROMPTOVI.md'}")
        return
    for it in items:
        out = out_dir / f"objava{it['objava']}_kadar{it['kadar']}.png"
        if out.exists() and not overwrite:
            print(f"  · {out.name} već postoji – preskačem (--prepisi za novu)")
            continue
        size = SIZES.get(it.get("format"), SIZES["karusel"])
        t0 = time.time()
        data = pollinations(full_prompt(it), size)
        _save(data, out, size)
        print(f"  · {out.name} ({gen}, {time.time() - t0:.0f} s)")
