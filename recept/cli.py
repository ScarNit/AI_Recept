"""AI recept: od Instagram brenda do tri gotove objave.

Faze (svaka sprema rezultat u <run>/ i može se ponoviti ili nastaviti):
  0 brif          – ulazi korisnika (YAML ili interaktivni brifing)       → 00_brif.json
  1 istrazivanje  – webshop: činjenice, cijene, fotografije, logo          → 01_izvori.json
  2 opis_slika    – AI opisuje službene fotografije (vision)              → 02_opis_slika.json
  3 analiza       – AI analiza brenda, provjereno vs. pretpostavke         → 03_analiza.json/.md
  4 plan          – AI plan triju objava (cilj, format, koncept)           → 04_plan.json/.md
  5 izrada        – AI tekstovi kadrova + opis objave (JSON)               → 05_sadrzaj.json
  6 render        – HTML predložak + službene fotografije → PNG            → 06_render.json
  7 provjera      – automatske provjere + AI kritika + popravak            → 07_provjera.json/.md
  8 isporuka      – gotove objave, opisi i pregled                         → isporuka/
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import shutil
import sys
import time
from pathlib import Path

import yaml

from . import provjera as checks
from . import render as rnd
from . import scrape
from .llm import LLM, ManualStepRequired

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
PHASES = ["brif", "istrazivanje", "opis_slika", "analiza", "plan", "izrada", "render", "provjera", "isporuka"]
OUTPUT = {"brif": "00_brif.json", "istrazivanje": "01_izvori.json", "opis_slika": "02_opis_slika.json",
          "analiza": "03_analiza.json", "plan": "04_plan.json", "izrada": "05_sadrzaj.json",
          "render": "06_render.json", "provjera": "07_provjera.json", "isporuka": "isporuka/README.md"}


# ---------------------------------------------------------------- pomoćno
def jdump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def jload(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def prompt(name: str, **kw) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8").format(**kw)


def compact_sources(sources: dict, ids: list[str] | None = None, long: bool = True) -> str:
    out = []
    for p in sources["proizvodi"]:
        if ids and p["id"] not in ids:
            continue
        d = {k: p.get(k) for k in ("id", "url", "naziv", "kategorija", "ocjena", "broj_recenzija",
                                   "kratki_opis", "napomena_korisnika")}
        d["varijante_i_cijene_EUR"] = [f"{v['naziv']}: {v['cijena']}" for v in p.get("varijante", [])][:12]
        d["cijene_dohvacene"] = p.get("dohvaceno")
        if long:
            d["dugi_opis"] = p.get("dugi_opis", "")[:4000]
            d["tablica"] = p.get("tablica", "")[:1500]
        out.append(d)
    return json.dumps({"web": sources.get("web"), "proizvodi": out}, ensure_ascii=False, indent=1)


class Run:
    def __init__(self, args):
        self.args = args
        self.dir = Path(args.run)
        self.dir.mkdir(parents=True, exist_ok=True)
        cfg_path = Path(args.config) if args.config else (ROOT / "config.yaml")
        if not cfg_path.exists():
            cfg_path = ROOT / "config.example.yaml"
        self.cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        print(f"Konfiguracija: {cfg_path.name} · provider: {self.cfg.get('llm', {}).get('provider')}")
        self._llm = None
        self.state_path = self.dir / "stanje.json"
        self.state = jload(self.state_path) if self.state_path.exists() else {}

    @property
    def llm(self) -> LLM:
        if self._llm is None:
            self._llm = LLM(self.cfg.get("llm", {}), self.dir)
        return self._llm

    @property
    def system(self) -> str:
        return (PROMPTS / "sustav.md").read_text(encoding="utf-8")

    def path(self, phase):
        return self.dir / OUTPUT[phase]

    def load(self, phase):
        return jload(self.path(phase))

    def done(self, phase, t0):
        self.state[phase] = {"zavrseno": time.strftime("%Y-%m-%d %H:%M:%S"), "sekundi": round(time.time() - t0, 1),
                             "izlaz": OUTPUT[phase]}
        jdump(self.state, self.state_path)

    # ------------------------------------------------------------ faze
    def brif(self):
        b = yaml.safe_load(Path(self.args.brif).read_text(encoding="utf-8"))
        jdump(b, self.path("brif"))

    def istrazivanje(self):
        jdump(scrape.run(self.load("brif"), self.dir), self.path("istrazivanje"))

    def opis_slika(self):
        sources = self.load("istrazivanje")
        prev = jload(self.path("opis_slika")) if self.path("opis_slika").exists() else {}
        out = {}
        for p in sources["proizvodi"]:
            imgs = [self.dir / i["datoteka"] for i in p.get("lokalne_slike", [])]
            if not imgs:
                continue
            if p["id"] in prev and len(prev[p["id"]]) == len(imgs):
                out[p["id"]] = prev[p["id"]]
                continue
            print(f"  · {p['id']}")
            popis = "\n".join(f"{i}: {Path(x).name}" for i, x in enumerate(imgs))
            res = self.llm.chat_json(self.system, prompt("01_opis_slika.md", naziv=p["naziv"], popis=popis),
                                     step=f"opis_slika_{p['id']}", images=imgs)
            out[p["id"]] = res.get("slike", [])
            jdump(out, self.path("opis_slika"))  # spremi nakon svakog proizvoda (nastavak)
        jdump(out, self.path("opis_slika"))

    def analiza(self):
        brief, sources = self.load("brif"), self.load("istrazivanje")
        ig = [Path(x) for x in sources.get("instagram_reference", [])][:10]
        res = self.llm.chat_json(self.system, prompt(
            "02_analiza.md", brif=json.dumps(brief, ensure_ascii=False, indent=1),
            izvori=compact_sources(sources), broj_ig=len(ig), datum=brief.get("datum_objave", "")),
            step="analiza", images=ig or None)
        jdump(res, self.path("analiza"))
        (self.dir / "03_analiza.md").write_text(analysis_md(res, brief, sources), encoding="utf-8")

    def plan(self):
        brief, sources, analysis = self.load("brif"), self.load("istrazivanje"), self.load("analiza")
        products = "\n".join(f"- {p['id']}: {p['naziv']} — {p.get('kratki_opis', '')[:300]}"
                             for p in sources["proizvodi"])
        res = self.llm.chat_json(self.system, prompt(
            "03_plan.md", brif=json.dumps(brief, ensure_ascii=False, indent=1),
            analiza=json.dumps(analysis, ensure_ascii=False, indent=1), proizvodi=products,
            datum=brief.get("datum_objave", "")), step="plan")
        jdump(res, self.path("plan"))
        (self.dir / "04_plan.md").write_text(plan_md(res), encoding="utf-8")

    def izrada(self, feedback: dict | None = None):
        brief, sources, analysis = self.load("brif"), self.load("istrazivanje"), self.load("analiza")
        plan = self.load("plan")
        descr = jload(self.path("opis_slika")) if self.path("opis_slika").exists() else {}
        existing = {p["broj"]: p for p in jload(self.path("izrada"))["objave"]} if self.path("izrada").exists() else {}
        only = self.only
        for obj in plan["objave"]:
            n = obj["broj"]
            if only and n not in only and n in existing:
                continue
            ids = obj.get("proizvodi", [])
            slike = []
            for pid in ids:
                prod = next((p for p in sources["proizvodi"] if p["id"] == pid), None)
                if not prod:
                    continue
                d = {x.get("indeks"): x for x in descr.get(pid, [])}
                for i, im in enumerate(prod.get("lokalne_slike", [])):
                    opis = d.get(i, {}).get("opis") or Path(im["datoteka"]).name
                    slike.append(f"- {pid} → {i} → {opis}")
            fb = ""
            if feedback and n in feedback:
                fb = ("\n\nPOVRATNA INFORMACIJA IZ PROVJERE PRETHODNE VERZIJE (obavezno uvaži):\n" +
                      json.dumps(feedback[n], ensure_ascii=False, indent=1))
            print(f"  · objava {n}: {obj.get('naziv', '')}")
            res = self.llm.chat_json(self.system, prompt(
                "04_izrada.md", broj=n, format=obj.get("format", "karusel"),
                plan_objave=json.dumps(obj, ensure_ascii=False, indent=1),
                analiza=json.dumps({k: analysis.get(k) for k in ("sazetak", "ton_glasa", "vizualni_stil", "publika")},
                                   ensure_ascii=False, indent=1),
                izvori=compact_sources(sources, ids), slike="\n".join(slike) or "(nema)",
                datum_cijena=f"cijena na gymbeam.hr, {time.strftime('%d.%m.%Y.')}",
                povratna_informacija=fb), step=f"izrada_objava{n}")
            res["broj"], res["format"] = n, obj.get("format", res.get("format", "karusel"))
            existing[n] = res
            jdump({"objave": [existing[k] for k in sorted(existing)]}, self.path("izrada"))

    def render(self):
        brief, sources = self.load("brif"), self.load("istrazivanje")
        posts = self.load("izrada")["objave"]
        brand = {"boje": brief.get("boje") or {"narancasta": "#FF4410", "crna": "#111111", "svijetla": "#F3F1EE"},
                 "web_oznaka": brief.get("web_oznaka") or brief.get("web_stranica", "").replace("https://", "")}
        prev = {int(k): v for k, v in jload(self.path("render")).items()} if self.path("render").exists() else {}
        rep = rnd.render_posts(posts, sources, brand, self.dir, self.dir / "isporuka", only=self.only)
        prev.update({int(k): v for k, v in rep.items()})
        jdump({str(k): prev[k] for k in sorted(prev)}, self.path("render"))

    def provjera(self):
        brief, sources = self.load("brif"), self.load("istrazivanje")
        plan = {o["broj"]: o for o in self.load("plan")["objave"]}
        corpus = checks.corpus_numbers(sources, brief)
        src_text = checks.corpus_text(sources)
        ids = {p["id"] for p in sources["proizvodi"]}
        result = jload(self.path("provjera")) if self.path("provjera").exists() else {}
        auto_fix = self.cfg.get("provjera", {}).get("automatski_popravak", True)

        for post in self.load("izrada")["objave"]:
            n = post["broj"]
            if self.only and n not in self.only:
                continue
            render_rep = {int(k): v for k, v in self.load("render").items()}.get(n, [])
            auto = checks.check_post(post, corpus, render_rep, ids, src_text)
            critic = self._critic(post, plan.get(n, {}), auto, sources, render_rep)
            entry = {"automatske": auto, "ai_kritika": critic, "popravljeno": []}

            if auto_fix and (critic.get("ispravci") or critic.get("ispravci_opisa") or auto["greske"]):
                fixed, applied = apply_fixes(post, critic)
                fixed_auto = checks.check_post(fixed, corpus, None, ids, src_text)
                new_unsourced = [w for w in fixed_auto["upozorenja"] if w.startswith("Brojke")]
                old_unsourced = [w for w in auto["upozorenja"] if w.startswith("Brojke")]
                if applied and (len(" ".join(new_unsourced)) <= len(" ".join(old_unsourced))):
                    print(f"  · objava {n}: primjenjujem {len(applied)} ispravaka i ponovno renderiram")
                    self._replace_post(fixed)
                    saved = self.only
                    self.only = {n}
                    self.render()
                    self.only = saved
                    render_rep = {int(k): v for k, v in self.load("render").items()}.get(n, [])
                    entry["automatske_nakon_popravka"] = checks.check_post(fixed, corpus, render_rep, ids, src_text)
                    entry["ai_kritika_nakon_popravka"] = self._critic(fixed, plan.get(n, {}),
                                                                      entry["automatske_nakon_popravka"],
                                                                      sources, render_rep, suffix="_2")
                    entry["popravljeno"] = applied
                elif applied:
                    entry["popravak_odbijen"] = "ispravci bi uveli brojke bez izvora"
            result[str(n)] = entry
            jdump(result, self.path("provjera"))
        (self.dir / "07_provjera.md").write_text(check_md(result), encoding="utf-8")

    def _critic(self, post, plan_obj, auto, sources, render_rep, suffix=""):
        imgs = [Path(r["datoteka"]) for r in render_rep][:10]
        return self.llm.chat_json(self.system, prompt(
            "05_provjera.md", broj=post["broj"], plan_objave=json.dumps(plan_obj, ensure_ascii=False, indent=1),
            sadrzaj=json.dumps(post, ensure_ascii=False, indent=1), automatske=json.dumps(auto, ensure_ascii=False),
            izvori=compact_sources(sources, plan_obj.get("proizvodi"), long=True)),
            step=f"provjera_objava{post['broj']}{suffix}", images=imgs)

    def _replace_post(self, new_post):
        data = self.load("izrada")
        data["objave"] = [new_post if p["broj"] == new_post["broj"] else p for p in data["objave"]]
        jdump(data, self.path("izrada"))

    def isporuka(self):
        brief, plan = self.load("brif"), {o["broj"]: o for o in self.load("plan")["objave"]}
        posts, render_rep = self.load("izrada")["objave"], self.load("render")
        checks_res = jload(self.path("provjera")) if self.path("provjera").exists() else {}
        out = self.dir / "isporuka"
        lines = [f"# {brief['brend']} – tri gotove objave", "",
                 f"Instagram: {brief.get('instagram')} · web: {brief.get('web_stranica')}", ""]
        from PIL import Image
        for post in posts:
            n, po = post["broj"], plan.get(post["broj"], {})
            pdir = out / f"objava_{n}"
            caption = post.get("opis", "").strip() + "\n\n" + " ".join(post.get("hashtagovi", []))
            (pdir / "opis.txt").write_text(caption + "\n", encoding="utf-8")
            files = sorted(pdir.glob("kadar_*.png"))
            # pregledna traka svih kadrova
            if files:
                ims = [Image.open(f) for f in files]
                h = 540
                ws = [int(i.width * h / i.height) for i in ims]
                strip = Image.new("RGB", (sum(ws) + 12 * (len(ims) - 1), h), "white")
                x = 0
                for im, w in zip(ims, ws):
                    strip.paste(im.resize((w, h)), (x, 0))
                    x += w + 12
                strip.save(pdir / "pregled.jpg", quality=88)
            final = checks_res.get(str(n), {})
            crit = final.get("ai_kritika_nakon_popravka") or final.get("ai_kritika") or {}
            lines += [f"## Objava {n} – {po.get('naziv', '')}", "",
                      f"- **Format:** {post.get('format')} ({len(files)} kadr.)",
                      f"- **Cilj:** {po.get('cilj', '')} (mjera: {po.get('mjera_uspjeha', '')})",
                      f"- **Koncept:** {po.get('koncept', '')}",
                      f"- **Zašto odgovara brendu:** {po.get('obrazlozenje', '')}",
                      f"- **AI ocjene provjere:** {json.dumps(crit.get('ocjene', {}), ensure_ascii=False)}", "",
                      f"![pregled](objava_{n}/pregled.jpg)", "",
                      "**Kadrovi:** " + ", ".join(f"[{f.name}](objava_{n}/{f.name})" for f in files), "",
                      "**Opis objave (caption):**", "", "```", caption, "```", "",
                      "**Alt tekstovi:**", ""]
            lines += [f"{i}. {k.get('alt_tekst', '')}" + (f" — naljepnica: {k['story_naljepnica']}"
                                                          if k.get("story_naljepnica") else "")
                      for i, k in enumerate(post.get("kadrovi", []), 1)]
            lines += ["", "**Korištene činjenice i izvori:**", ""]
            lines += [f"- {c.get('cinjenica')} — {c.get('izvor')}" for c in post.get("koristene_cinjenice", [])]
            if post.get("ai_scena_prompt"):
                lines += ["", f"**Opcionalni prompt za AI scenu (ChatGPT/Gemini, ručno):** {post['ai_scena_prompt']}"]
            lines.append("")
        (out / "README.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"  → {out / 'README.md'}")

    # ------------------------------------------------------------ pokretanje
    def run(self):
        start = PHASES.index(self.args.od) if self.args.od else 0
        stop = PHASES.index(self.args.do) if self.args.do else len(PHASES) - 1
        self.only = {int(x) for x in self.args.objave.split(",")} if self.args.objave else None
        for i, phase in enumerate(PHASES):
            if i > stop:
                break
            if i < start and self.path(phase).exists():
                continue
            if self.args.od is None and self.path(phase).exists() and phase in self.state:
                print(f"[{i}] {phase}: već gotovo ({self.state[phase]['zavrseno']}) – preskačem")
                continue
            if phase == "brif" and not self.args.brif:
                if self.path("brif").exists():
                    continue
                sys.exit("Za prvo pokretanje navedi --brif brief/<datoteka>.yaml")
            print(f"[{i}] {phase} …")
            t0 = time.time()
            try:
                getattr(self, phase)()
            except ManualStepRequired as e:
                print("\n" + str(e))
                sys.exit(2)
            self.done(phase, t0)
        print("Gotovo.")


# ------------------------------------------------------------ ispravci
EDITABLE = {"nadnaslov", "naslov", "podnaslov", "tekst", "gumb", "oznaka", "alt_tekst"}


def apply_fixes(post: dict, critic: dict):
    fixed, applied = copy.deepcopy(post), []
    for f in critic.get("ispravci") or []:
        try:
            i, field, val = int(f.get("kadar")), f.get("polje"), f.get("nova_vrijednost")
        except (TypeError, ValueError):
            continue
        if not (0 <= i < len(fixed["kadrovi"])) or not isinstance(val, str):
            continue
        k = fixed["kadrovi"][i]
        if field in EDITABLE:
            applied.append({"kadar": i, "polje": field, "staro": k.get(field), "novo": val, "razlog": f.get("razlog")})
            k[field] = val
        elif field and field.startswith("brojka.") and isinstance(k.get("brojka"), dict):
            sub = field.split(".", 1)[1]
            applied.append({"kadar": i, "polje": field, "staro": k["brojka"].get(sub), "novo": val,
                            "razlog": f.get("razlog")})
            k["brojka"][sub] = val
    cap = critic.get("ispravci_opisa")
    if isinstance(cap, str) and len(cap) > 200:
        applied.append({"polje": "opis", "staro": fixed.get("opis", "")[:120] + "…", "novo": cap[:120] + "…"})
        fixed["opis"] = cap
    return fixed, applied


# ------------------------------------------------------------ markdown izvještaji
def analysis_md(a: dict, brief: dict, sources: dict) -> str:
    L = [f"# Analiza brenda – {brief.get('brend')}", "", a.get("sazetak", ""), "",
         "## Publika", *[f"- {x}" for x in a.get("publika", [])], "",
         "## Ton glasa", a.get("ton_glasa", {}).get("opis", ""), "",
         "Primjeri: " + " / ".join(a.get("ton_glasa", {}).get("primjeri_fraza", [])), "",
         "Izbjegavati: " + "; ".join(a.get("ton_glasa", {}).get("izbjegavati", [])), "",
         "## Teme", *[f"- {x}" for x in a.get("teme", [])], "", "## Vizualni stil"]
    for k, v in (a.get("vizualni_stil") or {}).items():
        L.append(f"- **{k}:** " + ("; ".join(v) if isinstance(v, list) else str(v)))
    L += ["", "## Provjereni podaci (s izvorom)"]
    L += [f"- {x.get('tvrdnja')} — <{x.get('izvor')}>" for x in a.get("provjereni_podaci", [])]
    L += ["", "## Pretpostavke (nije provjereno)"]
    L += [f"- {x.get('tvrdnja')} — *{x.get('zasto')}*" for x in a.get("pretpostavke", [])]
    L += ["", "## Nedostupni izvori", *[f"- {x}" for x in a.get("nedostupni_izvori", [])], "",
          "## Prilike", *[f"- {x}" for x in a.get("prilike", [])], "",
          "## Rizici", *[f"- {x}" for x in a.get("rizici", [])], "",
          "## Korišteni izvori (automatski dohvaćeno)"]
    L += [f"- <{p['url']}> (dohvaćeno {p.get('dohvaceno')})" for p in sources.get("proizvodi", [])]
    L += [f"- Snimka Instagrama: {x}" for x in sources.get("instagram_reference", [])]
    return "\n".join(L) + "\n"


def plan_md(p: dict) -> str:
    L = ["# Plan triju objava", ""]
    for o in p.get("objave", []):
        L += [f"## Objava {o.get('broj')} – {o.get('naziv', '')}", "",
              f"- **Cilj:** {o.get('cilj')} (mjera: {o.get('mjera_uspjeha')})",
              f"- **Format:** {o.get('format')}, {o.get('broj_kadrova')} kadr.",
              f"- **Koncept:** {o.get('koncept')}",
              f"- **Proizvodi:** {', '.join(o.get('proizvodi', []))}",
              f"- **Obrazloženje:** {o.get('obrazlozenje')}",
              "- **Ključne činjenice:**", *[f"  - {c.get('cinjenica')} — {c.get('izvor')}"
                                             for c in o.get("kljucne_cinjenice", [])], ""]
    return "\n".join(L)


def check_md(res: dict) -> str:
    L = ["# Provjera objava", ""]
    for n, e in sorted(res.items()):
        L += [f"## Objava {n}", ""]
        for key, title in (("automatske", "Automatske provjere (prije popravka)"),
                           ("automatske_nakon_popravka", "Automatske provjere (nakon popravka)")):
            if key in e:
                L += [f"**{title}:** {'prolazi' if e[key]['prolazi'] else 'NE PROLAZI'}"]
                L += [f"- greška: {x}" for x in e[key]["greske"]] + [f"- upozorenje: {x}" for x in e[key]["upozorenja"]]
                L.append("")
        for key, title in (("ai_kritika", "AI kritika"), ("ai_kritika_nakon_popravka", "AI kritika nakon popravka")):
            c = e.get(key)
            if c:
                L += [f"**{title}:** ocjene {json.dumps(c.get('ocjene', {}), ensure_ascii=False)}, "
                      f"odobreno: {c.get('odobreno')}"]
                L += [f"- {k}: {v}" for k, v in (c.get("komentari") or {}).items()]
                L.append("")
        if e.get("popravljeno"):
            L += ["**Primijenjeni ispravci:**"] + [f"- kadar {x.get('kadar', '-')}, {x['polje']}: "
                                                    f"„{x.get('staro')}” → „{x.get('novo')}” ({x.get('razlog', '')})"
                                                    for x in e["popravljeno"]] + [""]
        if e.get("popravak_odbijen"):
            L += [f"**Popravak odbijen:** {e['popravak_odbijen']}", ""]
    return "\n".join(L)


# ------------------------------------------------------------ ljudske dorade
def apply_human_edits(run_dir: Path, edits_file: Path):
    """Primijeni ručne dorade iz YAML datoteke na 05_sadrzaj.json i zapiši ih u ljudske_dorade.md.

    Format stavke: {objava: 1, kadar: 5 | null, polje: naslov | opis | hashtagovi | brojka.opis,
                    novo: "...", razlog: "..."}   (kadar je 1-based, kao na slikama)
    """
    content_path = run_dir / OUTPUT["izrada"]
    data = jload(content_path)
    posts = {p["broj"]: p for p in data["objave"]}
    edits = yaml.safe_load(edits_file.read_text(encoding="utf-8")) or []
    log = [""]
    for e in edits:
        post = posts[int(e["objava"])]
        field = e["polje"]
        target = post if not e.get("kadar") else post["kadrovi"][int(e["kadar"]) - 1]
        if "." in field:
            parent, sub = field.split(".", 1)
            target, field = target[parent], sub
        old = target.get(field)
        target[field] = e["novo"]
        where = f"objava {e['objava']}" + (f", kadar {e['kadar']}" if e.get("kadar") else "")
        log += [f"- **{where}, {e['polje']}:** „{old}” → „{e['novo']}”", f"  - razlog: {e.get('razlog', '')}"]
    jdump(data, content_path)
    md = run_dir / "ljudske_dorade.md"
    head = md.read_text(encoding="utf-8") if md.exists() else "# Ljudske dorade AI prijedloga\n"
    md.write_text(head.rstrip() + f"\n\n## Dorade sadržaja iz `{edits_file.name}` ({time.strftime('%Y-%m-%d %H:%M')})\n"
                  + "\n".join(log) + "\n", encoding="utf-8")
    print(f"Primijenjeno {len(edits)} dorada. Pokreni: python -m recept pokreni --run {run_dir} --od render")


# ------------------------------------------------------------ interaktivni brif
QUESTIONS = [
    ("brend", "Naziv brenda", None),
    ("instagram", "Instagram profil (npr. @gymbeamhr)", None),
    ("web_stranica", "Točna web-stranica / webshop (URL)", None),
    ("logo_url", "URL logotipa (SVG/PNG) – prazno ako nemaš", ""),
    ("proizvodi", "URL-ovi proizvoda za promociju (odvoji zarezom)", "list"),
    ("publika", "Tko je publika?", None),
    ("ciljevi", "Ciljevi objava (odvoji zarezom), npr. edukacija, komentari, kupnja", "list"),
    ("ton_i_stil", "Ton i stil (kako brend govori?)", None),
    ("uzori_i_inspiracija", "Uzori i inspiracija", ""),
    ("datum_objave", "Kada se objavljuje (sezona/kontekst)?", ""),
    ("instagram_reference", "Putanje do snimki Instagram profila/objava (zarez, glob dopušten)", "list"),
]


def interactive_brief(out: Path):
    print("Interaktivni brifing – odgovori na pitanja (Enter za preskakanje opcionalnih).\n")
    data = {"jezik": "hrvatski", "max_slika_po_proizvodu": 4}
    for key, q, kind in QUESTIONS:
        ans = input(f"{q}: ").strip()
        if kind == "list":
            data[key] = [x.strip() for x in ans.split(",") if x.strip()]
        elif ans or kind is None:
            data[key] = ans
    data["proizvodi"] = [{"url": u} for u in data.get("proizvodi", [])]
    data["ogranicenja"] = ["Ne izmišljati svojstva, cijene ni izjave stvarnih osoba – sve činjenice samo iz izvora."]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"\nBrif spremljen u {out}. Pokreni: python -m recept pokreni --brif {out} --run runs/<naziv>")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="recept", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("brif", help="interaktivni brifing → YAML")
    b.add_argument("--izlaz", default="brief/moj_brend.yaml")
    r = sub.add_parser("pokreni", help="pokreni ili nastavi recept")
    r.add_argument("--brif", help="YAML brif (potreban pri prvom pokretanju)")
    r.add_argument("--run", default="runs/gymbeam_hr", help="mapa u koju se spremaju sve faze")
    r.add_argument("--config", help="config.yaml (zadano: config.yaml ili config.example.yaml)")
    r.add_argument("--od", choices=PHASES, help="ponovno pokreni od ove faze (nadalje)")
    r.add_argument("--do", choices=PHASES, help="stani nakon ove faze (npr. 'plan' za ljudsko odobrenje)")
    r.add_argument("--objave", help="samo ove objave, npr. 2 ili 1,3 (faze izrada/render/provjera)")
    d = sub.add_parser("dorada", help="primijeni ljudske dorade (YAML) na sadržaj objava")
    d.add_argument("--run", default="runs/gymbeam_hr")
    d.add_argument("--datoteka", required=True)
    s = sub.add_parser("stanje", help="prikaži stanje faza")
    s.add_argument("--run", default="runs/gymbeam_hr")
    args = ap.parse_args(argv)

    if args.cmd == "brif":
        interactive_brief(Path(args.izlaz))
    elif args.cmd == "pokreni":
        Run(args).run()
    elif args.cmd == "dorada":
        apply_human_edits(Path(args.run), Path(args.datoteka))
    else:
        st = Path(args.run) / "stanje.json"
        state = jload(st) if st.exists() else {}
        for i, ph in enumerate(PHASES):
            print(f"[{i}] {ph:13s} {state.get(ph, {}).get('zavrseno', '—')}")


if __name__ == "__main__":
    main()
