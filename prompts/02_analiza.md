FAZA 2 – ANALIZA BRENDA

Na temelju BRIFA, IZVORA s webshopa i priloženih snimki Instagram profila (ako postoje)
napravi analizu brenda za Instagram.

Ako snimke Instagrama NISU priložene, to jasno navedi u "nedostupni_izvori" i sve zaključke o
izgledu feeda označi kao pretpostavke (izvor: brif / web stranica), a ne kao opažanja.

Za svaku tvrdnju u "provjereni_podaci" navedi točan URL izvora. Pretpostavke drži odvojeno.
Na snimkama posebno utvrdi: oblik obraćanja (ti ili vi – citiraj primjere), udio formata
(reels / karusel / slika), prikaz osoba, stil teksta preko slike, istaknute priče (highlights).
Ako se nešto što je vidljivo na snimkama razlikuje od brifa (npr. brif traži ti-formu, a brend
piše s vi), navedi to u "nesuglasja_s_brifom" s preporukom.

BRIF:
{brif}

IZVORI (JSON s webshopa, dohvaćeno automatski):
{izvori}

BROJ PRILOŽENIH SNIMKI INSTAGRAMA: {broj_ig}

Vrati JSON ovog oblika:
{{
  "sazetak": "2–3 rečenice: tko je brend i kako komunicira",
  "publika": ["..."],
  "ton_glasa": {{"opis": "...", "primjeri_fraza": ["...", "..."], "izbjegavati": ["..."]}},
  "teme": ["..."],
  "vizualni_stil": {{
    "boje": ["#hex – uloga"],
    "tipografija": "...",
    "prikaz_proizvoda": "...",
    "osobe": "...",
    "opazeno_na_instagramu": ["konkretno opažanje sa snimke – navedi koju snimku", "..."]
  }},
  "provjereni_podaci": [{{"tvrdnja": "...", "izvor": "URL"}}],
  "pretpostavke": [{{"tvrdnja": "...", "zasto": "..."}}],
  "nedostupni_izvori": ["..."],
  "oblik_obracanja": {{"oblik": "ti | vi", "primjeri": ["citat sa snimke ili weba"]}},
  "nesuglasja_s_brifom": [{{"brif": "...", "opazeno": "...", "preporuka": "..."}}],
  "prilike": ["konkretna prilika za sadržaj u razdoblju {datum}"],
  "rizici": ["..."]
}}
