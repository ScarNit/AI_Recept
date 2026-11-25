"""Sloj za jezične modele.

Načini rada (config.yaml → ``llm``):

* ``providers`` – lanac OpenAI-kompatibilnih pružatelja (Gemini, Groq, OpenRouter …), svaki
  sa svojom varijablom za ključ i listom modela. Recept kruži kroz sve parove
  (pružatelj, model) redom prioriteta: kad je jedan preopterećen (503) ili potroši kvotu
  (429), prelazi na sljedeći. Pružatelj bez postavljenog ključa se preskače.
* ``provider: manual`` – bez API ključa: prompt se zapisuje u datoteku, korisnik ga
  zalijepi u ChatGPT / Gemini / Claude chat i odgovor spremi u pripremljenu datoteku;
  ponovno pokretanje iste faze nastavlja dalje.
* (kompatibilnost) ``provider: gemini`` ili ``provider: openai`` + ``models``.

Svi pozivi vraćaju čisti tekst; ``chat_json`` dodatno parsira JSON odgovor.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import sys
import time
from pathlib import Path

import requests

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"


class ManualStepRequired(Exception):
    """Ručni način rada: prompt je zapisan, čeka se odgovor korisnika."""


def _targets(cfg: dict) -> list[dict]:
    """Lista (pružatelj, model) parova redom prioriteta."""
    providers = cfg.get("providers")
    if not providers:  # stari oblik konfiguracije
        prov = cfg.get("provider", "gemini")
        providers = [{
            "name": prov,
            "base_url": GEMINI_BASE if prov == "gemini" else os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "key_env": "GEMINI_API_KEY" if prov == "gemini" else "OPENAI_API_KEY",
            "models": cfg.get("models") or ["gemini-3.5-flash"],
        }]
    out = []
    for p in providers:
        key = os.environ.get(p.get("key_env", ""), "")
        if not key:
            continue
        for m in p.get("models", []):
            m = m if isinstance(m, dict) else {"id": m}
            out.append({"provider": p["name"], "base_url": p["base_url"].rstrip("/"), "key": key,
                        "model": m["id"], "vision": m.get("vision", p.get("vision", True)),
                        "extra_headers": p.get("headers", {})})
    return out


class LLM:
    def __init__(self, cfg: dict, run_dir: Path):
        self.cfg = cfg or {}
        self.provider = self.cfg.get("provider", "chain" if self.cfg.get("providers") else "gemini")
        self.temperature = self.cfg.get("temperature", 0.7)
        self.max_retries = int(self.cfg.get("max_retries", 6))
        self.timeout = int(self.cfg.get("timeout_s", 240))
        self.run_dir = run_dir
        self.log_path = run_dir / "llm_log.jsonl"
        self.targets = [] if self.provider == "manual" else _targets(self.cfg)
        if self.provider != "manual" and not self.targets:
            envs = [p.get("key_env") for p in self.cfg.get("providers", [])] or ["GEMINI_API_KEY"]
            sys.exit("Nijedan pružatelj nema API ključ. Postavi barem jednu od varijabli: "
                     + ", ".join(envs) + " (vidi .env.example) ili u config.yaml stavi llm.provider: manual.")

    # ------------------------------------------------------------------ javno
    def chat(self, system: str, user: str, *, step: str, images: list[Path] | None = None,
             json_mode: bool = False) -> str:
        if self.provider == "manual":
            return self._manual(system, user, step=step, images=images)
        return self._api(system, user, step=step, images=images, json_mode=json_mode)

    def chat_json(self, system: str, user: str, *, step: str, images: list[Path] | None = None):
        last_err = None
        for attempt in range(3):
            extra = "" if attempt == 0 else (
                "\n\nPRETHODNI ODGOVOR NIJE BIO ISPRAVAN JSON (" + str(last_err)[:200] +
                "). Vrati ISKLJUČIVO valjani JSON, bez markdowna i komentara.")
            text = self.chat(system, user + extra, step=step if attempt == 0 else f"{step}_retry{attempt}",
                             images=images, json_mode=True)
            try:
                return parse_json(text)
            except ValueError as e:
                last_err = e
                if self.provider == "manual":
                    raise SystemExit(f"Odgovor u ručnom koraku '{step}' nije valjani JSON: {e}")
        raise RuntimeError(f"Model nije vratio valjani JSON za korak {step}: {last_err}")

    # ------------------------------------------------------------- API poziv
    def _api(self, system, user, *, step, images, json_mode):
        content: list | str = user
        if images:
            content = [{"type": "text", "text": user}]
            for img in images:
                content.append({"type": "image_url", "image_url": {"url": _data_uri(img)}})
        messages = [{"role": "system", "content": system}, {"role": "user", "content": content}]

        # Besplatni modeli su povremeno preopterećeni (HTTP 503/429). Umjesto dugog čekanja
        # na jedan model, kružimo kroz sve (pružatelj, model) parove u nekoliko krugova;
        # prvi u listi je preferirani (najkvalitetniji).
        candidates = [t for t in self.targets if t["vision"] or not images]
        if not candidates:
            raise RuntimeError("Nijedan konfigurirani model ne prima slike, a korak ih treba.")
        errors, dead = [], set()
        for rnd in range(self.max_retries):
            for t in candidates:
                tid = f"{t['provider']}/{t['model']}"
                if tid in dead:
                    continue
                body = {"model": t["model"], "messages": messages, "temperature": self.temperature}
                if json_mode:
                    body["response_format"] = {"type": "json_object"}
                t0 = time.time()
                try:
                    r = requests.post(f"{t['base_url']}/chat/completions",
                                      headers={"Authorization": f"Bearer {t['key']}",
                                               "Content-Type": "application/json", **t["extra_headers"]},
                                      json=body, timeout=self.timeout)
                except requests.RequestException as e:
                    errors.append(f"{tid}: {e}")
                    continue
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list):
                        data = data[0]
                    text = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
                    if text.strip():
                        self._log(step, tid, time.time() - t0, system, user, text, images)
                        print(f"    ({tid}, {time.time() - t0:.0f} s)")
                        return text
                    errors.append(f"{tid}: prazan odgovor")
                    continue
                msg = _err_msg(r)
                errors.append(f"{tid} HTTP {r.status_code}: {msg[:160]}")
                print(f"  ! {tid} HTTP {r.status_code}: {msg[:70]}{msg[msg.find(' [kvota'):] if ' [kvota' in msg else ''}",
                      file=sys.stderr)
                low = msg.lower()
                if r.status_code in (400, 401, 403, 404, 413) or (
                        r.status_code == 429 and ("per day" in low or "perday" in low or "daily" in low)):
                    dead.add(tid)  # model nedostupan, ne prima zahtjev ili je dnevna kvota potrošena
            if len(dead) == len(candidates):
                break
            time.sleep(min(60, 10 * (rnd + 1)))
        raise RuntimeError("Svi modeli su odbili zahtjev:\n  " + "\n  ".join(errors[-8:]))

    # ------------------------------------------------------------ ručni način
    def _manual(self, system, user, *, step, images):
        mdir = self.run_dir / "rucno"
        mdir.mkdir(parents=True, exist_ok=True)
        prompt_f = mdir / f"{step}_PROMPT.md"
        answer_f = mdir / f"{step}_ODGOVOR.md"
        if answer_f.exists() and answer_f.read_text(encoding="utf-8").strip():
            text = answer_f.read_text(encoding="utf-8")
            self._log(step, "manual", 0, system, user, text, images)
            return text
        img_note = ""
        if images:
            img_note = "\n\n## Priloži ove slike u chat\n" + "\n".join(f"- {p}" for p in images)
        prompt_f.write_text(f"# SUSTAVSKE UPUTE\n\n{system}\n\n# ZADATAK\n\n{user}{img_note}\n",
                            encoding="utf-8")
        answer_f.touch()
        raise ManualStepRequired(
            f"Ručni korak '{step}':\n  1) otvori {prompt_f}\n  2) cijeli sadržaj zalijepi u ChatGPT/Gemini/Claude"
            f"{' i priloži navedene slike' if images else ''}\n  3) odgovor spremi u {answer_f}\n"
            "  4) ponovno pokreni istu naredbu – rad se nastavlja.")

    def _log(self, step, model, secs, system, user, text, images):
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "step": step, "model": model,
                "seconds": round(secs, 1), "images": [str(p) for p in images or []],
                "system": system, "user": user, "response": text}, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ pomoćno
def parse_json(text: str):
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    start = min([i for i in (t.find("{"), t.find("[")) if i >= 0], default=-1)
    end = max(t.rfind("}"), t.rfind("]"))
    if start >= 0 and end > start:
        try:
            return json.loads(t[start:end + 1])
        except json.JSONDecodeError as e:
            raise ValueError(str(e)) from e
    raise ValueError("u odgovoru nema JSON objekta")


def _data_uri(path: Path, max_side: int = 1280) -> str:
    """Slika kao data URI; velike slike smanjuju se na max_side px (JPEG) da bi zahtjev
    stao u besplatnu minutnu kvotu ulaznih tokena."""
    import io

    from PIL import Image
    im = Image.open(path)
    if max(im.size) <= max_side and Path(path).stat().st_size < 600_000:
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()
    im = im.convert("RGB")
    im.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _err_msg(r: requests.Response) -> str:
    try:
        d = r.json()
        if isinstance(d, list):
            d = d[0]
        err = d.get("error", {})
        quotas = [v.get("quotaId", "") for x in err.get("details", []) for v in x.get("violations", [])]
        return err.get("message", r.text) + (f" [kvota: {', '.join(quotas)}]" if quotas else "")
    except Exception:
        return r.text
