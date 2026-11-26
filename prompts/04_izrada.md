FAZA 4 – IZRADA SADRŽAJA ZA OBJAVU {broj}

Napiši kompletan sadržaj za jednu objavu prema PLANU. Grafika se slaže automatski iz
predložaka (boje i logo brenda) i SLUŽBENIH fotografija proizvoda, pa ti biraš raspored
svakog kadra i pišeš sav tekst.

OBLIK OBRAĆANJA (obavezno, utvrđeno u analizi brenda):
{oblik_obracanja}
Sav tekst – kadrovi, opis, naljepnice, gumbi – mora biti u tom obliku. Ako je oblik "vi",
piši "spremite", "napišite", "vaš", "vama", malim slovom; nikad "spremi", "tvoj", "ti".

PLAN OVE OBJAVE:
{plan_objave}

ANALIZA BRENDA (ton i stil):
{analiza}

IZVORI ZA PROIZVODE IZ OVE OBJAVE (jedine dopuštene činjenice):
{izvori}

DOSTUPNE FOTOGRAFIJE (id proizvoda → indeks → opis):
{slike}

DOSTUPNI RASPOREDI KADRA ("layout"):
- "naslovna": nadnaslov, naslov, podnaslov, proizvod (opcionalno), oznaka (opcionalno)
- "brojka": nadnaslov, brojka {{"vrijednost": "22 g", "opis": "..."}}, tekst, proizvod (opcionalno)
- "lista": nadnaslov, naslov, stavke [{{"naslov": "...", "tekst": "..."}}] (2–4 stavke)
- "proizvod": nadnaslov, naslov, tekst, proizvod, cinjenice ["kratko", ...] (do 3), oznaka (opcionalno)
- "anketa": nadnaslov, naslov, opcije [{{"oznaka": "A", "naziv": "...", "proizvod": {{...}}}}, {{"oznaka": "B", ...}}], tekst
- "tekst": nadnaslov, naslov, tekst
- "cta": nadnaslov, naslov, tekst, gumb, proizvod (opcionalno)
Polje "proizvod" ima oblik {{"id": "<id proizvoda>", "slika": <indeks fotografije>}}.
Polje "tema" je "tamna", "svijetla" ili "narancasta" – izmjenjuj ih s mjerom (brend: crna,
bijela, narančasta #FF4410). U naslovu riječ ili dvije koje treba istaknuti narančastom
okruži zvjezdicama, npr. "Koliko *proteina* trebate?".

Pravila za izbor rasporeda:
- Ako plan uspoređuje dva proizvoda ili traži glasanje ("ovo ili ono", "slano ili slatko"),
  ključni kadar MORA biti "anketa" s oba proizvoda – to vrijedi i za format "slika".
- Nadnaslov mora opisivati baš sadržaj tog kadra (ne naslov cijele objave).
- Fotografiju biraj prema opisu: za "proizvod"/"naslovna" najbolji je čisti packshot.

Pravila za tekst na grafici:
- nadnaslov ≤ 28 znakova, naslov ≤ 48 znakova, podnaslov/tekst ≤ 160 znakova,
  stavka.naslov ≤ 28, stavka.tekst ≤ 90, gumb ≤ 24, oznaka ≤ 24 znaka.
- Jedna poruka po kadru. Prvi kadar mora zaustaviti skrolanje.
- Ne impliciraj učinke na probavu ili zdravlje (npr. "težina u želucu", "lakša probava") ako
  ih izvor doslovno ne navodi – opiši samo što proizvod SADRŽI.
- Cijene piši u hrvatskom formatu ("26,95 €"); hashtagove na hrvatskom standardu (#prehrana).
- Brojke i svojstva samo iz izvora. Cijenu navedi samo ako je u izvorima, uz "{datum_cijena}".
- Za "story": prvi i zadnji kadar imaju jasnu radnju (anketa / "klikni link"); u polju
  "story_naljepnica" predloži interaktivnu naljepnicu (anketa, kviz, link) za taj kadar.
- Prije vraćanja odgovora pročitaj sav tekst još jednom: pravopis (č/ć, dž/đ), padeži, oblik
  obraćanja i prirodnost rečenica.

Opis objave (caption): 400–1200 znakova, prva rečenica je udica, kratki odlomci, jasan
poziv na radnju usklađen s ciljem (npr. "spremite", "napišite u komentar", "link u biou"),
5–10 relevantnih hashtagova (mješavina hrvatskih i brendiranih, npr. #gymbeam).

Vrati JSON:
{{
  "broj": {broj},
  "format": "{format}",
  "kadrovi": [
    {{"layout": "naslovna", "tema": "tamna", "nadnaslov": "...", "naslov": "...", "podnaslov": "...",
      "proizvod": {{"id": "...", "slika": 0}}, "alt_tekst": "opis kadra za čitače zaslona",
      "story_naljepnica": null}}
  ],
  "opis": "caption …",
  "hashtagovi": ["#gymbeam", "..."],
  "koristene_cinjenice": [{{"cinjenica": "...", "izvor": "URL"}}],
  "ai_scena_prompt": "OPCIONALNO: prompt (engleski) za AI pozadinsku scenu BEZ proizvoda i teksta, ako bi poboljšala naslovni kadar; inače null"
}}
{povratna_informacija}
