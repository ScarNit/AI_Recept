"""Sloj za jezične modele.

Podržana su tri načina rada (``llm.provider`` u config.yaml):

* ``gemini``  – Google Gemini preko OpenAI-kompatibilnog endpointa
                (besplatni API ključ iz Google AI Studija, varijabla GEMINI_API_KEY).
* ``openai``  – bilo koji OpenAI-kompatibilni endpoint (OpenAI, OpenRouter, lokalni
                server …), varijable OPENAI_API_KEY i po želji OPENAI_BASE_URL.
* ``manual``  – bez API ključa: prompt se zapisuje u datoteku, korisnik ga zalijepi u
                ChatGPT / Gemini / Claude chat i odgovor spremi u pripremljenu
                datoteku; ponovno pokretanje iste faze nastavlja dalje.

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


class LLM:
    def __init__(self, cfg: dict, run_dir: Path):
        self.cfg = cfg or {}
        self.provider = self.cfg.get("provider", "gemini")
        self.models = self.cfg.get("models") or ["gemini-3.5-flash"]
        self.temperature = self.cfg.get("temperature", 0.7)
        self.max_retries = int(self.cfg.get("max_retries", 6))
        self.timeout = int(self.cfg.get("timeout_s", 240))
        self.run_dir = run_dir
        self.log_path = run_dir / "llm_log.jsonl"

        if self.provider == "gemini":
            self.base_url = GEMINI_BASE
            self.api_key = os.environ.get("GEMINI_API_KEY", "")
        elif self.provider == "openai":
            self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
            self.api_key = os.environ.get("OPENAI_API_KEY", "")
        elif self.provider == "manual":
            self.base_url = self.api_key = ""
        else:
            raise ValueError(f"Nepoznat llm.provider: {self.provider}")

        if self.provider != "manual" and not self.api_key:
            sys.exit(
                f"Nedostaje API ključ za provider '{self.provider}'. Postavi "
                f"{'GEMINI_API_KEY' if self.provider == 'gemini' else 'OPENAI_API_KEY'} "
                "(vidi .env.example) ili u config.yaml stavi llm.provider: manual."
            )

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
        body = {
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": content}],
            "temperature": self.temperature,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        # Besplatni modeli su povremeno preopterećeni (HTTP 503/429). Umjesto dugog
        # čekanja na jedan model, kružimo kroz listu modela u nekoliko krugova;
        # prvi model u listi je preferirani (najkvalitetniji).
        errors, dead = [], set()
        for rnd in range(self.max_retries):
            for model in self.models:
                if model in dead:
                    continue
                body["model"] = model
                t0 = time.time()
                try:
                    r = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers={"Authorization": f"Bearer {self.api_key}",
                                 "Content-Type": "application/json"},
                        json=body, timeout=self.timeout)
                except requests.RequestException as e:
                    errors.append(f"{model}: {e}")
                    continue
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list):
                        data = data[0]
                    text = data["choices"][0]["message"].get("content") or ""
                    if text.strip():
                        self._log(step, model, time.time() - t0, system, user, text, images)
                        print(f"    ({model}, {time.time() - t0:.0f} s)")
                        return text
                    errors.append(f"{model}: prazan odgovor")
                    continue
                msg = _err_msg(r)
                errors.append(f"{model} HTTP {r.status_code}: {msg[:160]}")
                print(f"  ! {model} HTTP {r.status_code}: {msg[:100]}", file=sys.stderr)
                if r.status_code in (400, 401, 403, 404) or (r.status_code == 429 and "per day" in msg.lower()):
                    dead.add(model)  # model nedostupan ili dnevna kvota potrošena
            if len(dead) == len(self.models):
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


def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def _err_msg(r: requests.Response) -> str:
    try:
        d = r.json()
        if isinstance(d, list):
            d = d[0]
        return d.get("error", {}).get("message", r.text)
    except Exception:
        return r.text
