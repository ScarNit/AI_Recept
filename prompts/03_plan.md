FAZA 3 – PLAN TRIJU OBJAVA

Osmisli TRI Instagram objave za brend. Svaka objava ima drugačiji glavni cilj iz brifa
(npr. edukacija/spremanja, komentari/interakcija, interes za kupnju). Format biraš sam:
"karusel" (4–7 slajdova, 1080×1350), "slika" (1 slajd, 1080×1350) ili
"story" (povezani niz 3–5 kadrova, 1080×1920).

Pravila:
- Koristi samo proizvode iz IZVORA (polje "id"). Svaka objava mora imati barem jedan proizvod.
- Koncept mora biti izvediv iz službenih fotografija ambalaže + grafike (tekst, brojke, boje
  brenda). Ne planiraj fotografije osoba ni scene koje traže nove fotografije.
- Svaka činjenica koju planiraš istaknuti mora postojati u izvorima – navedi koju.
- Uzmi u obzir sezonu: {datum}.

BRIF:
{brif}

ANALIZA BRENDA:
{analiza}

DOSTUPNI PROIZVODI (id → naziv, ključne činjenice):
{proizvodi}

Vrati JSON:
{{
  "objave": [
    {{
      "broj": 1,
      "naziv": "kratki radni naziv",
      "cilj": "...",
      "mjera_uspjeha": "npr. spremanja i dijeljenja",
      "format": "karusel | slika | story",
      "broj_kadrova": 6,
      "koncept": "2–3 rečenice",
      "proizvodi": ["id"],
      "kljucne_cinjenice": [{{"cinjenica": "...", "izvor": "URL"}}],
      "obrazlozenje": "zašto ovo odgovara brendu i publici (2–3 rečenice)"
    }}
  ]
}}
