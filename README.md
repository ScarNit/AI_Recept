# AI recept: od Instagram brenda do tri gotove objave

Ponovljivi, fazni AI recept koji iz brifa i službenog webshopa brenda izrađuje **tri gotove
Instagram objave** (slike + tekstovi). Demonstracija: **GymBeam Hrvatska –
[@gymbeamhr](https://www.instagram.com/gymbeamhr/)**.

- 📦 **Gotove objave:** [`runs/gymbeam_hr/isporuka/`](runs/gymbeam_hr/isporuka/README.md)
- 📄 **Upute i osvrt (PDF):** [`docs/upute_i_osvrt.pdf`](docs/upute_i_osvrt.pdf)
- 🧾 **Ulazi (brif):** [`brief/gymbeam_hr.yaml`](brief/gymbeam_hr.yaml)
- 🧠 **Promptovi:** [`prompts/`](prompts/)
- 🔍 **Međurezultati:** [analiza](runs/gymbeam_hr/03_analiza.md) · [plan](runs/gymbeam_hr/04_plan.md) ·
  [sadržaj](runs/gymbeam_hr/05_sadrzaj.json) · [provjera](runs/gymbeam_hr/07_provjera.md)

## Brzi start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium            # preglednik za render slika

export GEMINI_API_KEY=...               # besplatno: https://aistudio.google.com/apikey
python -m recept pokreni --brif brief/gymbeam_hr.yaml --run runs/moj_test
```

Rezultat je u `runs/moj_test/isporuka/` (PNG kadrovi, `opis.txt`, `README.md` s pregledom).

**Bez API ključa** (samo ChatGPT/Gemini/Claude chat pretplata): u `config.yaml` postavi
`llm.provider: manual`. Recept za svaki AI korak zapiše prompt u `runs/<run>/rucno/*_PROMPT.md`,
ti ga zalijepiš u chat (uz navedene slike), odgovor spremiš u `*_ODGOVOR.md` i ponovno
pokreneš istu naredbu – rad se nastavlja od tog koraka.

**Novi brend:** `python -m recept brif --izlaz brief/moj_brend.yaml` (interaktivni brifing:
web-stranica, proizvodi, publika, ciljevi, uzori, snimke Instagrama), zatim `pokreni`.

## Faze

| # | Faza | Ulaz | Što radi | Izlaz |
|---|------|------|----------|-------|
| 0 | `brif` | YAML / interaktivni brifing | ulazi korisnika: brend, web, proizvodi, publika, ciljevi, ton, ograničenja, snimke IG | `00_brif.json` |
| 1 | `istrazivanje` | brif | čita schema.org podatke i opise s webshopa, skida službene fotografije i logo | `01_izvori.json`, `assets/` |
| 2 | `opis_slika` | fotografije | AI (vision) opisuje svaku fotografiju da bi copywriter birao pravu | `02_opis_slika.json` |
| 3 | `analiza` | brif, izvori, snimke IG | ton, publika, teme, vizualni stil; **provjereno (s URL-om) odvojeno od pretpostavki** | `03_analiza.json/.md` |
| 4 | `plan` | analiza, izvori | tri objave: cilj, mjera uspjeha, format, koncept, činjenice, obrazloženje | `04_plan.json/.md` |
| 5 | `izrada` | plan, izvori, opisi slika | tekst svakog kadra (raspored, naslovi, brojke), caption, hashtagovi, alt tekst | `05_sadrzaj.json` |
| 6 | `render` | sadržaj, fotografije | HTML predložak u bojama brenda + originalne fotografije → PNG; mjeri prelijevanje teksta | `isporuka/objava_N/*.png` |
| 7 | `provjera` | PNG + sadržaj + izvori | deterministički: brojke bez izvora, duljine, prelijevanje; AI kritičar gleda slike i ocjenjuje; ispravci se primjenjuju i ponovno renderira | `07_provjera.json/.md` |
| 8 | `isporuka` | sve | `opis.txt`, pregled kadrova, README s ciljem, formatom i izvorima | `isporuka/` |

Svaka faza sprema rezultat; ponovno pokretanje preskače gotove faze (nastavak nakon prekida).
Korisne opcije:

```bash
python -m recept pokreni --run runs/x --do plan          # stani nakon plana → čovjek pregleda/uredi 04_plan.json
python -m recept pokreni --run runs/x --od izrada        # nastavi od izrade
python -m recept pokreni --run runs/x --od izrada --objave 2   # ponovi samo objavu 2
python -m recept stanje --run runs/x
```

**Opcionalne AI scene:** ako u `runs/<run>/ai_slike/` staviš sliku `objava1_kadar1.png`
(npr. generiranu u ChatGPT-u ili Geminiju prema `ai_scena_prompt` iz `05_sadrzaj.json`),
render je koristi kao pozadinu tog kadra; proizvod i logo i dalje dolaze iz originalnih datoteka.

## Struktura

```
brief/            ulazi (brif) za demonstraciju
prompts/          svi promptovi po fazama (sustav + 5 faza)
recept/           kod: cli.py (faze), llm.py, scrape.py, render.py, provjera.py, templates/, fonts/
runs/gymbeam_hr/  stvarno pokretanje: međurezultati, fotografije, gotove objave (isporuka/)
docs/             PDF s uputama i osvrtom
```

Alati: Python 3.11+, Google Gemini API (besplatni sloj, OpenAI-kompatibilni endpoint),
Playwright/Chromium za render, Inter font (OFL). Ključevi se ne spremaju u repozitorij
(`.env.example`, `config.example.yaml`).
